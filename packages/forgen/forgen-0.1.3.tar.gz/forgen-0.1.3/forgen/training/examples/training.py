import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM

# Import the LoRATrainer class
# Assuming the class is in a file called lora_trainer.py
from forgen.training.trainers.lora import LoRATrainer

# Check for CUDA availability and set appropriate device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

if device == "cpu":
    print("Warning: Training on CPU will be very slow. Consider using a GPU.")

# Load a small sample dataset for testing
# Using a small public dataset - TinyStories for instruction fine-tuning
dataset = load_dataset("roneneldan/TinyStories", split="train[:100]")  # Just 100 examples for testing

# Prepare the dataset in the expected format
# TinyStories has a "text" column called "story"
if "text" not in dataset.column_names:
    dataset = dataset.map(lambda example: {"text": example["story"]})

# Open-source model that doesn't require authentication
model_name = "gpt2"  # Using a small model for quick testing

# For GPT-2, explicitly specify target modules
# These are the linear layers in the GPT-2 architecture where LoRA will be applied
target_modules = ["c_attn", "c_proj", "c_fc"]

# Run the trainer with basic settings
try:
    LoRATrainer.train(
        base_model_name=model_name,
        output_dir="./lora_gpt2_test",
        train_data=dataset,
        text_column="text",
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=target_modules,  # Explicitly specify target modules
        batch_size=4,
        micro_batch_size=2,
        num_epochs=1,  # Just 1 epoch for testing
        learning_rate=5e-4,
        max_length=256,
        logging_steps=1  # Log after each step for testing
    )

    print("Training completed successfully!")

    # After training, load the model for inference
    from peft import PeftModel

    # Load the base model and tokenizer
    base_model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Load the LoRA adapter weights
    model = PeftModel.from_pretrained(base_model, "./lora_gpt2_test")

    # Test the model with a simple generation
    if device == "cuda":  # Only try generation if on GPU to avoid slow processing
        prompt = "Once upon a time"
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        print(f"\nGenerating text from prompt: '{prompt}'")
        outputs = model.generate(
            **inputs,
            max_length=50,
            temperature=0.7,
            top_p=0.9,
            num_return_sequences=1
        )

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Generated text: {generated_text}")

except Exception as e:
    print(f"An error occurred during training: {e}")
    import traceback

    traceback.print_exc()  # Print the full traceback for better debugging
