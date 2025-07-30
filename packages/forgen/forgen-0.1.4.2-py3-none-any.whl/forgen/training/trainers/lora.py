import os
import json
from hashlib import sha256
import torch

from transformers import (
    PreTrainedModel,
    PreTrainedTokenizer,
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import (
    get_peft_model,
    LoraConfig,
    TaskType,
    prepare_model_for_kbit_training
)
from datasets import Dataset, load_dataset
from typing import Dict, List, Optional, Union, Any


class LoRATrainer:
    """
    Static class for LoRA fine-tuning of language models.
    """

    @staticmethod
    def train(
        # Model configuration
        base_model_name: str,
        output_dir: str,

        # Training data
        train_data: Union[Dataset, str, List[Dict[str, str]]],
        val_data: Optional[Union[Dataset, str, List[Dict[str, str]]]] = None,
        text_column: str = "text",

        # LoRA configuration
        r: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.05,
        target_modules: Optional[List[str]] = None,

        # Training parameters
        batch_size: int = 4,
        micro_batch_size: int = 1,
        num_epochs: int = 3,
        learning_rate: float = 3e-4,
        warmup_steps: int = 100,
        max_steps: Optional[int] = None,

        # Tokenizer parameters
        max_length: int = 512,

        # Quantization parameters (for QLoRA)
        use_4bit: bool = False,
        use_8bit: bool = False,
        double_quant: bool = True,
        quant_type: str = "nf4",

        # Additional training arguments
        gradient_accumulation_steps: Optional[int] = None,
        gradient_checkpointing: bool = True,
        mixed_precision: Optional[str] = "fp16",

        # Misc
        save_steps: int = 100,
        logging_steps: int = 10,
        eval_steps: Optional[int] = None,
        seed: int = 42
    ) -> None:
        """
        Train a model using LoRA fine-tuning.

        Args:
            base_model_name: Hugging Face model identifier or local path
            output_dir: Directory to save model outputs
            train_data: Training data as a Dataset, path to dataset, or list of dictionaries
            val_data: Validation data (optional)
            text_column: Column name in dataset containing the text
            r: LoRA attention dimension
            lora_alpha: LoRA alpha parameter
            lora_dropout: LoRA dropout value
            target_modules: List of modules to apply LoRA to (defaults to None for auto-detection)
            batch_size: Global batch size
            micro_batch_size: Batch size per device
            num_epochs: Number of training epochs
            learning_rate: Learning rate
            warmup_steps: Steps for LR warmup
            max_steps: Maximum number of training steps (overrides num_epochs if set)
            max_length: Maximum token length for inputs
            use_4bit: Whether to use 4-bit quantization (QLoRA)
            use_8bit: Whether to use 8-bit quantization
            double_quant: Whether to use double quantization (for QLoRA)
            quant_type: Quantization type ("nf4" or "fp4")
            gradient_accumulation_steps: Number of steps for gradient accumulation
            gradient_checkpointing: Whether to use gradient checkpointing
            mixed_precision: Mixed precision training type
            save_steps: Save checkpoint every X steps
            logging_steps: Log metrics every X steps
            eval_steps: Run evaluation every X steps
            seed: Random seed
        """
        # Set random seed
        torch.manual_seed(seed)

        # Calculate gradient accumulation steps if not provided
        if gradient_accumulation_steps is None:
            gradient_accumulation_steps = batch_size // micro_batch_size

        # Prepare model loading configuration
        model_kwargs = {"device_map": "auto", "trust_remote_code": True}

        # Configure quantization if requested
        if use_4bit or use_8bit:
            if use_4bit:
                from transformers import BitsAndBytesConfig
                compute_dtype = torch.bfloat16

                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=double_quant,
                    bnb_4bit_quant_type=quant_type,
                    bnb_4bit_compute_dtype=compute_dtype
                )
                model_kwargs["quantization_config"] = bnb_config
            elif use_8bit:
                model_kwargs["load_in_8bit"] = True

        print(f"Loading base model: {base_model_name}")
        model = AutoModelForCausalLM.from_pretrained(base_model_name, **model_kwargs)
        tokenizer = AutoTokenizer.from_pretrained(base_model_name)

        # Configure tokenizer padding and EOS token
        if tokenizer.pad_token is None:
            if tokenizer.eos_token is not None:
                tokenizer.pad_token = tokenizer.eos_token
            else:
                tokenizer.pad_token = tokenizer.eos_token = "</s>"

        # Enable gradient checkpointing if requested
        if gradient_checkpointing:
            model.gradient_checkpointing_enable()

        # Prepare model for k-bit training if using quantization
        if use_4bit or use_8bit:
            model = prepare_model_for_kbit_training(model)

        # Auto-detect target modules if not specified
        if target_modules is None:
            # Get the model type for architecture-specific module detection
            model_type = base_model_name.lower()

            if "gpt2" in model_type or "gpt-2" in model_type:
                target_modules = ["c_attn", "c_proj", "c_fc"]
                print(f"Detected GPT-2 architecture, using target modules: {target_modules}")
            elif "llama" in model_type or "vicuna" in model_type:
                target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
                print(f"Detected LLaMA-like architecture, using target modules: {target_modules}")
            elif "mistral" in model_type:
                target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
                print(f"Detected Mistral architecture, using target modules: {target_modules}")
            elif "gptj" in model_type or "gpt-j" in model_type:
                target_modules = ["q_proj", "v_proj", "k_proj", "out_proj", "fc_in", "fc_out"]
                print(f"Detected GPT-J architecture, using target modules: {target_modules}")
            elif "gpt-neox" in model_type or "pythia" in model_type:
                target_modules = ["query_key_value", "dense", "dense_h_to_4h", "dense_4h_to_h"]
                print(f"Detected GPT-NeoX architecture, using target modules: {target_modules}")
            else:
                # Fallback to a general approach - scan the model layers
                possible_modules = [
                    "q_proj", "k_proj", "v_proj", "o_proj",  # Common in many models
                    "query_key_value", "dense", "dense_h_to_4h", "dense_4h_to_h",  # Common in some models
                    "gate_proj", "up_proj", "down_proj",  # LLaMA-style
                    "c_attn", "c_proj", "c_fc",  # GPT-2 style
                    "attn.q", "attn.k", "attn.v", "attn.out",  # Other variations
                    "linear", "linear1", "linear2"  # Generic linear layers
                ]

                # Get all named modules
                all_modules = dict(model.named_modules())
                detected_modules = set()

                # Check each module if it contains any of the patterns
                for name in all_modules:
                    for pattern in possible_modules:
                        if pattern in name:
                            parts = name.split('.')
                            # Find the specific linear layer name (usually the last part)
                            for i in range(len(parts) - 1, -1, -1):
                                if parts[i] in possible_modules:
                                    detected_modules.add(parts[i])
                                    break

                target_modules = list(detected_modules)
                if not target_modules:
                    # If we couldn't find any specific module, look for Linear layers
                    for name, module in all_modules.items():
                        if isinstance(module, torch.nn.Linear):
                            # Extract the module name from the full path
                            parts = name.split('.')
                            target_modules.append(parts[-1])

                # Final fallback - get any linear layer
                if not target_modules:
                    target_modules = ["query", "key", "value", "dense"]

                print(f"Auto-detected target modules: {target_modules}")

        # Configure LoRA
        print("Initializing LoRA configuration")
        peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            target_modules=target_modules
        )

        # Get PEFT model
        print("Applying LoRA adapters to model")
        model = get_peft_model(model, peft_config)

        # Print trainable parameters
        model.print_trainable_parameters()

        # Process the dataset
        def prepare_dataset(data):
            if isinstance(data, str):
                # Load from path/name
                return load_dataset(data)
            elif isinstance(data, list):
                # Convert list of dictionaries to dataset
                return Dataset.from_list(data)
            else:
                # Assume it's already a Dataset
                return data

        train_dataset = prepare_dataset(train_data)
        if val_data is not None:
            val_dataset = prepare_dataset(val_data)

        # Define tokenization function
        def tokenize_function(examples: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
            tokenized = tokenizer(
                examples[text_column],
                padding="max_length",
                truncation=True,
                max_length=max_length
            )
            tokenized["labels"] = tokenized["input_ids"].copy()
            return tokenized

        # Tokenize datasets
        print("Tokenizing datasets")
        tokenized_train = train_dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=train_dataset.column_names
        )

        if val_data is not None:
            tokenized_val = val_dataset.map(
                tokenize_function,
                batched=True,
                remove_columns=val_dataset.column_names
            )
        else:
            tokenized_val = None

        # Create data collator
        data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

        training_args_dict = {
            "output_dir": output_dir,
            "per_device_train_batch_size": micro_batch_size,
            "gradient_accumulation_steps": gradient_accumulation_steps,
            "learning_rate": learning_rate,
            "num_train_epochs": num_epochs,
            "warmup_steps": warmup_steps,
            "logging_steps": logging_steps,
            "save_steps": save_steps,
            "evaluation_strategy": "steps" if tokenized_val is not None else "no",
            "eval_steps": eval_steps if tokenized_val is not None and eval_steps is not None else None,
            "save_total_limit": 3,
            "load_best_model_at_end": tokenized_val is not None,
            "fp16": mixed_precision == "fp16",
            "bf16": mixed_precision == "bf16",
            "report_to": "tensorboard",
            "remove_unused_columns": False,
            "push_to_hub": False,
        }

        if max_steps is not None:
            training_args_dict["max_steps"] = max_steps

        training_args = TrainingArguments(**training_args_dict)

        # Create Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_train,
            eval_dataset=tokenized_val,
            data_collator=data_collator,
        )

        # Train model
        print("Starting training...")
        trainer.train()

        # Save model
        print(f"Saving model to {output_dir}")
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)

        print("Training complete!")


