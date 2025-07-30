import subprocess
import sys
import json
import os
import uuid
from datetime import datetime

from forgen.tool.builder import ToolBuilder
import openai

from forgen.tooling.auto_tool_generator_helper import secret_prompt, exec_in_package_scope, SAVE_DIR, \
    convert_schema
from forgen.tool.gen.tool import GenerativeTool
from forgen.tool.gen.phase import GenerativePhase
from forgen.tool.node import InputPhase, OutputPhase
from forgen.tool.tool import Tool
from forgen.llm.openai_interface.interface import get_chat_completions_response


class AutoToolGenerator(GenerativeTool):
    """Generative AI-driven, Automated Tool Generator that determines processing functions and schemas dynamically."""

    def __init__(self, openai_client_or_api_key, *args, **kwargs):
        self.openai_client = openai_client_or_api_key
        if isinstance(openai_client_or_api_key, str):
            self.openai_client = openai.OpenAI(api_key=openai_client_or_api_key)
        input_phase = InputPhase()
        generative_phase = GenerativePhase(self.build_and_save_tool)
        output_phase = OutputPhase()
        args = list(args)
        args.extend([input_phase, generative_phase, output_phase])
        kwargs = {
            "input_schema": {"objective": str},
            "output_schema": {"generated_tool": Tool}
        }
        super().__init__(*args, **kwargs)

    def install_missing_libs(self, function_code: str):
        required_libs = []
        for line in function_code.splitlines():
            if line.startswith("import ") or line.startswith("from "):
                lib = line.split()[1].split(".")[0]
                if lib not in sys.modules:
                    required_libs.append(lib)
        if required_libs:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + required_libs)

    def generate_generative_tool_definition(self, objective: str):
        prompt = secret_prompt(objective)
        response = get_chat_completions_response(
            message_history=[],
            system_content="Return valid JSON as per the prompt instructions.",
            user_content=prompt,
            username="generative_tool_generator",
            openai_client=self.openai_client,
            load_json=True
        )
        return response

    def _execute(self, input_data: dict):
        objective = input_data.get("objective", "")
        generated_tool = self.build_and_save_tool(objective)
        return {"generated_tool": generated_tool}

    def build_generative_tool(self, objective: str):
        generative_tool_def = self.generate_generative_tool_definition(objective)

        name = generative_tool_def["name"]
        function_name = generative_tool_def["function_name"]
        function_summary = generative_tool_def.get("function_definition", None)
        function_code = generative_tool_def["function_code"]

        input_schema = convert_schema(generative_tool_def["input_schema"])
        output_schema = convert_schema(generative_tool_def["output_schema"])

        operative_input_schema = generative_tool_def.get("operative_input_schema", input_schema)
        operative_output_schema = generative_tool_def.get("operative_output_schema", output_schema)

        preprocessor_code = generative_tool_def.get("preprocessor", None)
        postprocessor_code = generative_tool_def.get("postprocessor", None)

        local_scope = exec_in_package_scope(function_code)
        function = local_scope[function_name]

        preprocessor = None
        if preprocessor_code is not None:
            pre_scope = exec_in_package_scope(preprocessor_code)
            preprocessor = pre_scope["preprocessor"]

        postprocessor = None
        if postprocessor_code is not None:
            post_scope = exec_in_package_scope(postprocessor_code)
            postprocessor = post_scope["preprocessor"]

        builder = ToolBuilder(name=name, description=function_summary)
        builder.set_description(f"Auto-generated tool to {objective}")
        builder.set(
            input_schema=input_schema,
            output_schema=output_schema,
            operative_function=function,
            preprocessor_code=preprocessor,
            postprocessor_code=postprocessor,
            operative_input_schema=operative_input_schema,
            operative_output_schema=operative_output_schema,
        )

        tool_instance = builder.build()

        return tool_instance, function_code, preprocessor_code, postprocessor_code

    def save_tool_definition(self, tool_name: str, definition: dict):
        path = os.path.join(SAVE_DIR, f"{tool_name}.json")
        with open(path, "w") as f:
            json.dump(definition, f, indent=2)
        print(f"[SAVED] Tool definition saved to {path}")

    def build_and_save_tool(self, objective: str):
        """
        Generates, builds, and saves a tool based on the objective.

        Args:
            objective (str): The high-level instruction for what the tool should do.

        Returns:
            tool_instance: The built Tool instance
        """
        _tool, function_code, preprocessor_code, postprocessor_code = self.build_generative_tool(objective)
        tool_definition = {
            "name": _tool.name,
            "input_schema": {k: v.__name__ for k, v in _tool.input_schema.items()},
            "output_schema": {k: v.__name__ for k, v in _tool.output_schema.items()},
            "operative_phase_input_schema": {k: v.__name__ for k, v in _tool.operative_phase.input_schema.items()},
            "operative_phase_output_schema": {k: v.__name__ for k, v in _tool.operative_phase.output_schema.items()},
            "function_name": _tool.operative_phase.code.__name__,
            "function_description": _tool.description,
            "function_code": function_code,
            "preprocessor": preprocessor_code,
            "postprocessor": postprocessor_code,
            **({"docstring": _tool.__doc__} if _tool.__doc__ else {}) 
        }
        self.save_tool_definition(_tool.name, tool_definition)
        return _tool
    
    def build_and_store_in_ddb(self, objective: str, ddb_store_fn: callable, username: str = "_", tool_id: str = ""):
        """
        Generates, builds, saves locally, and stores the tool definition in DynamoDB.
    
        Args:
            objective (str): High-level instruction to generate the tool.
            ddb_store_fn (callable): Function to call to store in your ddb
            username (str): Username for storing in ddb.
            tool_id (str): Tol id for storing in ddb.  If not provided will be rand.
    
        Returns:
            Tool: The built tool instance
        """
        _tool, function_code, preprocessor_code, postprocessor_code = self.build_generative_tool(objective)
    
        if not tool_id:
            tool_id = str(uuid.uuid4()) 
        # Build full tool definition
        now = datetime.utcnow().isoformat()
        tool_definition = {
            "tool_name": _tool.name,
            "input_schema": {k: v.__name__ for k, v in _tool.input_schema.items()},
            "output_schema": {k: v.__name__ for k, v in _tool.output_schema.items()},
            "operative_phase_input_schema": {k: v.__name__ for k, v in _tool.operative_phase.input_schema.items()},
            "operative_phase_output_schema": {k: v.__name__ for k, v in _tool.operative_phase.output_schema.items()},
            "function_name": _tool.operative_phase.code.__name__,
            "function_description": _tool.description,
            "function_code": function_code,
            "preprocessor": preprocessor_code,
            "postprocessor_code": postprocessor_code,
            "created_at": now,
            "updated_at": now,
        }
    
        # Optional: add docstring if present
        if _tool.__doc__:
            tool_definition["docstring"] = _tool.__doc__
    
        # Save to local file (optional and reuse existing save function)
        self.save_tool_definition(_tool.name, tool_definition)
    
        # Save to DynamoDB
        try:
            ddb_store_fn(username, tool_id, tool_definition)
            print(f"✅ Tool '{_tool.name}' stored in DynamoDB.")
        except Exception as e:
            print(f"❌ Failed to store tool '{_tool.name}' in DynamoDB: {e}")
    
        return _tool

