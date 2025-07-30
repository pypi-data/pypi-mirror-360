import json
import re
from typing import List, Dict, Any, Optional

import tiktoken


class TokenEstimator:
    """Generic token estimation for various AI models and providers."""

    # Model configurations - covers all your MODEL_TOKEN_LEN models
    MODEL_CONFIGS = {
        # OpenAI GPT-3.5 Models
        'gpt-3.5-turbo': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                          'conv_overhead': 2},
        'gpt-3.5-turbo-0125': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                               'conv_overhead': 2},
        'gpt-3.5-turbo-0301': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                               'conv_overhead': 2},
        'gpt-3.5-turbo-0613': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                               'conv_overhead': 2},
        'gpt-3.5-turbo-1106': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                               'conv_overhead': 2},
        'gpt-3.5-turbo-16k': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                              'conv_overhead': 2},
        'gpt-3.5-turbo-16k-0613': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                                   'conv_overhead': 2},

        # OpenAI GPT-4 Models
        'gpt-4': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                  'conv_overhead': 2},
        'gpt-4-0125-preview': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                               'conv_overhead': 2},
        'gpt-4-0314': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                       'conv_overhead': 2},
        'gpt-4-0613': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                       'conv_overhead': 2},
        'gpt-4-1106-preview': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                               'conv_overhead': 2},
        'gpt-4-1106-vision-preview': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base',
                                      'msg_overhead': 4, 'conv_overhead': 2, 'has_vision': True},
        'gpt-4-32k': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                      'conv_overhead': 2},
        'gpt-4-32k-0314': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                           'conv_overhead': 2},
        'gpt-4-32k-0613': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                           'conv_overhead': 2},
        'gpt-4-turbo-preview': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                                'conv_overhead': 2},
        'gpt-4-vision-preview': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                                 'conv_overhead': 2, 'has_vision': True},

        # Newer OpenAI models
        'gpt-4-turbo': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'cl100k_base', 'msg_overhead': 4,
                        'conv_overhead': 2},
        'gpt-4o': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'o200k_base', 'msg_overhead': 4,
                   'conv_overhead': 2, 'has_vision': True},
        'gpt-4o-mini': {'provider': 'openai_interface', 'type': 'chat', 'encoding': 'o200k_base', 'msg_overhead': 4,
                        'conv_overhead': 2, 'has_vision': True},

        # Legacy completion models
        'text-davinci-003': {'provider': 'openai_interface', 'type': 'completion', 'encoding': 'p50k_base', 'msg_overhead': 0,
                             'conv_overhead': 0},

        # Anthropic Models (approximate)
        'claude-3-opus': {'provider': 'anthropic_interface', 'type': 'chat', 'chars_per_token': 3.5, 'msg_overhead': 3,
                          'conv_overhead': 5},
        'claude-3-sonnet': {'provider': 'anthropic_interface', 'type': 'chat', 'chars_per_token': 3.5, 'msg_overhead': 3,
                            'conv_overhead': 5},
        'claude-3-haiku': {'provider': 'anthropic_interface', 'type': 'chat', 'chars_per_token': 3.5, 'msg_overhead': 3,
                           'conv_overhead': 5},
        'claude-3.5-sonnet': {'provider': 'anthropic_interface', 'type': 'chat', 'chars_per_token': 3.5, 'msg_overhead': 3,
                              'conv_overhead': 5},

        # Generic fallback
        'generic': {'provider': 'generic', 'type': 'chat', 'chars_per_token': 4.0, 'msg_overhead': 3,
                    'conv_overhead': 5},
    }

    @classmethod
    def estimate_tokens(cls, message_history: List[Dict[str, Any]], model: Optional[str] = None) -> int:
        """
        Estimate total tokens for a message history with any model.

        Args:
            message_history: List of message dicts with 'content' and optionally 'role'
            model: Model name (e.g. 'gpt-4o', 'claude-3-sonnet-20240229')

        Returns:
            int: Estimated token count, or -1 if estimation failed
        """
        if not message_history:
            return 0

        try:
            config = cls._get_model_config(model)

            if config['provider'] == 'openai_interface' and 'encoding' in config:
                return cls._estimate_openai_tokens(message_history, config)
            else:
                return cls._estimate_generic_tokens(message_history, config)

        except Exception as e:
            # Fallback to generic estimation
            try:
                generic_config = cls.MODEL_CONFIGS['generic']
                return cls._estimate_generic_tokens(message_history, generic_config)
            except:
                return -1

    @classmethod
    def _get_model_config(cls, model: Optional[str]) -> Dict[str, Any]:
        """Get configuration for a model, with fuzzy matching."""
        if not model:
            return cls.MODEL_CONFIGS['generic']

        # Exact match
        if model in cls.MODEL_CONFIGS:
            return cls.MODEL_CONFIGS[model]

        # Fuzzy matching for versioned models
        model_lower = model.lower()
        for config_model, config in cls.MODEL_CONFIGS.items():
            if config_model != 'generic' and model_lower.startswith(config_model.lower()):
                return config

        # Check for provider-specific patterns
        if 'gpt' in model_lower:
            if 'gpt-4' in model_lower:
                if 'turbo' in model_lower:
                    return cls.MODEL_CONFIGS['gpt-4-turbo']
                return cls.MODEL_CONFIGS['gpt-4']
            elif 'gpt-3.5' in model_lower:
                return cls.MODEL_CONFIGS['gpt-3.5-turbo']
        elif 'claude' in model_lower:
            if 'opus' in model_lower:
                return cls.MODEL_CONFIGS['claude-3-opus']
            elif 'sonnet' in model_lower:
                return cls.MODEL_CONFIGS['claude-3.5-sonnet']
            elif 'haiku' in model_lower:
                return cls.MODEL_CONFIGS['claude-3-haiku']
            else:
                return cls.MODEL_CONFIGS['claude-3-sonnet']  # Default Claude

        # Fallback to generic
        return cls.MODEL_CONFIGS['generic']

    @classmethod
    def _estimate_openai_tokens(cls, message_history: List[Dict], config: Dict) -> int:
        """Estimate tokens using tiktoken for OpenAI models."""
        try:
            encoding = tiktoken.get_encoding(config['encoding'])
        except:
            encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')  # Fallback

        total_tokens = 0

        for message in message_history:
            # Message overhead
            total_tokens += config.get('msg_overhead', 4)

            # Role tokens
            role = message.get('role', '')
            if role:
                total_tokens += len(encoding.encode(role))

            # Content tokens
            content = message.get('content', '')
            if isinstance(content, str):
                total_tokens += len(encoding.encode(content))
            elif isinstance(content, list):
                # Multimodal content
                for item in content:
                    if item.get('type') == 'text':
                        text = item.get('text', '')
                        total_tokens += len(encoding.encode(text))
                    elif item.get('type') == 'image_url':
                        # Rough estimate for images
                        total_tokens += 765
            else:
                total_tokens += len(encoding.encode(str(content)))

        # Conversation overhead
        total_tokens += config.get('conv_overhead', 2)
        return total_tokens

    @classmethod
    def _estimate_generic_tokens(cls, message_history: List[Dict], config: Dict) -> int:
        """Estimate tokens using character-based heuristics."""
        total_tokens = 0
        chars_per_token = config.get('chars_per_token', 4.0)

        for message in message_history:
            # Message overhead
            total_tokens += config.get('msg_overhead', 3)

            # Role tokens
            role = message.get('role', '')
            if role:
                total_tokens += len(role) / chars_per_token

            # Content tokens
            content = message.get('content', '')
            if isinstance(content, str):
                total_tokens += len(content) / chars_per_token
            elif isinstance(content, list):
                # Multimodal content
                for item in content:
                    if item.get('type') == 'text':
                        text = item.get('text', '')
                        total_tokens += len(text) / chars_per_token
                    elif item.get('type') == 'image_url':
                        # Rough estimate for images
                        total_tokens += 500
            else:
                total_tokens += len(str(content)) / chars_per_token

        # Conversation overhead
        total_tokens += config.get('conv_overhead', 5)
        return int(total_tokens)

    @classmethod
    def get_context_limit(cls, model: str) -> Optional[int]:
        """Get context limit for a model based on your MODEL_TOKEN_LEN."""
        # Complete mapping from your MODEL_TOKEN_LEN
        context_limits = {
            # GPT-3.5 models
            "gpt-3.5-turbo": 16385,
            "gpt-3.5-turbo-0125": 16385,
            "gpt-3.5-turbo-0301": 4097,
            "gpt-3.5-turbo-0613": 4097,
            "gpt-3.5-turbo-1106": 16385,
            "gpt-3.5-turbo-16k": 16385,
            "gpt-3.5-turbo-16k-0613": 16385,

            # GPT-4 models
            "gpt-4": 8192,
            "gpt-4-0125-preview": 128000,
            "gpt-4-0314": 8192,
            "gpt-4-0613": 8192,
            "gpt-4-1106-preview": 128000,
            "gpt-4-1106-vision-preview": 128000,
            "gpt-4-32k": 32768,
            "gpt-4-32k-0314": 32768,
            "gpt-4-32k-0613": 32768,
            "gpt-4-turbo-preview": 128000,
            "gpt-4-vision-preview": 128000,

            # Newer models (common ones)
            "gpt-4-turbo": 128000,
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,

            # Claude models
            'claude-3-opus': 200000,
            'claude-3-sonnet': 200000,
            'claude-3-haiku': 200000,
            'claude-3.5-sonnet': 200000,
        }

        # Exact match first
        if model in context_limits:
            return context_limits[model]

        # Fuzzy matching for versioned models
        model_lower = model.lower()
        for limit_model, limit in context_limits.items():
            if model_lower.startswith(limit_model.lower()):
                return limit

        return None