class CachedLoRATrainer(LoRATrainer):
    """
    Extended LoRATrainer with input/output caching during inference.
    """

    @staticmethod
    def infer_with_cache(
        model: PreTrainedModel,
        tokenizer: PreTrainedTokenizer,
        input_texts: List[str],
        cache_path: str = "cache.jsonl",
        max_length: int = 512,
        log_hits: bool = True,
        generation_kwargs: dict = None
    ) -> List[str]:
        """
        Generate model outputs for input texts with caching.

        Args:
            model: Trained language model
            tokenizer: Tokenizer for the model
            input_texts: List of input strings to generate from
            cache_path: File path to store/reuse outputs
            max_length: Max generation length
            log_hits: If True, logs when cache is hit or missed
            generation_kwargs: Additional args for model.generate()

        Returns:
            List of generated strings, in same order as input_texts
        """
        cache = {}
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        cache[record["input_hash"]] = record
                    except json.JSONDecodeError:
                        continue

        results = []
        new_cache_entries = []
        generation_kwargs = generation_kwargs or {}

        for text in input_texts:
            input_hash = sha256(text.encode("utf-8")).hexdigest()

            if input_hash in cache:
                output = cache[input_hash]["output"]
                if log_hits:
                    print(f"[CACHE HIT] \"{text[:40]}...\"")
            else:
                inputs = tokenizer(
                    text,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=max_length
                ).to(model.device)

                with torch.no_grad():
                    output_ids = model.generate(
                        **inputs,
                        max_length=max_length,
                        **generation_kwargs
                    )
                output = tokenizer.decode(output_ids[0], skip_special_tokens=True)

                if log_hits:
                    print(f"[CACHE MISS] \"{text[:40]}...\" → Generated")

                # Save for later
                new_cache_entries.append({
                    "input": text,
                    "input_hash": input_hash,
                    "output": output
                })

            results.append(output)

        if new_cache_entries:
            with open(cache_path, "a", encoding="utf-8") as f:
                for entry in new_cache_entries:
                    f.write(json.dumps(entry) + "\n")

        return results
