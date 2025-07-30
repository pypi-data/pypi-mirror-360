from forgen.tool.builder import ToolBuilder

# Create a ToolBuilder instance
builder = ToolBuilder(name="InputChunker")

# Define input and output schemas
chunker_input_schema = {
    'prompt': str,
    'body_text': str,
    'num_chunks': int  # Optional parameter for desired number of chunks
}
chunker_output_schema = {
    'chunks': list  # List of text chunks
}


# Function to estimate token count (Placeholder function)
def estimate_tokens(text, model="MSG_GEN_MODEL"):
    """Estimate the number of tokens in a given text based on a model."""
    # Placeholder: Replace with actual token estimation logic
    return len(text.split())  # Naive approximation using word count


# Function to chunk the input text while including the prompt in each chunk
def chunk_input(input_data):
    prompt = input_data.get("prompt", "")
    body_text = input_data.get("body_text", "")
    num_chunks = input_data.get("num_chunks", None)  # Optional parameter

    if not prompt or not body_text:
        return {"error": "Both 'prompt' and 'body_text' are required."}

    max_tokens_per_chunk = 500  # Define max tokens per chunk (default)
    input_tokens = estimate_tokens(prompt)
    words = body_text.split()  # Splitting body_text into words for chunking

    # Determine chunk size dynamically if num_chunks is provided
    if num_chunks and num_chunks > 0:
        total_tokens = estimate_tokens(body_text)
        available_tokens_per_chunk = max(input_tokens, total_tokens // num_chunks)
    else:
        available_tokens_per_chunk = max_tokens_per_chunk - input_tokens

    chunks = []
    current_chunk = []
    current_chunk_tokens = 0

    for word in words:
        word_tokens = estimate_tokens(word)
        if current_chunk_tokens + word_tokens > available_tokens_per_chunk:
            # Finalize the current chunk and start a new one
            chunks.append(prompt + " " + " ".join(current_chunk))
            current_chunk = [word]
            current_chunk_tokens = word_tokens
        else:
            current_chunk.append(word)
            current_chunk_tokens += word_tokens

    # Add the last chunk if not empty
    if current_chunk:
        chunks.append(prompt + " " + " ".join(current_chunk))

    return {"chunks": chunks}


# Add tool to the builder
builder = ToolBuilder(
    name="InputChunker",
    tool_fn=chunk_input,
    input_schema=chunker_input_schema,
    output_schema=chunker_output_schema,
    description="Splits a long body of text into smaller chunks while preserving a given prompt in each chunk. "
                "Supports an optional parameter to specify the desired number of chunks for optimized text processing."
)

# Build the tool
input_chunker_tool = builder.build()

# Example execution of the tool
if __name__ == "__main__":
    user_input = {
        "prompt": "Summarize the following text:",
        "body_text": ("This is a long document that needs to be split into chunks. "
                      "Each chunk should be small enough to fit within the model's token limit, "
                      "while ensuring that the prompt is included in every request. "
                      "This helps in keeping the context consistent across multiple generations."),
        "num_chunks": 3  # Example: Requesting 3 chunks
    }

    # Execute the tool
    chunked_output = input_chunker_tool.execute(user_input)
    print(f"OUTPUT: {str(chunked_output)}")
