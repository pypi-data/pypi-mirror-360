import json
from abc import abstractmethod, ABC


class BaseModule(ABC):
    """
       Abstract base class defining the interface for a pipeline operand.
       This allows interoperability between Agent and Tool classes.
    """

    def __init__(self):
        self._version = "0.0.1"

    @property
    def version(self):
        """Version of the tool"""
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def input_schema(self):
        pass

    @property
    @abstractmethod
    def id(self):
        pass

    @property
    @abstractmethod
    def output_schema(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @property
    @abstractmethod
    def thread(self):
        pass

    @property
    @abstractmethod
    def forced_interface(self):
        pass

    @abstractmethod
    def set_forced_interface(self, forced_interface):
        pass

    @abstractmethod
    def execute(self, input_data) -> dict:
        raise NotImplementedError("BaseModule is abstract. Use BaseNode/Tool or GenerativeNode/GenerativeTool.")

    @abstractmethod
    def validate_schema(self):
        raise NotImplementedError("BaseModule is abstract. Use BaseNode/Tool or GenerativeNode/GenerativeTool.")

    @property
    def cost(self):
        """Default cost for non-generative tools is 0."""
        return 0

    def serialize(self) -> dict:
        spec = {
            "type": self.__class__.__name__,
            "name": self.name,
            "id": self.id,
            "description": self.description,
            "version": self.version,
            "tags": getattr(self, "tags", []),
            "execution_mode": getattr(self, "execution_mode", "local"),
            "input_schema": self._convert_schema(self.input_schema),
            "output_schema": self._convert_schema(self.output_schema),
        }

        if hasattr(self, "input_phase") and self.input_phase:
            spec["input_phase"] = self.input_phase.to_dict()
        if hasattr(self, "operative_phase") and self.operative_phase:
            spec["operative_phase"] = self.operative_phase.to_dict()
        if hasattr(self, "output_phase") and self.output_phase:
            spec["output_phase"] = self.output_phase.to_dict()

        if hasattr(self, "generative_phase") and self.generative_phase:
            if getattr(self, "use_standard_gen_framework", False):
                spec["use_standard_gen_framework"] = True
                if hasattr(self, "system_prompt"):
                    spec["system_prompt"] = self.system_prompt
                if hasattr(self, "user_prompt_template"):
                    spec["user_prompt_template"] = self.user_prompt_template
            else:
                spec["generative_phase"] = self.generative_phase.to_dict()

        if hasattr(self, "nodes"):
            spec["pipeline_nodes"] = [node.serialize() for node in self.nodes]
        if hasattr(self, "items") and hasattr(self, "dependencies"):
            spec["items"] = {k: v.serialize() for k, v in self.items.items()}
            spec["dependencies"] = self.dependencies

        if hasattr(self, "prompt"):
            spec["agent_prompt"] = self.prompt
            spec["modules"] = [mod.serialize() for mod in self.modules]

        return spec

    def _convert_schema(self, schema: dict, schema_format="name") -> dict:
        return {
            k: (v.__name__ if isinstance(v, type) else str(v))
            for k, v in schema.items()
        }

    def to_amcp_spec(self) -> dict:
        """
        Export a flat AMCP-compliant representation (for DDB or registries).
        """
        spec = self.serialize()
        for k in ["pipeline_nodes", "modules", "items", "dependencies", "agent_prompt"]:
            spec.pop(k, None)
        return spec

    def to_json(self, indent=2) -> str:
        return json.dumps(self.serialize(), indent=indent)
