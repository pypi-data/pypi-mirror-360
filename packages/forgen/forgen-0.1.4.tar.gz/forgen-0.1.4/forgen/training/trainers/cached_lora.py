import torch

from transformers import (
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
from datasets import  load_dataset
from typing import Dict, List, Optional, Union

from datasets import Dataset

from forgen.training.peft.base_model_cache import BaseModelCacheWrapper


class CachedBaseLoRATrainer:
    """
    A standalone LoRA trainer that caches the frozen base model's hidden states during training.
    """

    @staticmethod
    def train(
        base_model_name: str,
        output_dir: str,
        train_data: Union[Dataset, str, List[Dict[str, str]]],
        val_data: Optional[Union[Dataset, str, List[Dict[str, str]]]] = None,
        text_column: str = "text",
        r: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.05,
        target_modules: Optional[List[str]] = None,
        batch_size: int = 4,
        micro_batch_size: int = 1,
        num_epochs: int = 3,
        learning_rate: float = 3e-4,
        warmup_steps: int = 100,
        max_steps: Optional[int] = None,
        max_length: int = 512,
        use_4bit: bool = False,
        use_8bit: bool = False,
        double_quant: bool = True,
        quant_type: str = "nf4",
        gradient_accumulation_steps: Optional[int] = None,
        gradient_checkpointing: bool = True,
        mixed_precision: Optional[str] = "fp16",
        save_steps: int = 100,
        logging_steps: int = 10,
        eval_steps: Optional[int] = None,
        seed: int = 42,
        cache_path: str = "base_model_cache.jsonl"
    ) -> None:

        torch.manual_seed(seed)

        if gradient_accumulation_steps is None:
            gradient_accumulation_steps = batch_size // micro_batch_size

        model_kwargs = {"device_map": "auto", "trust_remote_code": True}

        if use_4bit or use_8bit:
            if use_4bit:
                from transformers import BitsAndBytesConfig
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=double_quant,
                    bnb_4bit_quant_type=quant_type,
                    bnb_4bit_compute_dtype=torch.bfloat16
                )
                model_kwargs["quantization_config"] = bnb_config
            elif use_8bit:
                model_kwargs["load_in_8bit"] = True

        print(f"Loading base model: {base_model_name}")
        base_model = AutoModelForCausalLM.from_pretrained(base_model_name, **model_kwargs)
        tokenizer = AutoTokenizer.from_pretrained(base_model_name)

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token or "</s>"

        for param in base_model.parameters():
            param.requires_grad = False

        if gradient_checkpointing:
            base_model.gradient_checkpointing_enable()

        if use_4bit or use_8bit:
            base_model = prepare_model_for_kbit_training(base_model)

        wrapped_base = BaseModelCacheWrapper(
            base_model,
            tokenizer=tokenizer,
            cache_path=cache_path,
            max_length=max_length,
            log_hits=True
        )

        if target_modules is None:
            target_modules = ["c_attn", "c_proj", "q_proj", "v_proj", "o_proj"]

        peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            target_modules=target_modules
        )

        model = get_peft_model(wrapped_base, peft_config)
        model.print_trainable_parameters()

        def prepare_dataset(data):
            if isinstance(data, str):
                return load_dataset(data)["train"]
            elif isinstance(data, list):
                return Dataset.from_list(data)
            return data

        train_dataset = prepare_dataset(train_data)
        val_dataset = prepare_dataset(val_data) if val_data else None

        def tokenize_function(examples):
            # Turn text into consistent tokens
            tokens = tokenizer(
                examples[text_column],
                padding="max_length",
                truncation=True,
                max_length=max_length,
                return_attention_mask=True,
                return_tensors="pt"  # ensures deterministic shape
            )

            tokens["labels"] = tokens["input_ids"].clone()
            return {k: v.numpy().tolist() for k, v in tokens.items()}  # convert back to list for datasets

        tokenized_train = train_dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=train_dataset.column_names
        )

        tokenized_val = val_dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=val_dataset.column_names
        ) if val_dataset else None

        data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

        training_args = TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size=micro_batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            learning_rate=learning_rate,
            num_train_epochs=num_epochs,
            max_steps=max_steps if max_steps else -1,
            warmup_steps=warmup_steps,
            logging_steps=logging_steps,
            save_steps=save_steps,
            evaluation_strategy="steps" if tokenized_val else "no",
            eval_steps=eval_steps,
            save_total_limit=3,
            load_best_model_at_end=bool(tokenized_val),
            fp16=mixed_precision == "fp16",
            bf16=mixed_precision == "bf16",
            report_to="tensorboard",
            remove_unused_columns=False,
            push_to_hub=False,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_train,
            eval_dataset=tokenized_val,
            data_collator=data_collator,
        )

        print("Starting training with base model caching...")
        trainer.train()

        print(f"Saving model to {output_dir}")
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)

        print("✅ Training complete with base model forward caching!")
