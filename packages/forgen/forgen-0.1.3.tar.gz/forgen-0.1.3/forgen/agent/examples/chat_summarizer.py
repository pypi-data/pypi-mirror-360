# chat_summarizer.py
from forgen.agent.examples import openai_client
from forgen.tool.gen.tool import GenerativeTool
from forgen.tool.gen.phase import GenerativePhase
from forgen.tool.node import InputPhase, OutputPhase
from forgen.pipeline.pipeline import SerialPipeline
from forgen.llm.openai_interface.interface import get_chat_completions_response

# Define the chat conversation
chat_messages = [
    {"role": "customer", "message": "Hi, I need help with my order."},
    {"role": "agent", "message": "Sure, can you please provide your order ID?"},
    {"role": "customer", "message": "It's #12345."},
    {"role": "agent", "message": "Thank you! Your order has been shipped and should arrive tomorrow."}
]

# InputPhase: Preprocess the chat into a single formatted string
input_schema_1 = {"chat": list}
output_schema_1 = {"formatted_chat": str}


def input_phase_1_code(input_data):
    chat = input_data["chat"]
    formatted_chat = "\n".join([f"{msg['role'].capitalize()}: {msg['message']}" for msg in chat])
    return {"formatted_chat": formatted_chat}


input_phase_1 = InputPhase(
    input_data={},
    input_schema=input_schema_1,
    output_schema=output_schema_1,
    code=input_phase_1_code
)

# GenerativePhase: Use the LLM to summarize the formatted chat
input_schema_generation = {"formatted_chat": str}
output_schema_generation = {"summary": str}

generative_phase_1 = GenerativePhase(
    input_data={},
    generative_function=lambda input_data: get_chat_completions_response(
        message_history=[],
        system_content="You are a helpful assistant summarizing chat conversations. RETURN A JSON with a 'summary' "
                       "attribute and with the value being the summary.",
        user_content=input_data["formatted_chat"],
        username="summarizer_agent",
        ai_client=openai_client,
        load_json=True
    ),
    input_schema=input_schema_generation,
    output_schema=output_schema_generation
)

# OutputPhase: Postprocess the summary into a user-friendly output
input_schema_2 = {"summary": str}
output_schema_2 = {"final_summary": str}


def output_phase_1_code(input_data):
    return {"final_summary": f"Chat Summary: \n{input_data['summary']}"}


output_phase_1 = OutputPhase(
    input_data={},
    input_schema=input_schema_2,
    output_schema=output_schema_2,
    code=output_phase_1_code
)

# Define the GenerativeNode
tool_node_1 = GenerativeTool(
    input_phase=input_phase_1,
    generative_phase=generative_phase_1,
    output_phase=output_phase_1,
    input_schema=input_schema_1,
    output_schema=output_schema_2
)

# Define the Agent
chat_summarizer = SerialPipeline(
    name="ChatSummarizer",
    nodes=[tool_node_1],
    description="Generates concise summaries of chat conversations, capturing key points and important "
                "exchanges to improve readability and understanding."
)


# Execute the Agent
def summarize_chat(chats):
    final_chat_output = chat_summarizer.execute({"chat": chats})
    return final_chat_output


if __name__ == "__main__":
    # This will execute when the script is run directly
    final_output = summarize_chat(chat_messages)
    print("Final Output:", final_output)
