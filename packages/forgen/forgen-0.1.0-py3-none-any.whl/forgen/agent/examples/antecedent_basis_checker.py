from forgen.tool.builder import ToolBuilder
from forgen.llm.openai_interface.interface import get_chat_completions_response

builder = ToolBuilder(name="antecedent_basis_tool")

builder.set_description("Checks whether a specified term in a claim or spec has proper antecedent basis.")
builder.set_input_schema({
    "text": str,
    "term": str
})
builder.set_output_schema({
    "term": str,
    "has_antecedent_basis": bool,
    "justification": str
})




def gen(input_data, openai_client=None):
    response = get_chat_completions_response(message_history=[],
                                                    system_content="""Return a JSON: Determine whether the specified term has antecedent basis in the provided text.
        Return the format:
        {
            "term": <term>,
            "has_antecedent_basis": <bool>,
            "justification": <str>
        }""",
                                                    user_content=f"Text: {input_data['text']}\nTerm: {input_data['term']}",
                                                    ai_client=openai_client,
                                                    json_response=True
                                                    )
    return {
        "term": input_data["term"],
        "has_antecedent_basis": response.get("has_antecedent_basis", False),
        "justification": response.get("justification", "N/A")
    }




builder.set_operative_function(gen)

antecedent_basis_checker = builder.build()
