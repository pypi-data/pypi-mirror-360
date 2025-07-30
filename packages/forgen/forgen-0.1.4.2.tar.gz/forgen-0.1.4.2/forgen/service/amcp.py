import json
import os

from flask import jsonify, request, Blueprint

from forgen.registry.amcp import AMCPComponent
from forgen.registry.deserialize import deserialize_operand
from forgen.registry.registered_module import RegisteredModule
from forgen.service.service import require_key
from forgen.user.user import get_user_from_request


def load_amcp_registry(path="amcp_registry.json") -> list[AMCPComponent]:
    with open(path, "r") as f:
        data = json.load(f)
    return [AMCPComponent.deserialize(item) for item in data]



API_KEY = os.getenv("FORGEN_API_KEY", "supersecret")
amcp_endpoint = Blueprint("amcp", __name__)
registry: list[AMCPComponent] = load_amcp_registry()


@amcp_endpoint.before_request
def verify_key():
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401


@require_key
@amcp_endpoint.route("/registry", methods=["GET"])
def list_amcp_registry():
    """Return the full AMCP registry."""
    return jsonify([component.serialize() for component in registry])


@require_key
@amcp_endpoint.route("/execute", methods=["POST"])
def execute_registered_module():
    """
    Execute a registered module.
    Expects JSON payload:
    {
        "component_id": "...",
        "module_id": "...",
        "input_data": {...}
    }
    """
    data = request.get_json()
    component_id = data.get("component_id")
    module_id = data.get("module_id")
    input_data = data.get("input_data", {})

    for component in registry:
        if component.id == component_id:
            for mod in component.modules:
                if mod.id == module_id:
                    try:
                        result = mod.module.execute(input_data)
                        return jsonify({"output": result})
                    except Exception as e:
                        return jsonify({"error": str(e)}), 500
            return jsonify({"error": f"Module '{module_id}' not found in component '{component_id}'"}), 404

    return jsonify({"error": f"Component '{component_id}' not found"}), 404


@amcp_endpoint.route("/domain", methods=["POST"])
@require_key
def create_domain():
    user = get_user_from_request(request)
    data = request.get_json()
    domain_id = data["domain_id"]
    name = data["name"]
    role = data.get("role", "")
    context = data.get("context", "")
    user.create_domain(domain_id, name, role, context)
    return jsonify({"status": "created"})


@amcp_endpoint.route("/module", methods=["POST"])
@require_key
def add_module():
    user = get_user_from_request(request)
    data = request.get_json()

    domain_id = data["domain_id"]
    module_id = data["module_id"]
    module_name = data["name"]
    module_code = data["code"]  # For now assume a serialized executable tool definition
    module_object = deserialize_operand(module_code)  # Must be validated upstream

    registered = RegisteredModule(
        id=module_id,
        name=module_name,
        module=module_object
    )

    user.add_module_to_domain(domain_id, registered)
    return jsonify({"status": "registered"})


@amcp_endpoint.route("/<domain_id>/registry", methods=["GET"])
@require_key
def list_user_domain(domain_id):
    user = get_user_from_request(request)
    domain = user.domains.get(domain_id)
    if not domain:
        return jsonify({"error": "Domain not found"}), 404
    return jsonify(domain.serialize())


@amcp_endpoint.route("/<domain_id>/execute", methods=["POST"])
@require_key
def execute_tool(domain_id):
    user = get_user_from_request(request)
    domain = user.domains.get(domain_id)
    if not domain:
        return jsonify({"error": "Domain not found"}), 404

    data = request.get_json()
    module_id = data["module_id"]
    input_data = data.get("input_data", {})

    module = next((m for m in domain.modules if m.id == module_id), None)
    if not module:
        return jsonify({"error": "Module not found"}), 404

    try:
        result = module.module.execute(input_data)
        return jsonify({"output": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
