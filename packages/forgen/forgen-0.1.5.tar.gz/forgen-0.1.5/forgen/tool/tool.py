from abc import ABC

from forgen.tool.node import BaseNode, InputPhase, OperativePhase, OutputPhase


class Tool(BaseNode, ABC):

    def __init__(self,
                 input_phase: InputPhase,
                 operative_phase: OperativePhase,
                 output_phase: OutputPhase,
                 input_schema=None,
                 output_schema=None,
                 forced_interface=False,
                 name: str = "",
                 _id: str = None,
                 description: str = "",
                 version: str = None):
        self._forced_interface = forced_interface
        self._thread = None
        self.operative_phase = operative_phase
        if forced_interface:
            self.set_forced_interface(forced_interface)
        self._input_schema = input_schema or input_phase.input_schema
        self._output_schema = output_schema or output_phase.output_schema
        super().__init__(input_phase, operative_phase, output_phase, name, description, node_id=_id)
        if version is not None:
            self.version(version)

    def __str__(self):
        return f"{self.node_name}: {self.node_description}"

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "description": self.description,
            "version": self.version,
            "input_schema": self._convert_schema(self.input_schema),
            "output_schema": self._convert_schema(self.output_schema),
            "input_phase": self.input_phase.to_dict() if self.input_phase else None,
            "operative_phase": self.operative_phase.to_dict() if self.operative_phase else None,
            "output_phase": self.output_phase.to_dict() if self.output_phase else None,
            "forced_interface": self.forced_interface,
            "tags": getattr(self, "tags", []),
            "execution_mode": getattr(self, "execution_mode", "local")
        }

    def __call__(self, input_data):
        return self.execute(input_data)
    
    @property
    def input_data(self):
        return self.input_phase.input_data

    @input_data.setter
    def input_data(self, val):
        self.input_phase.input_data = val

    @property
    def output_data(self):
        return self.output_phase.output_data

    @output_data.setter
    def output_data(self, val):
        self.output_phase.output_data = val

    @property
    def description(self):
        return self.node_description

    @description.setter
    def description(self, val):
        self.node_description = val

    @property
    def thread(self):
        return self._thread

    @thread.setter
    def thread(self, val):
        self._thread = val

    @property
    def input_schema(self):
        return self._input_schema or self.input_phase.input_schema

    @input_schema.setter
    def input_schema(self, val):
        self._input_schema = val

    @property
    def output_schema(self):
        return self._output_schema or self.output_phase.output_schema

    @output_schema.setter
    def output_schema(self, val):
        self._output_schema = val

    @property
    def forced_interface(self):
        return self._forced_interface

    @forced_interface.setter
    def forced_interface(self, val):
        self.set_forced_interface(val)

    def set_preprocessor(self, code):
        self.input_phase.code = code

    def set_postprocessor(self, code):
        self.output_phase.code = code

    def set_forced_interface(self, val):
        self._forced_interface = val
        self.input_phase.forced_interface = val
        self.operative_phase.forced_interface = val
        self.output_phase.forced_interface = val
