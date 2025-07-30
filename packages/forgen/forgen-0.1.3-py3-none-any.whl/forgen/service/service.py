import logging
import os
from functools import wraps

from flask_cors import CORS
from flask import Flask, jsonify, request

from forgen.service.amcp import amcp_endpoint
from forgen.user.user import USER_REGISTRIES

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["https://test.forgen.ai"])
app.register_blueprint(amcp_endpoint, url_prefix="/amcp")
current_thread = None
admins = os.environ.get("ADMIN_USERS", str(["jimmy", "rpinnama", "jim"])).split(",")
MASTER_API_KEY = os.getenv("FORGEN_API_KEY", "supersecret")
PUBLIC_ENDPOINTS = {"healthcheck"}


def require_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")
        if not api_key or api_key not in USER_REGISTRIES:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


def require_master_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get("X-API-KEY") != MASTER_API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def healthcheck():
    return "Here I am!"


def initialize_logging(app):
    app.logger.setLevel(logging.INFO)
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)


if __name__ != "__main__":
    initialize_logging(app)
