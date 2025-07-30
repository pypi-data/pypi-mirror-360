import json


class OpenAIToolAdapter:
    """
        Adapter for ForGen Tools and OpenAI Tools
    """
    def __init__(self, tool):
        self.tool = tool

    def to_openai_tool(self):
        """

        :return: dict formatted per OpenAI's API for Tools
        """
        return {
            "type": "function",
            "name": self.tool.name,
            "description": self.tool.description,
            "parameters": self.tool.input_schema,
            "strict": True
        }

    def execute(self, arguments_json):
        """
            Executes the tool with the arguments
        :param arguments_json: the arguments to pass into the tool
        :return:
        """
        args = json.loads(arguments_json)
        result = self.tool.execute(args)
        return result


class ToolRegistry:
    """
        For keeping a registry of (a set of) tools so that the set may be
        transcoded readily.
    """
    def __init__(self, tools: list):  # List of your Tool instances
        self.adapters = {
            tool.name: OpenAIToolAdapter(tool)
            for tool in tools
        }

    def openai_tools(self):
        """
            Converts registered tools to OpenAI API format
        :return:
        """
        return [adapter.to_openai_tool() for adapter in self.adapters.values()]

    def dispatch(self, tool_call):
        """
            Executes the set of tools
        :param tool_call:
        :return:
        """
        adapter = self.adapters[tool_call["name"]]
        return adapter.execute(tool_call["arguments"])
