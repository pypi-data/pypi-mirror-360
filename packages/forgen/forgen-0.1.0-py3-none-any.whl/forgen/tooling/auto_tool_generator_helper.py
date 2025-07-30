from forgen.tool.module import BaseModule


def secret_prompt(objective: str = ""):
    return f"""
You are an expert Python assistant that generates FORGEN-compatible generative tools using the `ToolBuilder` class.
The user will give you an OBJECTIVE.

Your job is to:
1. Determine the function name (snake_case).
2. Write Python function code that uses OpenAI's `get_chat_completions_response`.
3. Define input and output schemas (as Python dicts, using stringified types like "str", "list", etc.).
4. Provide code that builds the tool using `ToolBuilder`, `set`, `set_description`, etc.
5. Include a concise natural language function definition for the tool.

⚠️ Important:
- You MUST use the OpenAI interface the same way as in the example.
- You MUST use ToolBuilder to construct the tool.
- The generation function can be a normal function or a string-based function if needed.

---

User Objective: "{objective}"

BELOW IS AN EXAMPLE OF AN DIFFERENT GENERATIVE_TOOL.  
NOTE TO USE THE openai_interface method in the same exact manner as the examples, only changing the text input of user or system as appropriate.

```python
from forgen.agent.builder import ToolBuilder
from forgen.llm_interface.openai_interface import get_chat_completions_response
import requests
from bs4 import BeautifulSoup

def url_preprocessing(input_data):
    url = input_data['url']
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()
        return {{'formatted_input': text_content}}
    except requests.exceptions.RequestException as e:
        return {{'formatted_input': f"Error fetching URL content: {{str(e)}}"}}

def url_summarizer_generation_function(input_data, openai_client=None):
    response = get_chat_completions_response(
        message_history=[],
        system_content="SUMMARIZE THIS URL INTO A JSON WITH OUTPUT SCHEMA: {{'summary_text': summary_text}}",
        user_content=input_data["formatted_input"],
        username="url_summarizer",
        json_response=True,
        ai_client=openai_client
    )
    return response

builder = ToolBuilder(tool_name="URLSummarizerAgent")

url_summarizer_input_schema = {{'url': str}}
url_summarizer_generation_input_schema = {{'formatted_input': str}}
url_summarizer_output_schema = {{'summary_text': str}}

builder.set_description("Fetches and summarizes the content of a given URL.")

builder.set(
    url_summarizer_input_schema,
    url_summarizer_output_schema,
    url_summarizer_generation_function,
    preprocessor_code=url_preprocessing,
    operative_input_schema=url_summarizer_generation_input_schema)

url_summarizer_agent = builder.build()
NOW RETURN A JSON WITH THESE FIELDS ONLY:

{{
  "name": "...",
  "function_name": "...",
  "function_code": "...",  <-- full Python string
  "input_schema": {{ "field": "type" }},
  "output_schema": {{ "field": "type" }},
  "function_definition": "..."
}}

Ensure the function_code includes working OpenAI usage and follows the builder format exactly. 
response = get_chat_completions_response(
    message_history=[],
    system_content="RETURN ONLY VALID JSON THAT FITS THE SCHEMA. NO MARKDOWN. NO EXPLANATIONS.",
    user_content=prompt,
    username="generative_tool_generator",
    openai_client=self.openai_client,
    load_json=True
)

return response
"""

import os
import json


def load_all_tools_from_dir(path: str, openai_client=None):
    """
    Loads and builds all tool JSON definitions from a directory.

    Args:
        path (str): Directory containing .json tool definitions.
        openai_client: Optional OpenAI client for dynamic tools.

    Returns:
        dict: {tool_name: built_tool}
    """
    TYPE_MAPPING = {
        "str": str, "int": int, "float": float, "bool": bool,
        "list": list, "dict": dict, "tuple": tuple,
        "set": set, "NoneType": type(None)
    }

    tool_registry = {}

    for filename in os.listdir(path):
        if filename.endswith(".json"):
            filepath = os.path.join(path, filename)
            with open(filepath, "r") as f:
                definition = json.load(f)

            name = definition["name"]
            function_name = definition["function_name"]
            function_code = definition["function_code"]
            function_description = definition.get("function_summary", None)
            input_schema = {
                k: TYPE_MAPPING.get(v, str) for k, v in definition["input_schema"].items()
            }
            output_schema = {
                k: TYPE_MAPPING.get(v, str) for k, v in definition["output_schema"].items()
            }

            local_scope = {}
            exec(function_code, globals(), local_scope)
            function = local_scope[function_name]

            builder = ToolBuilder(name=name)
            builder.set_description(f"Loaded from {filename}")
            builder.set(
                input_schema=input_schema,
                output_schema=output_schema,
                operative_function=function
            )
            _tool = builder.build()
            _tool.description = function_description if function_description else _tool.description
            tool_registry[name] = _tool

    return tool_registry

import sys
import subprocess
import re

from forgen.llm.openai_interface.interface import get_chat_completions_response
from forgen.tool.builder import ToolBuilder
from typing import List, Dict, Any


def extract_required_libs(code: str):
    required = set()
    for line in code.splitlines():
        if line.strip().startswith("import ") or line.strip().startswith("from "):
            match = re.match(r"(?:from|import)\s+([a-zA-Z0-9_]+)", line)
            if match:
                required.add(match.group(1))
    return list(required)


def install_missing_libs_if_needed(code: str):
    required = extract_required_libs(code)
    missing = [lib for lib in required if lib not in sys.modules]
    if missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)


def get_default_exec_context():
    return {
        "ToolBuilder": ToolBuilder,
        "get_chat_completions_response": get_chat_completions_response,
        "List": List,
        "Dict": Dict,
        "Any": Any,
        "print": print  # always useful for debugging!
    }


def exec_in_package_scope(code: str, output_schema=None):
    """
    Install missing libs, prepare execution context, and run exec() safely.
    """
    install_missing_libs_if_needed(code)
    context = get_default_exec_context()
    local_scope = {}
    exec(code, context, local_scope)
    return local_scope


def build_system_prompt_for_schema(output_schema: dict, context_description: str = "") -> str:
    schema_preview = json.dumps({
        key: ("..." if "List" not in str(val) else ["..."])
        for key, val in output_schema.items()
    }, indent=2)

    return f"""You are a JSON-only API {context_description}.

You MUST return a valid JSON object that matches exactly this format:
{schema_preview}

Do NOT include explanations, headers, markdown, or extra commentary.
Only output valid JSON in the correct shape.
"""


TYPE_MAPPING = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "set": set,
    "BaseModule": BaseModule,
    "NoneType": type(None)
}


SAVE_DIR = "../agent/saved_generative_tools"


def convert_schema(schema: dict) -> dict:
    return {key: TYPE_MAPPING.get(value, str) for key, value in schema.items()}


if __name__ == "__main__":
    tools = load_all_tools_from_dir("../agent/saved_generative_tools")

    summary = tools["ParagraphSummarizerAgent"].execute({
        "paragraph_text": "A base station for OFDM sub-carrier optimization in telecom networks..."
    })

    print(summary)