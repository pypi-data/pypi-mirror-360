import json
import os
import pprint

from forgen.tooling.auto_tool_generator_helper import convert_schema, get_default_exec_context
from forgen.tool.builder import ToolBuilder
from forgen.llm.openai_interface.interface import get_chat_completions_response


def generate_dummy_output(schema: dict):
    def dummy_value(py_type):
        if py_type == str:
            return "dummy string"
        elif py_type == int:
            return 123
        elif py_type == float:
            return 3.14
        elif py_type == bool:
            return True
        elif py_type == list:
            return ["item1", "item2"]
        elif py_type == dict:
            return {"key": "value"}
        elif py_type == tuple:
            return 1, 2
        elif py_type == set:
            return {"a", "b"}
        else:
            return None

    return {key: dummy_value(py_type) for key, py_type in schema.items()}


def get_exec_context(output_schema: dict = None):
    from forgen.llm.openai_interface.interface import get_chat_completions_response

    is_testing = os.getenv("ENV", "").lower() == "test"

    if is_testing and output_schema:
        def mock_get_chat_completions_response(*args, **kwargs):
            return generate_dummy_output(output_schema)
        return {
            "get_chat_completions_response": mock_get_chat_completions_response
        }
    else:
        return {
            "get_chat_completions_response": get_chat_completions_response
        }


class ToolLoader:

    @staticmethod
    def load_generative_tool(tool_id: str, tool_dir: str = "../saved_generative_tools", ddb_fn=None, username=None):
        """
        Load a generative tool either from a DDB fetch function or from a local JSON file.

        :param tool_id: The name or ID of the tool.
        :param tool_dir: Directory where local tools are stored.
        :param ddb_fn: Optional function to fetch tool definition from DDB.
        :param username: Optional username to fetch tool definition from DDB.
        :return: A generative tool instance.
        """
        definition = None

        # Try loading from DDB if function is provided
        for username in [username, "system"]:
            if ddb_fn:
                try:
                    definition = ddb_fn(username, tool_id)
                    if definition is not None:
                        break
                except Exception as e:
                    print(f"[DDB] Failed to load tool from DDB: {e}")

        # Fallback to local file if DDB failed or returned nothing
        if not definition:
            path = os.path.join(tool_dir, f"{tool_id}.json")
            if not os.path.exists(path):
                raise FileNotFoundError(f"No tool found in DDB or local path: {tool_id}")
            with open(path, "r") as f:
                definition = json.load(f)

        # Convert schemas
        input_schema = convert_schema(definition["input_schema"])
        output_schema = convert_schema(definition["output_schema"])
        operative_input_schema = convert_schema(definition["operative_phase_input_schema"])
        operative_output_schema = convert_schema(definition["operative_phase_output_schema"])
        if definition.get("use_standard_gen_framework"):
            user_prompt_fn = None
            if "user_prompt_fn_code" in definition:
                _scope = {}
                exec(definition["user_prompt_fn_code"], {}, _scope)
                user_prompt_fn = list(_scope.values())[-1]
            elif "user_prompt_template" in definition:
                template = definition["user_prompt_template"]
                user_prompt_fn = lambda input_data: template.format(**input_data)
            else:
                raise ValueError(
                    "Missing `user_prompt_fn_code` or `user_prompt_template` with `use_standard_gen_framework`.")

            def operative_fn(input_data, openai_client=None):
                prompt = user_prompt_fn(input_data)
                system_prompt = f"THE RESPONSE MUST BE A JSON OBJECT THAT IS FORMATTED ACCORDING TO THE SCHEMA: {operative_output_schema}\n\n{definition['system_prompt']}"
                response = get_chat_completions_response(
                    message_history=[],
                    system_content=system_prompt,
                    user_content=prompt,
                    ai_client=openai_client,
                    json_response=True
                )
                return {key: response.get(key, None) for key in output_schema}
        else:
            local_scope = {}
            exec(definition["function_code"], get_default_exec_context(), local_scope)
            operative_fn = local_scope[definition["function_name"]]
        preprocessor = definition.get("preprocessor", None)
        if preprocessor:
            _scope = {}
            exec(definition["preprocessor"], get_exec_context(operative_input_schema), _scope)
            preprocessor = list(_scope.values())[-1]
        postprocessor = definition.get("postprocessor", None)
        if postprocessor:
            _scope = {}
            exec(definition["postprocess_code"], get_exec_context(operative_output_schema), _scope)
            postprocessor = list(_scope.values())[-1]
        builder = ToolBuilder(name=tool_id)
        if definition.get("function_description"):
            builder.set_description(definition["function_description"])
        builder.set(
            input_schema=input_schema,
            output_schema=output_schema,
            operative_function=operative_fn,
            preprocessor_code=preprocessor,
            postprocessor_code=postprocessor,
            operative_input_schema=operative_input_schema,
            operative_output_schema=operative_output_schema,
        )

        return builder.build()

    @staticmethod
    def load_all_generative_tools_from_dir(directory_path: str, openai_client=None):
        """
        Loads all generative tools saved as JSON files from a directory.
        Uses `load_generative_tool()` to avoid code duplication.

        Args:
            directory_path (str): Folder containing JSON definitions.
            openai_client: Optional OpenAI client instance to be passed to loaded tools.

        Returns:
            dict: A dictionary of {tool_name: tool_instance}
        """
        tool_registry = {}

        for filename in os.listdir(directory_path):
            if not filename.endswith(".json"):
                continue

            tool_name = filename.removesuffix(".json")
            try:
                tool = ToolLoader.load_generative_tool(tool_name, tool_dir=directory_path)
                tool_registry[tool_name] = tool
            except Exception as e:
                print(f"[ERROR] Failed to load {tool_name}: {e}")

        return tool_registry

    @staticmethod
    def store_std_gen_tools_into_ddb(array_file_path, ddb_func=None, username="system"):
        """
        Loads tools from a JSON file containing either a single tool definition or an array of tool definitions.
        Optionally stores each tool into a database via `ddb_func`.

        Args:
            array_file_path (str): Path to the JSON file.
            ddb_func (function): Optional. Function to store tools in a remote database (e.g., DynamoDB).
            username (str): Optional. Username to assign to stored tools.

        Returns:
            dict: A dictionary of {tool_name: built_tool_instance}
        """
        tool_registry = {}
        for filename in os.listdir(array_file_path):
            if not filename.endswith(".json"):
                continue
            full_path = os.path.join(array_file_path, filename)
            with open(full_path, "r") as f:
                definitions = json.load(f)
            if isinstance(definitions, dict):
                definitions = [definitions]
            for definition in definitions:
                tool_id = definition.get("tool_name") or definition.get("name")
                if not tool_id:
                    print("[WARN] Skipping a tool with no 'tool_name'")
                    continue
                try:
                    if ddb_func:
                        print(f"[DDB] Storing tool '{tool_id}' in DDB...")
                        ddb_func(username=username, tool_id=tool_id, **definition)
                except Exception as e:
                    print(f"[ERROR] Failed to load tool '{tool_id}': {e}")
        return tool_registry

    @staticmethod
    def store_local_saved_tools_into_ddb(directory_path: str, ddb_func, username="jimmy"):
        """
        Loads all generative tools from a local directory and stores their JSON definitions into DynamoDB.

        Args:
            directory_path (str): Directory where .json tool definitions are saved.
            ddb_func (function): Function to insert into DDB (e.g. `ddb.add_tool_to_tool_registry_in_ddb`).
            username (str): Owner of the tools in DDB.
        """
        for filename in os.listdir(directory_path):
            if not filename.endswith(".json"):
                continue
            path = os.path.join(directory_path, filename)
            with open(path, "r") as f:
                try:
                    tool_definition = json.load(f)
                    tool_id = tool_definition.get("tool_name") or tool_definition.get("name") or filename.removesuffix(".json")
                    if not tool_id:
                        print(f"[WARN] Skipping {filename}: No tool_id found.")
                        continue
                    print(f"📥 Storing tool '{tool_id}' in DDB...")
                    ddb_func(username=username, tool_id=tool_id, **tool_definition)
                except Exception as e:
                    print(f"[ERROR] Failed to store {filename}: {e}")


