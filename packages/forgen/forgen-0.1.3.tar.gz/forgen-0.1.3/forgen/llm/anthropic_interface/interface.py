import json
import os

import anthropic
from dotenv import load_dotenv

from forgen.llm.anthropic_interface import MODEL_TOKEN_LEN
from forgen.llm.util import estimate_tokens, extract_and_parse_output
from forgen.prompt.core_prompt import get_drawing_summary_prompt, get_summary_of_images_text_with_prompt

load_dotenv()
_claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

LARGE_MSG_GEN_MODEL = os.environ.get("LARGE_MSG_GEN_MODEL", "claude-4-sonnet-20250514")
LARGE_MODEL_TOKEN_MAX_LEN = MODEL_TOKEN_LEN.get(LARGE_MSG_GEN_MODEL, {"max_in": 200000}).get("max_in", 200000)

MSG_GEN_MODEL = os.environ.get("MSG_GEN_MODEL", "claude-4-sonnet-20250514")
MODEL_TOKEN_MAX_LEN = MODEL_TOKEN_LEN.get(MSG_GEN_MODEL, {"max_in": 200000}).get("max_in", 200000)


def get_num_tokens(response):
    """Extract token usage from Claude response."""
    if not hasattr(response, 'usage') or not response.usage:
        return 0, 0, 0

    usage = response.usage
    input_tokens = getattr(usage, 'input_tokens', 0) or 0
    output_tokens = getattr(usage, 'output_tokens', 0) or 0
    total_tokens = input_tokens + output_tokens
    return input_tokens, output_tokens, total_tokens


def get_chat_message_with_event(message_history, system_content, user_content, event, response_obj,
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
    """Get JSON response from Claude chat completions."""
    return get_chat_completions_response(
        message_history, system_content, user_content, images=images,
        username=username, increment_usage=increment_usage, json_response=True,
        load_json=load_json, temp=0.4, ai_client=ai_client
    )


def get_chat_message(message_history, system_content, user_content, username, increment_usage, images=[],
                     ai_client=None):
    """Get text response from Claude chat completions."""
    return get_chat_completions_response(
        message_history, system_content, user_content, images=images,
        username=username, increment_usage=increment_usage, json_response=False,
        temp=0.5, ai_client=ai_client
    )


def _process_image_for_claude(image):
    """Process image for Claude API format."""
    if image.startswith("http"):
        # For HTTP URLs, we'd need to download and convert
        # For now, return None to skip HTTP images
        return None

    # Handle base64 images
    if image.startswith("data:image/"):
        # Extract base64 data
        header, data = image.split(",", 1)
        media_type = header.split(":")[1].split(";")[0]
    else:
        # Assume it's raw base64
        data = image
        media_type = "image/jpeg"  # Default assumption

    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": data
        }
    }


def _convert_messages_for_claude(message_history):
    """Convert OpenAI-style messages to Claude format."""
    claude_messages = []
    system_content = ""

    for message in message_history:
        role = message.get("role", "")
        content = message.get("content", "")

        if role == "system":
            # Claude handles system messages separately
            system_content += str(content) + "\n"
            continue
        elif role == "user":
            claude_role = "user"
        elif role == "assistant":
            claude_role = "assistant"
        else:
            continue  # Skip unknown roles

        # Handle multimodal content
        if isinstance(content, list):
            claude_content = []
            for item in content:
                if item.get("type") == "text":
                    claude_content.append({
                        "type": "text",
                        "text": item.get("text", "")
                    })
                elif item.get("type") == "image_url":
                    image_url = item.get("image_url", {}).get("url", "")
                    processed_image = _process_image_for_claude(image_url)
                    if processed_image:
                        claude_content.append(processed_image)

            claude_messages.append({
                "role": claude_role,
                "content": claude_content if claude_content else [{"type": "text", "text": str(content)}]
            })
        else:
            # Simple text content
            claude_messages.append({
                "role": claude_role,
                "content": str(content)
            })

    return claude_messages, system_content.strip()


