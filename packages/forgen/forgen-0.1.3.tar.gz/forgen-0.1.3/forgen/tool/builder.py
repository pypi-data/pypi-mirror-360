from typing import Union

from forgen.llm.interface import get_chat_completions_response
from forgen.tool.node import InputPhase, OutputPhase, OperativePhase
from forgen.tool.gen.tool import GenerativeTool
from forgen.tool.gen.phase import GenerativePhase
from forgen.tool.tool import Tool


class ToolBuilder:

    def __init__(self,
                 name: str = None,
                 input_schema: dict = None,
                 operative_phase_input_schema: dict = None,
                 output_schema: dict = None,
                 operative_phase_output_schema: dict = None,
                 description: str = None,
                 code_input: Union[str, callable] = None,
                 code_output: Union[str, callable] = None,
                 tool_fn: callable = None,
                 forced_interface: bool = False):
        self.name = name
        self.input_schema = input_schema
        self.operative_phase_input_schema = operative_phase_input_schema
        self.operative_phase_output_schema = operative_phase_output_schema
        self.output_schema = output_schema
        self.description = description
        self.code_input = code_input
        self.code_output = code_output
        self.code_operative = tool_fn
        self.operative_fn = None
        self.batch_mode = False
        self.tool = None
        self.forced_interface = forced_interface

    def set_operative_function(self, fn: callable):
        self.operative_fn = fn

    def set_generative_function(self, fn: callable):
        self.code_operative = fn

    def set_code_input(self, code_input: callable):
        self.code_input = code_input

    def set_code_output(self, code_output: callable):
        self.code_output = code_output

    def set_tool_name(self, name: str):
        self.name = name

    def set_description(self, description: str):
        self.description = description

    def set_input_schema(self, schema: dict):
        self.input_schema = schema

    def set_output_schema(self, schema: dict):
        self.output_schema = schema

    def set_operative_phase_input_schema(self, schema: dict):
        self.operative_phase_input_schema = schema

    def set_operative_phase_output_schema(self, schema: dict):
        self.operative_phase_output_schema = schema

    def set_batch_mode(self, val: bool):
        self.batch_mode = val

    def build(self, forced_interface: bool = False) -> Tool:
        if not self.name:
            raise ValueError("Tool name must be set.")
        if not self.input_schema or not self.output_schema:
            raise ValueError("Both input and output schemas are required.")
        if not self.operative_phase_input_schema:
            self.operative_phase_input_schema = self.input_schema
        if not self.operative_phase_output_schema:
            self.operative_phase_output_schema = self.output_schema

        # Input Phase
        input_phase = InputPhase(
            input_schema=self.input_schema,
            output_schema=self.operative_phase_input_schema,
            code=self.code_input,
            forced_interface=forced_interface
        )

        # Choose between OperativePhase or GenerativePhase
        if getattr(self, "use_standard_gen_framework", False):
            def structured_prompt_fn(input_data):
                return self.user_prompt_template.format(**input_data)

            def generation_function(input_data, openai_client=None):
                from forgen.llm.openai_interface.interface import get_chat_completions_response
                return get_chat_completions_response(
                    message_history=[],
                    system_content=self.system_prompt,
                    user_content=structured_prompt_fn(input_data),
                    ai_client=openai_client,
                    json_response=True
                )

            operative_phase = GenerativePhase(
                generative_function=generation_function,
                input_schema=input_phase.output_schema,
                output_schema=self.operative_phase_output_schema,
                forced_interface=forced_interface
            )

        elif callable(self.code_operative):
            operative_phase = GenerativePhase(
                generative_function=self.code_operative,
                input_schema=input_phase.output_schema,
                output_schema=self.operative_phase_output_schema,
                forced_interface=forced_interface
            )

        elif callable(self.operative_fn):
            operative_phase = OperativePhase(
                code=self.operative_fn,
                input_schema=input_phase.output_schema,
                output_schema=self.operative_phase_output_schema,
                forced_interface=forced_interface
            )

        else:
            raise ValueError(
                "ToolBuilder requires one of the following: "
                "a structured prompt setup (via use_standard_gen_framework), "
                "a callable generative function (code_operative), or "
                "a callable operative function (operative_fn)."
            )

        # Output Phase
        output_phase = OutputPhase(
            input_schema=operative_phase.output_schema,
            output_schema=self.output_schema,
            code=self.code_output,
            forced_interface=forced_interface
        )

        # Create the Tool or GenerativeTool
        if isinstance(operative_phase, GenerativePhase):
            self.tool = GenerativeTool(
                input_phase=input_phase,
                generative_phase=operative_phase,
                output_phase=output_phase,
                input_schema=self.input_schema,
                output_schema=self.output_schema,
                forced_interface=forced_interface,
                name=self.name,
                description=self.description
            )
        else:
            self.tool = Tool(
                input_phase=input_phase,
                operative_phase=operative_phase,
                output_phase=output_phase,
                input_schema=self.input_schema,
                output_schema=self.output_schema,
                forced_interface=forced_interface,
                name=self.name,
                description=self.description
            )

        return self.tool

    def set_code(self, operative_function,
                 preprocessor_code: Union[callable, str] = None, postprocessor_code: Union[callable, str] = None):
        self.operative_fn = operative_function
        if preprocessor_code is not None:
            self.code_input = preprocessor_code
        if postprocessor_code is not None:
            self.code_output = postprocessor_code

    def set_schema(self, input_schema, output_schema,
                   operative_input_schema: dict = None, operative_output_schema: dict = None):
        if isinstance(input_schema, dict):
            self.input_schema = input_schema
        else:
            raise TypeError(f"All schema objects must be of type dict: input_schema is of type {type(input_schema).__name__}")
        if isinstance(output_schema, dict):
            self.output_schema = output_schema
        else:
            raise TypeError(f"All schema objects must be of type dict: output_schema is of type {type(output_schema).__name__}")
        if isinstance(operative_input_schema, dict):
            self.set_operative_phase_input_schema(operative_input_schema)
        if isinstance(operative_output_schema, dict):
            self.set_operative_phase_output_schema(operative_output_schema)

    def set(self, input_schema, output_schema, operative_function,
            preprocessor_code: Union[callable, str] = None, postprocessor_code: Union[callable, str] = None,
            operative_input_schema: dict = None, operative_output_schema: dict = None):
        self.set_schema(input_schema, output_schema, operative_input_schema=operative_input_schema, operative_output_schema=operative_output_schema)
        self.set_code(operative_function, preprocessor_code=preprocessor_code, postprocessor_code=postprocessor_code)