def generate_dummy_value(py_type):
        if py_type == str:
            return "test string"
        elif py_type == int:
            return 42
        elif py_type == float:
            return 3.14
        elif py_type == bool:
            return True
        elif py_type == list:
            return ["item1", "item2"]
        elif py_type == dict:
            return {"key": "value"}
        elif py_type == tuple:
            return 1, 2
        elif py_type == set:
            return {"a", "b"}
        else:
            return None
def test_tools(tools):

    print(f"🧪 Testing {len(tools)} tools...\n")

    for tool_name, tool in tools.items():
        test_tool(tool, tool_name)
        print("-" * 50)


def test_tool(tool, tool_name):
    print(f"▶️  Running test for tool: {tool_name}")
    try:
        # Create dummy input based on tool's input schema
        dummy_input = {
            k: generate_dummy_value(v) for k, v in tool.input_schema.items()
        }

        # Run the tool
        result = tool.execute(dummy_input)
        print("✅ Output:")
        pprint.pprint(result)
    except Exception as e:
        print("❌ Error while executing tool:")
        print(e)


if __name__ == "__main__":
    from forgen.ddb import tooling
    ToolLoader.store_std_gen_tools_into_ddb("../agent/saved_generative_tools/std_gen_tools", tooling.add_tool_to_tool_registry_in_ddb, "jimmy")
    # store_local_saved_tools_into_ddb("../saved_generative_tools", tooling.add_tool_to_tool_registry_in_ddb)

    # tool_to_load = "PatentClaimsExtractor"
    # loaded_tool = ToolLoader.load_generative_tool(tool_to_load)
    # test_tool(loaded_tool, tool_to_load)
    # auto_generated_tools = ToolLoader.load_all_generative_tools_from_dir("../agent/saved_generative_tools")
    # predefined_tools = ToolLoader.load_all_generative_tools_from_dir("patent")
    # duplicate_keys = set(auto_generated_tools.keys()) & set(predefined_tools.keys())
    # if duplicate_keys:
    #     raise ValueError(f"Duplicate tool names found: {duplicate_keys}")
    #
    # tools = {**auto_generated_tools, **predefined_tools}
    # test_tools(tools)