def get_chat_completions_response(
        message_history=None, system_content="", user_content="", images=None,
        username=None, increment_usage=None, json_response=False, load_json=False,
        temp=0.3, ai_client=None
):
    """
    Generate chat completions using the Claude API.
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
        ai_client: Custom Claude client instance

    Returns:
        Dict with 'output', 'input_tokens', 'output_tokens', 'total_tokens'
    """
    if message_history is None:
        message_history = []
    if images is None:
        images = []

    ai_client = ai_client or _claude_client

    # Create a copy to avoid modifying the original
    working_history = message_history.copy()

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

    # Prepare user message with images
    if images:
        user_message_content = []
        if user_content:
            user_message_content.append({"type": "text", "text": user_content})

        for image in images:
            if not image:
                continue
            processed_image = _process_image_for_claude(image)
            if processed_image:
                user_message_content.append(processed_image)

        working_history.append({"role": "user", "content": user_message_content})
    else:
        working_history.append({"role": "user", "content": user_content})

    # Convert to Claude format
    claude_messages, extracted_system = _convert_messages_for_claude(working_history)

    # Combine system prompts
    full_system = ""
    if system_content:
        full_system += str(system_content)
    if extracted_system:
        if full_system:
            full_system += "\n\n"
        full_system += extracted_system

    # Prepare API parameters
    api_params = {
        "model": cur_model,
        "messages": claude_messages,
        "temperature": temp,
        "max_tokens": 64000
    }

    if full_system:
        api_params["system"] = full_system

    # Add JSON instruction for Claude
    if json_response or load_json:
        json_instruction = "\n\nPlease respond with valid JSON only."
        if "system" in api_params:
            api_params["system"] += json_instruction
        else:
            api_params["system"] = json_instruction.strip()

    api_params["stream"] = True

    try:
        response_stream = ai_client.messages.create(**api_params)
        ai_message = ""
        final_response = None
        usage_data = None

        try:
            for chunk in response_stream:
                # Always save the latest chunk
                final_response = chunk

                # Handle different event types properly
                if hasattr(chunk, 'type'):
                    # For newer SDK versions with explicit event types
                    if chunk.type == "content_block_delta":
                        if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                            ai_message += chunk.delta.text
                    elif chunk.type == "message_delta":
                        if hasattr(chunk, 'usage'):
                            usage_data = chunk.usage
                    elif chunk.type == "message_stop":
                        # Final message event, may contain usage
                        if hasattr(chunk, 'usage'):
                            usage_data = chunk.usage
                else:
                    # Fallback for older SDK versions or different event structure
                    if hasattr(chunk, "delta") and chunk.delta:
                        if hasattr(chunk.delta, "text"):
                            ai_message += chunk.delta.text
                        elif isinstance(chunk.delta, dict) and chunk.delta.get("text"):
                            ai_message += chunk.delta["text"]

                    # Check for usage information
                    if hasattr(chunk, 'usage') and chunk.usage:
                        usage_data = chunk.usage

            if not ai_message and final_response is None:
                raise ValueError("No response chunks received from Claude API.")
            # Extract token usage - try multiple sources
            input_tokens = output_tokens = total_tokens = 0

            if usage_data:
                input_tokens = getattr(usage_data, 'input_tokens', 0) or 0
                output_tokens = getattr(usage_data, 'output_tokens', 0) or 0
                total_tokens = input_tokens + output_tokens
            elif final_response and hasattr(final_response, 'usage') and final_response.usage:
                try:
                    input_tokens, output_tokens, total_tokens = get_num_tokens(final_response)
                except (AttributeError, TypeError) as e:
                    print(f"Warning: Could not extract token usage: {e}")
                    input_tokens = output_tokens = total_tokens = 0
            else:
                # Fallback - estimate tokens if no usage data available
                print("Warning: No usage data found in streaming response")

            # Track usage
            if increment_usage and username:
                increment_usage(username, cur_model, input_tokens, output_tokens, total_tokens)

            # Handle JSON parsing
            if json_response or load_json:
                ai_message = extract_and_parse_output(ai_message)
            if not isinstance(ai_message, dict) and (json_response or load_json):
                try:
                    output_content = json.loads(ai_message)
                except json.JSONDecodeError:
                    output_content = ai_message

            output_content = ai_message
            return {
                "output": output_content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }

        except Exception as e:
            return {
                "output": f"[GENERATION ERROR] Streaming error: {str(e)}",
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None
            }

    except Exception as e:
        return {
            "output": f"[GENERATION ERROR] API error: {str(e)}",
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None
        }