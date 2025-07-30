import os
import secrets

from flask import jsonify, request, Blueprint

from forgen.ddb.user import save_user_registry_to_ddb
from forgen.service.service import require_master_key
from forgen.user.user import USER_REGISTRIES, UserRegistry


user_endpoint = Blueprint("user", __name__)


@user_endpoint.route("/admin/create_user", methods=["POST"])
@require_master_key
def create_user():
    if request.headers.get("X-ADMIN-KEY") != os.getenv("ADMIN_KEY", "adminsecret"):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    display_name = data.get("name")
    wallet = data.get("wallet")
    email = data.get("email")
    verified = False
    user_id = wallet or secrets.token_hex(16)  # Use wallet as user_id if present

    if email:
        domain = email.split("@")[-1]
        verified = domain not in ["gmail.com", "yahoo.com"]
    else:
        domain = None

    user_reg_item = UserRegistry(
        user_id=user_id,
        display_name=display_name,
        wallet=wallet,
        email=email,
        domain=domain,
        verified=verified
    )
    USER_REGISTRIES[user_id] = user_reg_item
    save_user_registry_to_ddb(user_reg_item)

    return jsonify({
        "user": display_name,
        "user_id": user_id,
        "wallet": wallet,
        "email": email,
        "verified": verified
    })