#
# if __name__ == "__main__":
#     from dotenv import load_dotenv
#
#     load_dotenv()
#
#     openai_api_key = os.getenv("OPENAI_API_KEY")
#     generator = AutoToolGenerator(openai_client_or_api_key=openai_api_key)
#     #
#     # # objective = "Extract claims from a patent document. Input: {'document_text': str}, Output: {'claims': List[str]}"
#     objective = """Generate a tool (the "Generated Tool" herein, but give it a better function_name) that uses this tool (AutoToolGenerator with {"input_schema": {"objective": str}, "output_schema": {"generated_tool": Tool}}) to generate one or more tools as per the input request.  The output of the Generated Tool after processing an input 'request', should be a list of the tool definitions.  After the AutoToolGenerator.execute returns a tool, you then call AutoToolGenerator.save_tool_definition(self, tool_name: str, definition: dict) to save the tool.
#
#     Schema Required for the Generated Tool: Input: {'request': str}, Output: {'tools': list}"""
#
#     tool = generator.build_and_save_tool(objective)
#
#     tool_name = "GeneratedTool"
#     example_input = {
#         "request": "Build a suite of tools for building a patent application."
#     }
#     tool = ToolLoader.load_generative_tool(tool_name)
#     tool.set_forced_interface(True)
#     batch_processor_tool.execute({"items": list, "tool_name": str})
#     print("🧪 Tool output:")
#     print(tool.execute(example_input))
#     print(f"End of Tool {tool_name} output")
#
# """
#     # Step 1 — Initialize with your API key
#     openai_api_key = "sk-"
#     generator = AutoToolGenerator(openai_api_key=openai_api_key)
#
#     # Step 2 — Provide an objective for the tool
#     objective = "Summarize a paragraph of text into a concise summary, with input_schema: {'paragraph_text': str} and" \
#                 "output_schema = {'summary': str}"
#
#     # Step 3 — Build the generative tool using OpenAI
#     tool, gen_code_as_str = generator.build_generative_tool(objective)
#
#     # Step 4 — Run the tool on examples input
#     example_input = {
#         "paragraph_text": (
#             "The invention relates to a base station and method for communicating data with terminals "
#             "in a wireless telecommunications system using Orthogonal Frequency Division Multiplex (OFDM) sub-carriers. "
#             "It dynamically allocates unused sub-carriers based on the receiver's bandwidth status and traffic load."
#         )
#     }
#
#     result = tool.execute(example_input)
#
#     # Step 5 — Print the output
#     print("💡 Tool Output:")
#     print(result)
#
#     # Step 6 — Save the tool for reuse (optional)
#     generator.save_tool_definition(tool.name, {
#         "name": tool.name,
#         "input_schema": {k: v.__name__ for k, v in tool.input_schema.items()},
#         "output_schema": {k: v.__name__ for k, v in tool.output_schema.items()},
#         "function_name": tool.operative_phase.code.__name__,
#         "function_code": gen_code_as_str
#     })
# """