import os
import time

import boto3
import requests
from jose import JWTError, jwt

from forgen.util.general import calculate_secret_hash
from cachetools import cached, TTLCache


AWS_REGION = "us-east-2"
COGNITO_USERPOOL_ID = "us-east-2_5Bsq5jr9r"
COGNITO_DOMAIN = "https://patdown.auth.us-east-2.amazoncognito.com"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("COGNITO_APP_CLIENT_SECRET")

COGNITO_ISSUER = "https://cognito-idp." + AWS_REGION + ".amazonaws.com/" + COGNITO_USERPOOL_ID

client = boto3.client("cognito-idp", region_name=AWS_REGION)




cache = TTLCache(maxsize=1, ttl=3600)

@cached(cache)
def get_jwks():
    jwks_url = COGNITO_ISSUER + '/.well-known/jwks.json'
    response = requests.get(jwks_url)
    response.raise_for_status()
    return response.json()


def confirm_signup_for_user(username, confirmation_code):
    try:
        client.confirm_sign_up(
          ClientId=CLIENT_ID,
          Username=username,
          ConfirmationCode=confirmation_code,
          SecretHash=calculate_secret_hash(CLIENT_ID, CLIENT_SECRET, username),
        )
        return "success", 200
    except Exception as e:
      return f"error confirming sign up for user: {username}, and code: {confirmation_code}", 500


def change_user_password(access_token, previous_password, proposed_password):
    try:
        response = client.change_password(
            PreviousPassword=previous_password,
            ProposedPassword=proposed_password,
            AccessToken=access_token
        )
        return "Password change successful", 200
    except client.exceptions.NotAuthorizedException:
        return "Not authorized to change password", 401
    except client.exceptions.LimitExceededException:
        return "Limit exceeded, please try again later", 429
    except Exception as e:
        return f"Error changing password: {str(e)}", 500


def initiate_forgot_password(username):
    try:
        response = client.forgot_password(
            ClientId=CLIENT_ID,
            Username=username,
            SecretHash=calculate_secret_hash(CLIENT_ID, CLIENT_SECRET, username),
        )
        # If the call succeeds, return a success message
        return {"message": "Password reset initiated. Check your email or SMS for the verification code. If you do not receive a code, please contact us at support@forgen.ai."}, 200
    except client.exceptions.UserNotFoundException:
        # Handle specific exceptions such as user not found
        return "User not found", 404
    except client.exceptions.LimitExceededException:
        # Handle limit exceeded exception
        return "Limit exceeded, please try again later", 429
    except client.exceptions.NotAuthorizedException:
        # Handle not authorized exception
        return "Not authorized to start forgot password process", 401
    except Exception as e:
        # For any other exceptions, return a generic error message
        return f"Error initiating forgot password process: {str(e)}", 500


def confirm_forgot_password(username, verification_code, new_password):
    try:
        response = client.confirm_forgot_password(
            ClientId=CLIENT_ID,
            Username=username,
            ConfirmationCode=verification_code,
            Password=new_password,
            SecretHash=calculate_secret_hash(CLIENT_ID, CLIENT_SECRET, username),
        )
        return {"message": "Password reset successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400


def resend_code_for_user(username):
    try:
        client.resend_confirmation_code(
          ClientId=CLIENT_ID,
          Username=username,
          SecretHash=calculate_secret_hash(CLIENT_ID, CLIENT_SECRET, username),
        )
        return "success", 200
    except Exception as e:
      return f"error resending code for user: {username}", 500


def get_username_from_token(id_token):
    try:
        decoded_token = jwt.decode(id_token, key='', options={"verify_signature": False})
        return decoded_token.get("cognito:username") or decoded_token.get("username") or decoded_token.get("sub")
    except Exception as e:
        app_logger.warning(f"Failed to decode token or extract username: {str(e)}")
        return None


def is_token_valid(token):
  try:
    unverified_header = jwt.get_unverified_header(token)
    jwks = get_jwks()
    rsa_key = {}
    for key in jwks['keys']:
      if key['kid'] == unverified_header['kid']:
        rsa_key = {
          'kty': key['kty'],
          'kid': key['kid'],
          'use': key['use'],
          'n': key['n'],
          'e': key['e']
        }
    payload = jwt.decode(
      token,
      rsa_key,
      algorithms=['RS256'],
      audience=CLIENT_ID,
      issuer=COGNITO_ISSUER
    )
    return payload
  except Exception as e:
    # app_logger.info(f"error: {str(e)}")
    return False


def get_token_param(token, param_name):
  return is_token_valid(token).get(param_name)


def check_id_token_and_get_username(id_token):
    if not id_token:
        return False
    valid_token = is_token_valid(id_token)
    if not valid_token:
        return False
    username = valid_token.get("cognito:username", "").lower()
    return username


def validate_and_refresh_id_token(id_token, refresh_token):
    token_payload = is_token_valid(id_token)
    if token_payload and token_payload.get("exp", 0) >= time.time() + 300:
        return {"id_token": id_token, "username": check_id_token_and_get_username(id_token)}

    if not refresh_token:
        return {"error": "Token expired and no refresh token provided."}

    username = check_id_token_and_get_username(id_token)
    if not username:
        return {"error": "Invalid token: username missing or malformed"}

    refreshed_tokens = _refresh_tokens_logic(refresh_token, username)
    if not isinstance(refreshed_tokens, dict) or "id_token" not in refreshed_tokens:
        return {"error": "Token refresh failed"}

    return {
        "id_token": refreshed_tokens["id_token"],
        "username": username
    }


def _refresh_tokens_logic(refresh_token, username):
    try:
        resp = client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token,
                'SECRET_HASH': calculate_secret_hash(CLIENT_ID, CLIENT_SECRET, username),
            }
        )
        authentication_result = resp.get('AuthenticationResult')
        if not authentication_result:
            raise ValueError("Authentication failed")

        return {
            "id_token": authentication_result.get('IdToken'),
            "access_token": authentication_result.get('AccessToken'),
            "refresh_token": refresh_token,
            "username": username
        }
    except Exception as e:
        return {"error": "Token refresh failed"}
    