import os
from forgen.tool.builder import ToolBuilder
from forgen.llm.openai_interface.interface import get_chat_completions_response
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# **Preprocessing Function**: Extracts text from documents
def summarizer_preprocessing(input_data):
    documents = input_data.get("documents", [])
    return {"formatted_documents": documents}


# **Generation Function**: Calls OpenAI API to summarize documents
def summarizer_generation_function(input_data, openai_client=None):
    documents = input_data["formatted_documents"]
    summarized_docs = []

    for doc in documents:
        response = get_chat_completions_response(
            message_history=[],
            system_content="Summarize the following document in 2-3 sentences.",
            user_content=doc,
            username="",
            ai_client=openai_client
        )
        summarized_docs.append({
            "title": doc.get("title", ""),
            "summary": response
        })

    return {"summarized_documents": summarized_docs}


# **Postprocessing Function**: Formats the summaries
def summarizer_postprocessing(output_data):
    if isinstance(output_data, str):
        return {"summarized_documents": output_data}
    return {"summarized_documents": output_data.get("summarized_documents", output_data)}


# Create the agent builder
builder = ToolBuilder(name="GeneralDocumentSummarizerAgent")

builder.set_description("Summarizes documents by extracting key information, reducing large texts into concise and "
                        "meaningful summaries for quick comprehension. Input should be a dict with attr 'documents' "
                        "that is an array of elements with 'title' and 'text' attrs--if 'title' and 'text' attrs are "
                        "not present, all content of 'documents' will be treated as a single document'")

# Define input and output schemas
summarizer_input_schema = {"documents": list}  # List of dicts with {"title": str, "text": str}
summarizer_output_schema = {"summarized_documents": list}  # List of dicts with {"title": str, "summary": str}

generation_input_schema = {"formatted_documents": list}
generation_output_schema = {"summarized_documents": list}

builder.set(summarizer_input_schema, summarizer_output_schema, summarizer_generation_function, summarizer_preprocessing, summarizer_postprocessing, generation_input_schema, generation_output_schema)

# Build the agent
general_document_summarizer_agent = builder.build()

# Example execution of the agent
if __name__ == "__main__":
    user_input = {
        "documents": [
            {"title": "Advances in Quantum Computing", "text": "Quantum computing is an emerging field..."},
            {"title": "The Future of AI", "text": "Artificial intelligence is transforming industries..."}
        ]
    }
    output = general_document_summarizer_agent.execute(user_input)
    print(f"OUTPUT: {str(output)}")
