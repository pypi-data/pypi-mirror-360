from forgen.agent.agent import GenerativeAgent
from forgen.agent.examples.doc_summarizer import general_document_summarizer_agent
from forgen.agent.examples.text_gloss_generator import text_gloss_generator_tool
from forgen.agent.examples.tools.batch_tool_processor import batch_processor_tool
from forgen.agent.examples.tools.list_to_string import list_to_string_tool
from forgen.agent.examples.url_summarizer import url_summarizer_agent


cog_agent_general_url = GenerativeAgent(
    prompt="Use the best tools or agents to process user requests effectively.",
    modules=[batch_processor_tool, list_to_string_tool, text_gloss_generator_tool, url_summarizer_agent, general_document_summarizer_agent],
    forced_interface=True,
    agent_name="Basic URL Fetcher & Summarizer, with batch processing support.",
    description="Used for fetching content from public URLs, summarizing said content, performing general batch "
                "operations, and large text summaries."
)


def preprocessor_code(x):
    input_items = x.get("items", [])
    input_tool_name = x.get("tool_name")
    for tool in cog_agent_general_url.modules:
        if tool.name == input_tool_name:
            return {
                "agent": tool,
                "items": input_items
            }
    return x


def postprocessor_code(x):
    input_items = x.get("output", [])
    documents = []

    def find_string(y):
        if isinstance(y, list):
            for item in y:
                find_string(item)
        else:
            documents.append(y)
    find_string(input_items)
    return {"documents": documents}


batch_processor_tool.set_preprocessor(preprocessor_code)
batch_processor_tool.set_postprocessor(postprocessor_code)

user_request = "Summarize all urls mentioned in the chat, and then write a final summary based on all of the individual summaries.  Then generate text glosses for each summary."
input_data = {
    "formatted_chat": """
    User: Hey, I found some great resources on AI and ML. Have you seen the latest research?
    Assistant: Not yet! What have you found?
    User: Well, I was reading this article on deep learning: https://en.wikipedia.org/wiki/Deep_learning.
    Assistant: That sounds interesting! Anything else?
    User: Yeah! There’s also an excellent summary on Natural Language Processing here: https://en.wikipedia.org/wiki/Natural_language_processing.
    Assistant: Nice! Those are solid sources. Anything more specific?
    User: I also came across a great breakdown of generative AI techniques at https://huggingface.co/blog/how-to-train.
    Assistant: That’s useful. Hugging Face is great for ML research.
    User: And there’s an overview of OpenAI models at https://openai.com/research/.
    Assistant: These are great! Would you like a summary of these?
    User: Yes, that would be helpful!
    """
}


# User-defined schemas
input_schema = {"formatted_chat": str}
output_schema = {"summary": str}

cog_agent_general_url.user_input_schema = input_schema
cog_agent_general_url.user_output_schema = output_schema

input_data["user_request"] = user_request

if __name__ == "__main__":
    result = cog_agent_general_url.execute(input_data)
    print(f"🔹 CognitiveAgent Output: {result}")