class GenToolBuilder:

    def __init__(self,
                 name: str,
                 input_schema: dict,
                 output_schema: dict,
                 system_prompt: str,
                 user_prompt_template: str,
                 description: str = "",
                 forced_interface: bool = False):
        self.name = name
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template
        self.description = description
        self.forced_interface = forced_interface

    def build(self) -> GenerativeTool:
        def structured_prompt_fn(input_data):
            return self.user_prompt_template.format(**input_data)

        def generation_function(input_data, openai_client=None):
            return get_chat_completions_response(
                message_history=[],
                system_content=self.system_prompt,
                user_content=structured_prompt_fn(input_data),
                ai_client=ai_client,
                json_response=True
            )

        input_phase = InputPhase(
            input_schema=self.input_schema,
            output_schema=self.input_schema,
            code=(lambda x: x),
            forced_interface=self.forced_interface
        )

        generative_phase = GenerativePhase(
            generative_function=generation_function,
            input_schema=self.input_schema,
            output_schema=self.output_schema,
            forced_interface=self.forced_interface
        )

        output_phase = OutputPhase(
            input_schema=self.output_schema,
            output_schema=self.output_schema,
            code=(lambda x: x),
            forced_interface=self.forced_interface
        )

        tool = GenerativeTool(
            input_phase=input_phase,
            generative_phase=generative_phase,
            output_phase=output_phase,
            input_schema=self.input_schema,
            output_schema=self.output_schema,
            forced_interface=self.forced_interface,
            name=self.name,
            description=self.description
        )

        # Mark for serialization support
        tool.use_standard_gen_framework = True
        tool.system_prompt = self.system_prompt
        tool.user_prompt_template = self.user_prompt_template

        return tool
