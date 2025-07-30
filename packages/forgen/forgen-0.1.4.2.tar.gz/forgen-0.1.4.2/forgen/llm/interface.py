import os
from typing import List, Dict, Optional, Union, Callable, Any

from dotenv import load_dotenv
from openai import OpenAI
import anthropic

from forgen.llm.openai_interface import MODEL_TOKEN_LEN as OPENAI_MODEL_TOKEN_LEN
from forgen.llm.openai_interface import DEFAULT_MODEL as OPENAI_DEFAULT_MODEL
from forgen.llm.anthropic_interface import MODEL_TOKEN_LEN as ANTHROPIC_MODEL_TOKEN_LEN
from forgen.llm.anthropic_interface import DEFAULT_MODEL as ANTHROPIC_DEFAULT_MODEL

# Load environment variables
load_dotenv()

# Combined model token limits
MODEL_TOKEN_LEN = {**OPENAI_MODEL_TOKEN_LEN, **ANTHROPIC_MODEL_TOKEN_LEN}

# Default models
use_anthropic_as_default = os.getenv("USE_ANTHROPIC_FOR_TOOL_DEFAULT", False)
DEFAULT_MODEL = ANTHROPIC_DEFAULT_MODEL if use_anthropic_as_default else OPENAI_DEFAULT_MODEL
DEFAULT_MSG_GEN_MODEL = os.environ.get("MSG_GEN_MODEL", DEFAULT_MODEL)
DEFAULT_LARGE_MSG_GEN_MODEL = os.environ.get("LARGE_MSG_GEN_MODEL", DEFAULT_MODEL)

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

DEFAULT_CLIENT = anthropic_client if use_anthropic_as_default else openai_client

def get_provider_from_model(model_name: str) -> str:
    """Determine the provider based on model name."""
    if model_name.startswith("gpt-") or model_name.startswith("o1-"):
        return "openai_interface"
    elif model_name.startswith("claude-"):
        return "anthropic_interface"
    else:
        # Default fallback - could be made configurable
        return "anthropic_interface"


def get_interface_module(provider: str):
    """Import and return the appropriate interface module."""
    if provider == "openai_interface":
        from forgen.llm.openai_interface import interface as openai_interface
        return openai_interface
    elif provider == "anthropic_interface":
        from forgen.llm.anthropic_interface import interface as anthropic_interface
        return anthropic_interface
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_client_for_provider(provider: str):
    """Get the appropriate client for the provider."""
    if provider == "openai_interface":
        return openai_client
    elif provider == "anthropic_interface":
        return anthropic_client
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_chat_completions_response(
        message_history: Optional[List[Dict]] = None,
        system_content: str = "",
        user_content: str = "",
        images: Optional[List[str]] = None,
        username: Optional[str] = None,
        increment_usage: Optional[Callable] = None,
        json_response: bool = False,
        load_json: bool = False,
        temp: float = 0.3,
        ai_client: Optional[Any] = None,
        model: Optional[str] = None
) -> Dict[str, Union[str, int, None]]:
    """
    Generate chat completions using the appropriate provider based on model.

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
        ai_client: Custom client instance (if None, uses default for provider)
        model: Model name to use (overrides default)

    Returns:
        Dict with 'output', 'input_tokens', 'output_tokens', 'total_tokens'
    """
    # Use provided model or default
    target_model = model or DEFAULT_MSG_GEN_MODEL
    provider = get_provider_from_model(target_model)
    interface_module = get_interface_module(provider)

    # Use provided client or get default for provider
    target_client = ai_client or get_client_for_provider(provider)

    return interface_module.get_chat_completions_response(
        message_history=message_history,
        system_content=system_content,
        user_content=user_content,
        images=images,
        username=username,
        increment_usage=increment_usage,
        json_response=json_response,
        load_json=load_json,
        temp=temp,
        ai_client=target_client
    )


def get_chat_message(
        message_history: List[Dict],
        system_content: str,
        user_content: str,
        username: str,
        increment_usage: Callable,
        images: Optional[List[str]] = None,
        ai_client: Optional[Any] = None,
        model: Optional[str] = None
) -> Dict[str, Union[str, int, None]]:
    """
    Get text response from chat completions using the appropriate provider.

    Args:
        message_history: List of message dicts for conversation context
        system_content: System prompt content
        user_content: User message content
        username: Username for usage tracking
        increment_usage: Function to track token usage
        images: List of image URLs or base64 strings
        ai_client: Custom client instance (if None, uses default for provider)
        model: Model name to use (overrides default)

    Returns:
        Dict with 'output', 'input_tokens', 'output_tokens', 'total_tokens'
    """
    if images is None:
        images = []

    # Use provided model or default
    target_model = model or DEFAULT_MSG_GEN_MODEL
    provider = get_provider_from_model(target_model)
    interface_module = get_interface_module(provider)

    # Use provided client or get default for provider
    target_client = ai_client or get_client_for_provider(provider)

    return interface_module.get_chat_message(
        message_history=message_history,
        system_content=system_content,
        user_content=user_content,
        username=username,
        increment_usage=increment_usage,
        images=images,
        ai_client=target_client
    )


