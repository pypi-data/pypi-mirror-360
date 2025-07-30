from forgen.tool.gen.phase import GenerativePhase
from forgen.tool.tool import Tool
from forgen.tool.node import InputPhase, OutputPhase


class GenerativeTool(Tool):

    @property
    def thread(self):
        return self._thread

    @property
    def cost(self):
        return getattr(self.generative_phase, "cost", None)

    @property
    def metrics(self):
        return getattr(self.generative_phase, "metrics", None)

    def __init__(
        self,
        input_phase: InputPhase,
        generative_phase: GenerativePhase,
        output_phase: OutputPhase,
        input_schema=None,
        output_schema=None,
        forced_interface=None,
        name: str = "",
        description: str = "",
        _id: str = ""
    ):
        self.generative_phase = generative_phase
        self.use_standard_gen_framework = getattr(self, "use_standard_gen_framework", False)
        self.system_prompt = getattr(self, "system_prompt", None)
        self.user_prompt_template = getattr(self, "user_prompt_template", None)

        super().__init__(
            _id=_id,
            input_phase=input_phase,
            operative_phase=generative_phase,
            output_phase=output_phase,
            input_schema=input_schema,
            output_schema=output_schema,
            forced_interface=forced_interface,
            name=name,
            description=description
        )

    def serialize(self) -> dict:
        base = super().serialize()

        if getattr(self, "use_standard_gen_framework", False):
            base["use_standard_gen_framework"] = True
            if self.system_prompt:
                base["system_prompt"] = self.system_prompt
            if self.user_prompt_template:
                base["user_prompt_template"] = self.user_prompt_template
            base.pop("operative_phase", None)  # don't serialize generative phase if using standard prompt framework
        else:
            base["generative_phase"] = self.generative_phase.to_dict()

        return base

