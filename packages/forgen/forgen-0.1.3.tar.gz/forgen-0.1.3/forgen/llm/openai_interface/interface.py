import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from forgen.llm.openai_interface import MODEL_TOKEN_LEN
from forgen.llm.util import estimate_tokens
from forgen.prompt.core_prompt import get_drawing_summary_prompt, get_summary_of_images_text_with_prompt


load_dotenv()
_openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LARGE_MSG_GEN_MODEL = os.environ.get("LARGE_MSG_GEN_MODEL", "gpt-4o")
LARGE_MODEL_TOKEN_MAX_LEN = MODEL_TOKEN_LEN.get(LARGE_MSG_GEN_MODEL, {"max_in": 128000}).get("max_in", 128000)

MSG_GEN_MODEL = os.environ.get("MSG_GEN_MODEL", "gpt-4o")
MODEL_TOKEN_MAX_LEN = MODEL_TOKEN_LEN.get(MSG_GEN_MODEL, {"max_in": 128000}).get("max_in", 128000)


def get_num_tokens(response):
    """Extract token usage from OpenAI response."""
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens
    return input_tokens, output_tokens, total_tokens


def get_openai_chat_message_with_event(message_history, system_content, user_content, event, response_obj,
                                       username, increment_usage):
    """Async wrapper for chat message generation with event signaling."""
    print("enhance_prompt")
    response = get_chat_message(message_history, system_content, user_content, username,
                               increment_usage=increment_usage)
    print(f"enhance_prompt response: {response}")
    response_obj = response
    event.set()
    print(f"enhance_prompt event set")


def get_chat_json(message_history, system_content, user_content, username, images=[], increment_usage=None,
                  load_json=False, ai_client=None):
    """Get JSON response from OpenAI chat completions."""
    return get_chat_completions_response(
        message_history, system_content, user_content, images=images,
        username=username, increment_usage=increment_usage, json_response=True,
        load_json=load_json, temp=0.4, ai_client=ai_client
    )


def get_chat_message(message_history, system_content, user_content, username, increment_usage, images=[],
                     ai_client=None):
    """Get text response from OpenAI chat completions."""
    return get_chat_completions_response(
        message_history, system_content, user_content, images=images,
        username=username, increment_usage=increment_usage, json_response=False,
        temp=0.5, ai_client=ai_client
    )


def get_chat_completions_response(
        message_history=None, system_content="", user_content="", images=None,
        username=None, increment_usage=None, json_response=False, load_json=False,
        temp=0.3, ai_client=None
):
    """
    Generate chat completions using the OpenAI API.
    Returns standardized dict for GenerativePhase compatibility.

    Args:
        message_history: List of message dicts for conversation context
        system_content: System prompt content
        user_content: User message content
        images: List of image URLs or base64 strings
        username: Username for usage tracking
        increment_usage: Function to track token usage
        json_response: Whether to request JSON format response
        load_json: Whether to parse response as JSON
        temp: Temperature for response generation
        ai_client: Custom OpenAI client instance

    Returns:
        Dict with 'output', 'input_tokens', 'output_tokens', 'total_tokens'
    """
    if message_history is None:
        message_history = []
    if images is None:
        images = []

    ai_client = ai_client or _openai_client

    # Create a copy to avoid modifying the original
    working_history = message_history.copy()
    working_history.append({"role": "system", "content": str(system_content)})

    cur_model = MSG_GEN_MODEL

    # Check if we need to use the larger model due to token limits
    if estimate_tokens(working_history) > MODEL_TOKEN_MAX_LEN:
        if images:
            # Summarize images if present to reduce token usage
            summary_response = get_chat_message(
                [], get_drawing_summary_prompt(), user_content, username,
                images=images, increment_usage=increment_usage
            )

            # Handle both dict and string responses from summarization
            if isinstance(summary_response, dict):
                summary = summary_response.get('output', str(summary_response))
            else:
                summary = str(summary_response)

            user_content += get_summary_of_images_text_with_prompt(summary)

        cur_model = LARGE_MSG_GEN_MODEL

    # Prepare message content with images
    if images:
        message_content = [{"type": "text", "text": user_content}] if user_content else []
        for image in images:
            if not image:
                continue
            if not image.startswith("http"):
                image = f"data:image/jpeg;base64,{image}"
            message_content.append({"type": "image_url", "image_url": {"url": image}})
        working_history.append({"role": "user", "content": message_content})
    else:
        working_history.append({"role": "user", "content": user_content})

    # Prepare API parameters
    api_params = {
        "model": cur_model,
        "messages": working_history,
        "temperature": temp
    }

    if json_response or load_json:
        api_params["response_format"] = {"type": "json_object"}

    try:
        response = ai_client.chat.completions.create(**api_params)
        ai_message = response.choices[0].message.content.strip()

        # Token tracking
        input_tokens, output_tokens, total_tokens = get_num_tokens(response)
        if increment_usage and username:
            increment_usage(username, cur_model, input_tokens, output_tokens, total_tokens)

        # Return standardized response
        return {
            "output": ai_message if not (json_response or load_json) else json.loads(ai_message),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }

    except Exception as e:
        return {
            "output": f"[GENERATION ERROR] {str(e)}",
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None
        }