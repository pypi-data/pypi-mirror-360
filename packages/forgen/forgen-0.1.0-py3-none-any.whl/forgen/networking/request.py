import inspect
import json
import os
import threading
import uuid

from flask import Response, request
from werkzeug.utils import secure_filename

from forgen.ddb.job import set_job_in_ddb, update_status_by_job_id_in_ddb
from forgen.security.cryption import decrypt_data, encrypt_data
from forgen.util import date
from forgen.util.cache import SimpleCache
from forgen.util.cognito import check_id_token_and_get_username, validate_and_refresh_id_token
from forgen.util.file import hash_file_or_string
from forgen.util.logger import get_logger


_logger = get_logger()

request_cache = SimpleCache()

endpoints_to_have_short_cache = []
endpoints_to_have_no_cache = []


def handle_encrypted_request(service_path, endpoint_name, request_data_keys, processing_fn, check_login=True, check_cache=True, **kwargs):
    full_endpoint_name = f"{service_path}-{endpoint_name}"
    timestamp = date.now()
    request_id = f"{full_endpoint_name}-{timestamp}"
    try:
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(',')[0].strip()
        request_id = f"{client_ip}-{full_endpoint_name}-{timestamp}"
        encrypted_data = request.json.get('data')
        raw_data = decrypt_data(encrypted_data)
        cache_key = None
        if check_cache:
            cache_key = f"{client_ip}-{full_endpoint_name}-{hash_file_or_string(str(raw_data) if raw_data else '')}"
            cached_response = request_cache.get(cache_key)
            if cached_response:
                _logger.info(f"[{request_id}] [{full_endpoint_name}] [CACHE HIT] Returning cached response...")
                return cached_response, 200
        request_data = json.loads(raw_data)
        id_token = "" if not check_login else request_data.get("id_token", "")
        auth_result = None
        username = None
        if check_login and id_token:
            refresh_token = request.cookies.get("refresh_token", "") if check_login else ""
            auth_result = validate_and_refresh_id_token(id_token, refresh_token)
            if "error" in auth_result:
                print(f"[{request_id}] [{full_endpoint_name}] [ID_TOKEN EXPIRED] Token expired and no refresh token provided.")
                return encrypt_data(auth_result), 403
            id_token = auth_result["id_token"]
            request_data["id_token"] = id_token
            username = auth_result.get("username")
        if check_login and not username:
            return encrypt_data({"error": "Invalid token"}), 403
        if "data" in request_data:
            request_data = request_data["data"]
        request_id = f"{username}-{client_ip}-{full_endpoint_name}-{timestamp}"
        extracted_data = {key:request_data.get(key) for key in request_data_keys}
        missing_keys = [key for key in request_data_keys if key not in request_data or request_data.get(key) is None]
        if missing_keys:
            _logger.warning(f"[{full_endpoint_name}] Missing keys in request data: {missing_keys}")
        if not extracted_data:
            extracted_data = request_data
        kwargs.update({key:extracted_data.get(key) for key in request_data_keys})
        kwargs["timestamp"] = timestamp
        try:
            if check_login:
                _logger.info(f"[{request_id}] [{full_endpoint_name}] [IDTOKEN {id_token[-10:]} AUTHORIZED] Processing request...")
            _logger.debug(f"[{request_id}] [{full_endpoint_name}] [PROCESSING] Processing request with data: {extracted_data}...\n")
            sig = inspect.signature(processing_fn)
            accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
            if accepts_kwargs:
                result = processing_fn(extracted_data, username, **kwargs)
            else:
                result = processing_fn(extracted_data, username)
            _logger.debug(f"[{request_id}] [{full_endpoint_name}] [CACHING] Cached response: {str(result)[:20]}")
            cache_timeout = 1 if full_endpoint_name in endpoints_to_have_short_cache else kwargs.get("cache_timeout", 15)
            if isinstance(result, Response) and full_endpoint_name not in endpoints_to_have_no_cache: 
                result_data = result.get_data(as_text=False)
                if cache_key:
                    request_cache.set(cache_key, result_data, ttl_seconds=cache_timeout)
            else:
                result_data = encrypt_data(result)
                if cache_key:
                    request_cache.set(cache_key, result_data, ttl_seconds=cache_timeout)
            _logger.debug(f"[{request_id}] [{full_endpoint_name}] [SUCCESS] Returning result: {str(result)[:20]}")
            return result_data, 200
        except ValueError as e:
            if "has not paid for service" in str(e):
                return encrypt_data({"error":f"[{full_endpoint_name}] User has not paid for service"}), 402
            return None
        except Exception as inner_err:
            _logger.error(f"[{request_id}] [{full_endpoint_name}] [PROCESSING - ERROR] Error in processing_fn ({processing_fn.__name__}): {str(inner_err)}.")
            return encrypt_data({"error":f"[{full_endpoint_name}] Internal processing error: {str(inner_err)}"}), 500
    except Exception as outer_err:
        _logger.error(f"[{request_id}] [{full_endpoint_name}] [PROCESSING - ERROR] Error processing request: {str(outer_err)}.")
        return encrypt_data({"error":f"[{full_endpoint_name}] Failed to handle request: {str(outer_err)}"}), 500


def generic_wrapper(processing_fn, data, username, job_id):
    try:
        fn_params = inspect.signature(processing_fn).parameters
        if 'username' in fn_params:
            result = processing_fn(data, username)
        else:
            result = processing_fn(data)
        status = "complete" if "app_no" not in data else "complete-" + data["app_no"]
        update_status_by_job_id_in_ddb(job_id, status)
        return result
    except Exception as e:
        _logger.error(f"[{job_id}] ERROR: {str(e)}")
        update_status_by_job_id_in_ddb(job_id, "error")
        return "error", 404


def generic_process(data, username, processing_fn, update_job_status_fn=set_job_in_ddb):
    job_id = str(uuid.uuid4())
    update_job_status_fn(job_id, "processing")
    threading.Thread(
        target=generic_wrapper,
        args=(processing_fn, data, username, job_id)
    ).start()
    return ({"job_id": job_id})


def handle_file_download_by_app_no(data, custom_handler_fn, username=None):
    if username is not None:
        return custom_handler_fn(data, username)
    return custom_handler_fn(data)


def generic_process_file_upload(_request, processing_fn):
    def wrapper(_request_form_data, saved_file_path, saved_filename, username, job_id):
        try:
            _logger.info(f"[{job_id}] Starting file upload job")
            result = processing_fn(_request_form_data, saved_file_path, saved_filename, username)
            update_status_by_job_id_in_ddb(job_id, "complete")
            _logger.info(f"[{job_id}] Completed file upload job")
        except Exception as e:
            _logger.error(f"[{job_id}] File upload failed: {str(e)}")
            update_status_by_job_id_in_ddb(job_id, "failed")

    _request_form_data = _request.form.to_dict()
    id_token = _request_form_data.get("idToken", "")
    username = check_id_token_and_get_username(id_token)
    if not username:
        return encrypt_data({"error": "Invalid token"}), 403

    # Save uploaded file to disk
    uploaded_file = _request.files.get('file')
    if not uploaded_file:
        return {"error": "No file uploaded"}, 400
    filename = secure_filename(uploaded_file.filename)
    tmp_path = os.path.join("/tmp", f"{uuid.uuid4()}_{filename}")
    uploaded_file.save(tmp_path)

    job_id = str(uuid.uuid4())
    set_job_in_ddb(job_id, "processing")

    threading.Thread(
        target=wrapper,
        args=(_request_form_data, tmp_path, filename, username, job_id),
        daemon=True
    ).start()

    return {"job_id": job_id}, 200
