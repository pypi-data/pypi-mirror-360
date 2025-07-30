from openai import OpenAI
from forgen.tool.module import BaseModule


class MCPToolWrapper(BaseModule):
    def __init__(self, name, server_url, tool_name, headers=None):
        super().__init__(name=name)
        self.server_url = server_url
        self.tool_name = tool_name
        self.headers = headers or {}

    def execute(self, input_data: dict) -> dict:
        client = OpenAI()
        response = client.responses.create(
            model="gpt-4.1",
            input=input_data["prompt"],
            tools=[{
                "type": "mcp",
                "server_label": self.name,
                "server_url": self.server_url,
                "headers": self.headers,
                "allowed_tools": [self.tool_name],
                "require_approval": "never"
            }]
        )
        return {"output": response.output_text}
