from forgen.tool.builder import ToolBuilder
from forgen.llm.openai_interface.interface import get_chat_completions_response

builder = ToolBuilder(name="boilerplate_inserter_tool")

builder.set_description("Inserts legal boilerplate or argument templates into patent responses based on a rejection context.")
builder.set_input_schema({
    "template_type": str,
    "inserts": dict
})
builder.set_output_schema({
    "boilerplate": str
})


def gen(input_data, openai_client=None):
    template = input_data["template_type"]
    inserts = input_data["inserts"]
    user_message = f"Template Type: {template}\nInsert Data: {inserts}"
    
    response = get_chat_completions_response(
        system_content="""Use the template type and insert data to generate legal boilerplate language for a patent OA response. Output JSON:
        {
            "boilerplate": "..."
        }""",
        user_content=user_message,
        ai_client=openai_client,
        json_response=True
    )
    return response


builder.set_operative_function(gen)

boilerplate_inserter_tool = builder.build()
