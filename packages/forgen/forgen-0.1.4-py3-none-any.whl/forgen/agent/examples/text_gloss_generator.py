from forgen.tool.builder import ToolBuilder


def preprocess_text(input_data: dict) -> dict:
    """
    Splits the raw text into sections and formats them.
    Returns a dictionary with 'formatted_text' and a list of 'sections'.
    """
    raw_text = input_data.get("raw_text", None)
    if not raw_text:
        raw_text = input_data
    if isinstance(raw_text, dict):
        raw_text = str(input_data)
    return {"raw_text": raw_text}

vector_generation_function = """
def vector_generation_function(input_data):
    from forgen.llm.openai_interface import get_chat_completions_response
    return get_chat_completions_response(
        message_history=[],
        system_content=(
            "You are a helpful assistant generating vector embeddings for text sections. "
            "Return a JSON with a 'vector_entries' attribute. This attribute should be a list of objects, "
            "where each object contains an 'id' (a unique identifier for the section, such as paragraph number) "
            "and a 'text_gloss' (an array of one or more strings that would have high relevance to a user query " 
            "attempting to locate this particular information within the context of this document)."
        ),
        user_content=input_data["raw_text"],
        username="vector_glosser_agent",
        json_response=True,
        load_json=True
    )
"""

text_gloss_input_schema = {"raw_text": str}
text_gloss_output_schema = {
    "vector_entries": list  # Each entry is expected to be a dict with 'id' and 'vector'
}

tool_builder = ToolBuilder(name="TextGlosserAgent")

tool_builder.set(text_gloss_input_schema, text_gloss_output_schema, vector_generation_function, preprocessor_code=preprocess_text)

tool_builder.set_description("Generates glossaries or explanations for key terms found in a text, improving "
                              "comprehension by providing concise definitions or contextual meanings.")

text_gloss_generator_tool = tool_builder.build()


if __name__ == "__main__":
    raw_input_data = {
        "raw_text": """
        [0001] This is the first line of the document.
        [0002] Here is the second line with more details.
        [0003] Finally, this is the third line.
        """
    }

    try:
        outputs = text_gloss_generator_tool.execute(raw_input_data)
        final_output = outputs
        print("Final Output:")
        print(final_output)
    except Exception as e:
        print("Error executing the agent:", e)
