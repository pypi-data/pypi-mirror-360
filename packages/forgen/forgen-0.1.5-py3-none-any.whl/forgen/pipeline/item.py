from forgen.tool.node import BaseNode, InputPhase, OutputPhase, OperativePhase
from forgen.tool.module import BaseModule


class PipelineItem(BaseNode, BaseModule):
    def __init__(
        self,
        _id: str,
        module: BaseModule,
        cust_input_schema: dict = None,
        cust_output_schema: dict = None,
        cust_preprocessing: callable = None,
        cust_postprocessing: callable = None,
        _version: str = "0.0.1"
    ):
        if not module:
            raise ValueError("You must provide a module for PipelineItem.")
        self._version = _version
        self.module = module
        self._input_schema = cust_input_schema or module.input_schema
        self._output_schema = cust_output_schema or module.output_schema
        self.preprocessing = cust_preprocessing
        self.postprocessing = cust_postprocessing
        self.output_data = None
        self.input_phase = InputPhase(input_schema=self._input_schema, output_schema=self.module.input_schema, code=self.preprocessing)
        self.operative_phase = OperativePhase(input_schema=self.module.input_schema, output_schema=self.module.output_schema, code=self.module.execute)
        self.output_phase = OutputPhase(input_schema=self.module.output_schema, output_schema=self._output_schema, code=self.postprocessing)
        self.verify_schema(self._input_schema, is_input=True)
        self.verify_schema(self._output_schema, is_input=False)
        self.id = _id

    @property
    def name(self):
        return self.id

    @property
    def cost(self):
        return getattr(self.module, "cost", 0)

    @property
    def metrics(self):
        return getattr(self.module, "metrics", None)

    @property
    def input_schema(self):
        return self._input_schema

    @property
    def output_schema(self):
        return self._output_schema

    @property
    def description(self):
        return getattr(self.module, "description", f"PipelineItem wrapping {self.module.__class__.__name__}")

    @property
    def thread(self):
        return getattr(self.module, "thread", None)

    @property
    def forced_interface(self):
        return getattr(self.module, "forced_interface", False)

    def set_forced_interface(self, forced_interface: bool):
        if hasattr(self.module, "set_forced_interface"):
            self.module.set_forced_interface(forced_interface)

    @staticmethod
    def verify_schema(schema, is_input: bool):
        if not isinstance(schema, dict):
            raise TypeError(f"{'Input' if is_input else 'Output'} schema must be a dictionary.")
        for key, value_type in schema.items():
            if not isinstance(key, str):
                raise TypeError(f"Schema key must be a string, got {type(key)} for key '{key}'")
            if not isinstance(value_type, type):
                raise TypeError(f"Schema value for key '{key}' must be a type, got {type(value_type)}")
        return True

    def serialize(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "input_schema": self._convert_schema(self.input_schema),
            "output_schema": self._convert_schema(self.output_schema),
            "module": self.module.serialize(),
        }

    def execute(self, input_data: dict = None):
        if self.preprocessing:
            input_data = self.preprocessing(input_data)

        output_data = self.module.execute(input_data)

        if self.postprocessing:
            output_data = self.postprocessing(output_data)

        self.output_data = output_data
        return output_data
