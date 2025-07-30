import json
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Dict, Any
from forgen.tool.module import BaseModule
from forgen.registry.registered_module import RegisteredModule


def export_amcp_registry(modules: List[BaseModule], path="amcp_registry.json"):
    specs = [m.to_amcp_spec() for m in modules]
    with open(path, "w") as f:
        json.dump(specs, f, indent=2)


def load_amcp_registry(path="amcp_registry.json") -> List[dict]:
    with open(path, "r") as f:
        return json.load(f)


@dataclass
class AMCPComponent:
    id: str
    name: str
    domain: Optional[str] = None
    role: Optional[str] = None
    context: Optional[str] = None
    modules: List[RegisteredModule] = field(default_factory=list)
    strategy_function: Optional[
        Callable[[Dict[str, Any], Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
    ] = None

    def serialize(self) -> dict:
        return {
            "type": "AMCPComponent",
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "role": self.role,
            "context": self.context,
            "modules": [m.serialize() for m in self.modules],
            # strategy_function is not serializable directly
        }

    @staticmethod
    def deserialize(spec: dict) -> "AMCPComponent":
        modules = [RegisteredModule.deserialize(m) for m in spec.get("modules", [])]
        return AMCPComponent(
            id=spec.get("id"),
            name=spec.get("name"),
            domain=spec.get("domain"),
            role=spec.get("role"),
            context=spec.get("context"),
            modules=modules
        )

    def execute(self, user_request: Dict[str, Any]) -> Dict[str, Any]:
        if not self.strategy_function:
            raise ValueError("No strategy function defined for AMCPComponent.")

        # Call strategy function
        context_info = {
            "domain": self.domain,
            "role": self.role,
            "context": self.context
        }

        plan = self.strategy_function(user_request, context_info, {})
        output = {}

        for step in plan.get("steps", []):
            tool_name = step["tool_name"]
            input_data = step.get("input", {})

            tool = next((m.module for m in self.modules if m.name == tool_name), None)
            if tool is None:
                raise ValueError(f"Tool '{tool_name}' not found in AMCPComponent '{self.name}'")

            output = tool.execute(input_data)

        return output
