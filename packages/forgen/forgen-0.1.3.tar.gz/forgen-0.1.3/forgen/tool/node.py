from abc import ABC

from forgen.tool.phase import BasePhase
from forgen.tool.module import BaseModule


class InputPhase(BasePhase):
    def __init__(self, input_data=None, input_schema=None, output_schema=None, code=None, forced_interface=False):
        """Handles the validation and processing of input data."""
        super().__init__("InputPhase", input_data, input_schema, output_schema, code, forced_interface)


class OperativePhase(BasePhase, ABC):
    def __init__(self, input_data=None, input_schema=None, output_schema=None, code=None, forced_interface=False):
        """Handles the processing of input data."""
        super().__init__("OperativePhase", input_data, input_schema, output_schema, code, forced_interface)


class OutputPhase(BasePhase):
    def __init__(self, input_data=None, input_schema=None, output_schema=None, code=None, forced_interface=False):
        """Handles post-processing and validation of the final output."""
        super().__init__("OutputPhase", input_data, input_schema, output_schema, code, forced_interface)


class BaseNode(BaseModule, ABC):

    def __init__(self, input_phase: InputPhase, operative_phase: OperativePhase, output_phase: OutputPhase, node_name: str = "", node_description: str = "", node_id: str = None, input_data: dict = None, output_data: dict = None):
        super().__init__()
        self.input_phase = input_phase
        self.operative_phase = operative_phase
        self.output_phase = output_phase
        self.node_name = node_name
        self.node_description = node_description
        self._input_schema = input_phase.input_schema
        self._output_schema = output_phase.output_schema or operative_phase.output_schema
        self.input_data = input_data
        self.output_data = output_data
        self._id = node_id

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            "input_phase": self.input_phase,
            "input_data": self.input_data,
            "input_schema": self._input_schema,
            "output_schema": self._output_schema,
            "operative_phase": str(self.operative_phase),
            "forced_interface": self.forced_interface,
            "output_data": self.output_data,
        }

    def __call__(self, input_data):
        return self.execute(input_data)

    @property
    def name(self):
        _name = self.node_name or self.__class__.__name__
        _name = _name + f"(id={self.id})" if self.id else _name
        return _name

    @name.setter
    def name(self, val):
        self.node_name = val

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, val):
        self._id = val

    @property
    def input(self):
        return self.input_phase.input

    @property
    def output(self):
        return self.output_phase.output

    def set_forced_interface(self, forced_interface):
        self.input_phase.forced_interface = forced_interface
        self.operative_phase.forced_interface = forced_interface
        self.output_phase.forced_interface = forced_interface
    
    def execute(self, input_data: dict) -> dict:
        preprocessed_data = self.input_phase.execute(input_data)
        processed_data = self.operative_phase.execute(preprocessed_data)
        self.output_data = self.output_phase.execute(processed_data)
        return self.output_data

    def validate_schema(self) -> bool:
        """
        Validate both input and output data against their respective schemas
        using the validation logic from the phase system.

        :return: True if both input and output schemas are valid. Raises ValueError otherwise.
        """
        self.input_phase.validate_schema(
            data=self.input_phase.input_data or self.input_data,
            schema=self.input_schema,
            label=f"{self.node_name or 'Node'} input"
        )
        self.output_phase.validate_schema(
            data=self.output_phase.output_data or self.output_data,
            schema=self.output_schema,
            label=f"{self.node_name or 'Node'} output"
        )
        return True

    @property
    def input_schema(self):
        return self._input_schema

    @input_schema.setter
    def input_schema(self, value):
        self._input_schema = value

    @property
    def output_schema(self):
        return self._output_schema

    @output_schema.setter
    def output_schema(self, value):
        self._output_schema = value

    def connect(self, next_node: "BaseNode", code: callable = None):
        """
        Connect this node's output to the next node's input.
        Optionally applies a transformation function (code) between output and input.
        """
        input_phase = next_node.input_phase
        output_phase = self.output_phase
        code = code if code is not None else self.output_phase.code
        if code:
            try:
                dummy_input = dict(output_phase.input_data) if isinstance(output_phase.input_data, dict) else {}
                default_map = {str: "", int: 0, float: 0.0, bool: False, list: [], dict: {}}
                for k, typ in (output_phase.output_schema or {}).items():
                    if k not in dummy_input:
                        dummy_input[k] = default_map.get(typ, None)
                result = code(dummy_input)
                if isinstance(result, dict):
                    inferred_schema = {
                        k: type(v) if v is not None else str
                        for k, v in result.items()
                    }
                    input_phase.input_schema.update(inferred_schema)
                    output_phase.output_schema = inferred_schema
                    self.output_schema = inferred_schema
            except Exception as e:
                raise RuntimeError(
                    f"Failed to infer schema from connect() code between {self.name} and {next_node.name}: {e}"
                )
        else:
            input_phase.input_schema = output_phase.output_schema
