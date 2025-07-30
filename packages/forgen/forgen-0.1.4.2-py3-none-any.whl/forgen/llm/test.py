from forgen.llm.interface import (
    get_chat_message,
    list_available_models,
)

def dummy_increment_usage(*args, **kwargs):
    print("[INFO] Dummy increment_usage called.")

def test_provider(model_name: str):
    print(f"\n=== Testing model: {model_name} ===")
    message_history = []
    system_content = "You are a helpful assistant."
    user_content = "What is 2 + 2?"
    username = "test_user"

    response = get_chat_message(
        message_history=message_history,
        system_content=system_content,
        user_content=user_content,
        username=username,
        increment_usage=dummy_increment_usage,
        model=model_name,
    )
    print(f"[RESULT] Response for {model_name}: {response}")

def main():
    print("Available models:")
    models = list_available_models()
    for provider, model_list in models.items():
        print(f"- {provider}:")
        for model in model_list:
            print(f"  - {model}")

    print("\nRunning tests for OpenAI and Anthropic providers:")

    # Pick one OpenAI and one Anthropic model to test
    openai_models = models.get("openai_interface", [])
    anthropic_models = models.get("anthropic_interface", [])

    if openai_models:
        test_provider(openai_models[0])
    else:
        print("[WARNING] No OpenAI models found!")

    if anthropic_models:
        test_provider(anthropic_models[0])
    else:
        print("[WARNING] No Anthropic models found!")

if __name__ == "__main__":
    main()
