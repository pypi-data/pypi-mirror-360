from forgen.tool.builder import ToolBuilder
from forgen.llm.openai_interface.interface import get_chat_completions_response


def gen(input_data, openai_client=None):
    response = get_chat_completions_response(
        system_content="Summarize the key teaching of the prior art text in one sentence.",
        user_content=input_data["reference_text"],
        ai_client=openai_client,
        json_response=True
    )
    return response




builder = ToolBuilder(name="reference_summarizer_node")
builder.set_description("Summarizes the core teachings of a prior art excerpt.")

input_schema = {
    "reference_text": str
}

output_schema = {
    "summary": str
}
builder.set_schema(input_schema, output_schema)

builder.set_code(gen)

reference_summarizer_node = builder.build()