# Convenience functions for backward compatibility
def estimate_tokens(message_history: List[Dict[str, Any]], model: Optional[str] = None) -> int:
    """Convenience function matching your original API."""
    return TokenEstimator.estimate_tokens(message_history, model)


def remove_oldest_message_until_within_limit(message_history: List[Dict], n: int, max_len: int,
                                             model: Optional[str] = None):
    """Remove oldest messages until within token limit."""
    while len(message_history) > n:
        current_tokens = estimate_tokens(message_history, model)
        if current_tokens <= max_len or current_tokens == -1:
            break
        message_history.pop(n)


def extract_and_parse_output(obj):
    """
    If obj has an 'output' key:
      - if obj['output'] is a JSON string (optionally wrapped in ```json code fences), parse it.
      - if obj['output'] is already a dict, leave as-is.
    Returns the obj with 'output' replaced by the parsed dict (if needed).
    If no 'output' key, returns obj unchanged.
    """
    if not isinstance(obj, str) or (isinstance(obj, dict) and 'output' not in obj):
        return obj

    output = obj
    if isinstance(obj, dict) and obj.get('output'):
        output = obj.get('output')


    if isinstance(output, dict):
        return obj  # already parsed

    if isinstance(output, str):
        # Remove code fences if present
        code_fence_pattern = r"^```(?:json)?\s*(.*?)```$"
        match = re.match(code_fence_pattern, output.strip(), re.DOTALL | re.IGNORECASE)
        json_str = match.group(1).strip() if match else output.strip()

        try:
            obj = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in 'output': {e}")

    return obj


