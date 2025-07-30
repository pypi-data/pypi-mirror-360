from forgen.tool.builder import ToolBuilder
from forgen.llm.openai_interface.interface import get_chat_completions_response

builder = ToolBuilder(name="examiner_data_tool")

builder.set_description("Summarizes historical behavior for a USPTO examiner (e.g., allowance rate, RCE usage, appeal tendencies).")
builder.set_input_schema({
    "examiner_name": str,
    "art_unit": str
})
builder.set_output_schema({
    "allowance_rate": float,
    "average_rce_count": float,
    "appeal_likelihood": float,
    "notes": str
})


def gen(input_data, openai_client=None):
    message = f"Examiner: {input_data['examiner_name']}, Art Unit: {input_data['art_unit']}"
    response = get_chat_completions_response(
        system_content="""Based on historical trends (assumed), summarize examiner behavior. Return:
        {
            "allowance_rate": <float>,
            "average_rce_count": <float>,
            "appeal_likelihood": <float>,
            "notes": <str>
        }""",
        user_content=message,
        ai_client=openai_client,
        json_response=True
    )
    return response


builder.set_generative_function(gen)

examiner_data_tool = builder.build()
