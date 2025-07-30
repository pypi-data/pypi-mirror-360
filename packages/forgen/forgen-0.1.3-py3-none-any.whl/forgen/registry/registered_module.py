from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from forgen.ddb.author import verify_author
from forgen.ddb.owner import verify_owner
from forgen.ddb.tooling import log_tool_usage
from forgen.tool.module import BaseModule


@dataclass
class RegisteredModule:
    """
    A wrapped registry-ready module (tool, pipeline, agent, etc.)
    Includes metadata for versioning, tagging, and identification in AMCP or global registries.
    """
    id: str
    name: str
    module: BaseModule
    author_id: Optional[str] = None
    owner_id: Optional[str] = None
    version: str = "0.0.1"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = ""
    execution_mode: Optional[str] = "local"
    require_verification: Optional[bool] = False

    def serialize(self) -> dict:
        return {
            "type": "RegisteredModule",
            "id": self.id,
            "name": self.name,
            "author_id": self.author_id,
            "owner_id": self.owner_id,
            "version": self.version,
            "tags": self.tags,
            "metadata": self.metadata,
            "description": self.description,
            "execution_mode": self.execution_mode,
            "require_verification": self.require_verification,
            "module": self.module.serialize() if self.module else None,
        }

    @staticmethod
    def deserialize(spec: dict) -> "RegisteredModule":
        from forgen.registry.deserialize import deserialize_operand

        module_spec = spec.get("module")
        if not module_spec:
            raise ValueError("Missing module specification during RegisteredModule deserialization")

        module = deserialize_operand(module_spec)
        return RegisteredModule(
            id=spec["id"],
            name=spec["name"],
            author_id=spec.get("author_id"),
            owner_id=spec.get("owner_id"),
            version=spec.get("version", "0.0.1"),
            tags=spec.get("tags", []),
            metadata=spec.get("metadata", {}),
            description=spec.get("description", ""),
            execution_mode=spec.get("execution_mode", "local"),
            require_verification=spec.get("require_verification", False),
            module=module
        )

    def verify_author(self):
        return verify_author(self.author_id)

    def verify_owner(self):
        return verify_owner(self.owner_id)

    def verify_parties(self):
        author_verified = self.verify_author()
        if not author_verified:
            print(
                f"[ WARNING ] RegisteredModule {self.id}, author not verified: {self.author_id[-10:] if self.author_id else 'None'}")
        owner_verified = self.verify_owner()
        if not owner_verified:
            print(
                f"[ WARNING ] RegisteredModule {self.id}, owner not verified: {self.owner_id[-10:] if self.owner_id else 'None'}")
        if self.require_verification and not (author_verified and owner_verified):
            raise Exception(
                f"RegisteredModule {self.id} requires verified author and owner. "
                f"author_verified={author_verified}, owner_verified={owner_verified}"
            )

    def execute(self, input_data):
        if not self.module or not isinstance(self.module, BaseModule):
            raise ValueError(f"Module {self.id} has no attached BaseModule instance.")
        self.verify_parties()
        result = self.module.execute(input_data)
        self.register_usage(result)
        return result

    def register_usage(self, result):
        metrics = getattr(result, "metrics", None)
        if not metrics:
            return
        input_tokens = getattr(metrics, "input_tokens", 0)
        output_tokens = getattr(metrics, "output_tokens", 0)
        cost = getattr(metrics, "cost", metrics.input_tokens + metrics.output_tokens)
        model = getattr(metrics, "model", "")
        log_tool_usage(
            tool_id=self.id,
            author_id=self.author_id,
            version=self.version,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=cost,
        )

    def __call__(self, input_data):
        return self.execute(input_data)