# Test Suite
def run_tests():
    """Comprehensive test suite for the token estimator."""
    print("🧪 Running Token Estimator Tests\n")

    # Test data
    simple_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you for asking!"}
    ]

    multimodal_messages = [
        {"role": "user", "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
        ]}
    ]

    long_message = [
        {"role": "user", "content": "This is a very long message. " * 100}
    ]

    # Test different models - now includes all your MODEL_TOKEN_LEN models
    test_models = [
        'gpt-4o',
        'gpt-4-turbo-2024-04-09',
        'gpt-3.5-turbo',
        'gpt-3.5-turbo-0125',
        'gpt-3.5-turbo-16k',
        'gpt-4',
        'gpt-4-0613',
        'gpt-4-32k',
        'gpt-4-1106-preview',
        'gpt-4-vision-preview',
        'claude-3-sonnet-20240229',
        'claude-3.5-sonnet-20241022',
        'unknown-model-2024',
        None
    ]

    print("📊 Testing different models with simple messages:")
    print("-" * 60)
    for model in test_models:
        tokens = estimate_tokens(simple_messages, model)
        context_limit = TokenEstimator.get_context_limit(model) if model else "Unknown"
        print(f"{model or 'None (generic)':<30} | Tokens: {tokens:>6} | Limit: {context_limit}")

    print(f"\n🖼️  Testing multimodal content (GPT-4):")
    print("-" * 40)
    tokens = estimate_tokens(multimodal_messages, 'gpt-4o')
    print(f"Multimodal message tokens: {tokens}")

    print(f"\n📏 Testing long content:")
    print("-" * 25)
    for model in ['gpt-4o', 'claude-3-sonnet', None]:
        tokens = estimate_tokens(long_message, model)
        print(f"{model or 'generic':<15} | Long message tokens: {tokens}")

    print(f"\n🔄 Testing message trimming:")
    print("-" * 30)
    # Create a long conversation
    long_conversation = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    for i in range(10):
        long_conversation.extend([
            {"role": "user", "content": f"This is message {i} with some content that takes up tokens."},
            {"role": "assistant", "content": f"This is response {i} with helpful information."}
        ])

    original_length = len(long_conversation)
    original_tokens = estimate_tokens(long_conversation, 'gpt-4o')

    # Trim to 1000 tokens, keeping first 3 messages
    remove_oldest_message_until_within_limit(long_conversation, n=3, max_len=1000, model='gpt-4o')

    final_length = len(long_conversation)
    final_tokens = estimate_tokens(long_conversation, 'gpt-4o')

    print(f"Original: {original_length} messages, {original_tokens} tokens")
    print(f"Trimmed:  {final_length} messages, {final_tokens} tokens")

    print(f"\n✅ All tests completed!")

    # Edge cases
    print(f"\n🔍 Testing edge cases:")
    print("-" * 25)
    print(f"Empty history: {estimate_tokens([], 'gpt-4o')} tokens")
    print(f"No model specified: {estimate_tokens(simple_messages)} tokens")
    print(f"Invalid model: {estimate_tokens(simple_messages, 'invalid-model-xyz')} tokens")


if __name__ == "__main__":
    run_tests()