def get_chat_json(
        message_history: List[Dict],
        system_content: str,
        user_content: str,
        username: str,
        images: Optional[List[str]] = None,
        increment_usage: Optional[Callable] = None,
        load_json: bool = False,
        ai_client: Optional[Any] = None,
        model: Optional[str] = None
) -> Dict[str, Union[str, int, None]]:
    """
    Get JSON response from chat completions using the appropriate provider.

    Args:
        message_history: List of message dicts for conversation context
        system_content: System prompt content
        user_content: User message content
        username: Username for usage tracking
        images: List of image URLs or base64 strings
        increment_usage: Function to track token usage
        load_json: Whether to parse response as JSON
        ai_client: Custom client instance (if None, uses default for provider)
        model: Model name to use (overrides default)

    Returns:
        Dict with 'output', 'input_tokens', 'output_tokens', 'total_tokens'
    """
    if images is None:
        images = []

    # Use provided model or default
    target_model = model or DEFAULT_MSG_GEN_MODEL
    provider = get_provider_from_model(target_model)
    interface_module = get_interface_module(provider)

    # Use provided client or get default for provider
    target_client = ai_client or get_client_for_provider(provider)

    return interface_module.get_chat_json(
        message_history=message_history,
        system_content=system_content,
        user_content=user_content,
        username=username,
        images=images,
        increment_usage=increment_usage,
        load_json=load_json,
        ai_client=target_client
    )


def get_chat_message_with_event(
        message_history: List[Dict],
        system_content: str,
        user_content: str,
        event: Any,
        response_obj: Any,
        username: str,
        increment_usage: Callable,
        model: Optional[str] = None
):
    """
    Async wrapper for chat message generation with event signaling.

    Args:
        message_history: List of message dicts for conversation context
        system_content: System prompt content
        user_content: User message content
        event: Event object to signal completion
        response_obj: Object to store response
        username: Username for usage tracking
        increment_usage: Function to track token usage
        model: Model name to use (overrides default)
    """
    # Use provided model or default
    target_model = model or DEFAULT_MSG_GEN_MODEL
    provider = get_provider_from_model(target_model)
    interface_module = get_interface_module(provider)

    # Get default client for provider
    target_client = get_client_for_provider(provider)

    return interface_module.get_chat_message_with_event(
        message_history=message_history,
        system_content=system_content,
        user_content=user_content,
        event=event,
        response_obj=response_obj,
        username=username,
        increment_usage=increment_usage,
        ai_client=target_client
    )


def remove_oldest_message_until_within_limit(
        message_history: List[Dict],
        n: int,
        max_len: int
):
    """
    Remove the oldest messages (beyond the first n) until within max token length.
    This function works the same for both providers.

    Args:
        message_history: List of message dicts
        n: Number of messages to preserve at the beginning
        max_len: Maximum token length allowed
    """
    # Import utility function
    from forgen.llm.util import estimate_tokens

    token_length = estimate_tokens(message_history)
    while token_length > max_len:
        if len(message_history) > n:
            message_history.pop(n)
            token_length = estimate_tokens(message_history)
            if token_length == -1:
                break
        else:
            break


def get_model_token_limits(model_name: str) -> Dict[str, int]:
    """
    Get token limits for a given model.

    Args:
        model_name: Name of the model

    Returns:
        Dict with 'max_in' and 'max_out' token limits
    """
    return MODEL_TOKEN_LEN.get(model_name, {"max_in": 200000, "max_out": 8192})


def list_available_models() -> Dict[str, List[str]]:
    """
    List all available models by provider.

    Returns:
        Dict with provider names as keys and lists of model names as values
    """
    openai_models = [model for model in MODEL_TOKEN_LEN.keys() if model.startswith(("gpt-", "o1-"))]
    anthropic_models = [model for model in MODEL_TOKEN_LEN.keys() if model.startswith("claude-")]

    return {
        "openai_interface": openai_models,
        "anthropic_interface": anthropic_models
    }


def get_clients() -> Dict[str, Any]:
    """
    Get all initialized clients.

    Returns:
        Dict with provider names as keys and client instances as values
    """
    return {
        "openai_interface": openai_client,
        "anthropic_interface": anthropic_client
    }