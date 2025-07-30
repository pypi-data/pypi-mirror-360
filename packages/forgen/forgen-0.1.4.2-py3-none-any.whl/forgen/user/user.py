from dataclasses import dataclass, field
from typing import Dict, Optional

from forgen.registry.amcp import AMCPComponent
from forgen.registry.registered_module import RegisteredModule


@dataclass
class UserRegistry:
    user_id: str
    display_name: Optional[str] = ""
    wallet: Optional[str] = None
    email: Optional[str] = None
    domain: Optional[str] = None
    verified: bool = False
    domains: Dict[str, AMCPComponent] = field(default_factory=dict)

    def create_domain(self, domain_id: str, name: str, role: str = "", context: str = ""):
        self.domains[domain_id] = AMCPComponent(
            id=domain_id, name=name, role=role, context=context, modules=[]
        )

    def add_module_to_domain(self, domain_id: str, module: RegisteredModule):
        if domain_id not in self.domains:
            raise ValueError(f"Domain '{domain_id}' not found for user '{self.user_id}'")
        self.domains[domain_id].modules.append(module)


USER_REGISTRIES: Dict[str, UserRegistry] = {
    "secret_key111": UserRegistry(user_id="jimmy"),
    "g3nbl0k": UserRegistry(user_id="ravi"),
}


def get_user_from_request(req) -> UserRegistry:
    api_key = req.headers.get("X-API-KEY")
    if not api_key:
        raise ValueError("Missing API key or wallet")
    if api_key not in USER_REGISTRIES:
        raise ValueError("Invalid API key or wallet")
    return USER_REGISTRIES[api_key]
