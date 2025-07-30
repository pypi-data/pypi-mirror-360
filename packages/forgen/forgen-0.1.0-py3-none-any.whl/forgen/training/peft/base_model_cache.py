import os
import json
import torch
from torch import nn
from hashlib import sha256
from transformers import AutoModelForCausalLM, PreTrainedTokenizer, PreTrainedModel
from transformers.modeling_outputs import CausalLMOutputWithPast


class BaseModelCacheWrapper(PreTrainedModel):
    """
    Wraps a causal language model to cache frozen base model forward outputs for training efficiency.
    Designed to be PEFT-compatible (i.e., works with LoRA).
    """

    def __init__(
        self,
        base_model: AutoModelForCausalLM,
        tokenizer: PreTrainedTokenizer,
        cache_path: str = "base_model_cache.jsonl",
        max_length: int = 512,
        log_hits: bool = True
    ):
        # Properly initialize the parent class with the base model's config
        config = base_model.config
        super().__init__(config)

        # Store the base model
        self._base_model = base_model

        # Try to locate the transformer and lm_head (supports GPT2, LLaMA, etc.)
        self.transformer = getattr(base_model, "transformer", getattr(base_model, "model", None))
        self.lm_head = getattr(base_model, "lm_head", getattr(base_model, "lm_head_proj", None))

        if self.transformer is None or self.lm_head is None:
            raise AttributeError(
                "Could not locate `transformer` or `lm_head` in the provided base_model."
            )

        self.tokenizer = tokenizer
        self.cache_path = cache_path
        self.max_length = max_length
        self.log_hits = log_hits
        self.cache = self._load_cache()
        self.cache_hits = 0
        self.cache_misses = 0

    @property
    def cache_stats(self):
        total = self.cache_hits + self.cache_misses
        pct = (self.cache_hits / total * 100) if total > 0 else 0.0
        return f"{self.cache_hits}/{total} hits ({pct:.2f}%)"

    def _load_cache(self):
        if not os.path.exists(self.cache_path):
            return {}
        cache = {}
        with open(self.cache_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line)
                    cache[item["input_hash"]] = item
                except json.JSONDecodeError:
                    continue
        return cache

    def _save_to_cache(self, input_hash, hidden_states):
        record = {
            "input_hash": input_hash,
            "hidden_states": hidden_states.detach().cpu().tolist()
        }
        with open(self.cache_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        self.cache[input_hash] = record

    def _compute_hash(self, input_ids):
        flat = input_ids.view(-1).tolist()
        h = sha256(json.dumps(flat).encode("utf-8")).hexdigest()
        print("📛 Hash:", h)  # ⬅️ Debug this
        return h

    def get_input_embeddings(self):
        return self._base_model.get_input_embeddings()

    def set_input_embeddings(self, new_embeddings):
        return self._base_model.set_input_embeddings(new_embeddings)

    def forward(self, input_ids=None, attention_mask=None, labels=None, **kwargs):
        input_hash = self._compute_hash(input_ids)
        print(f"🚦Cache {'HIT' if input_hash in self.cache else 'MISS'}: {input_hash}")

        if input_hash in self.cache:
            self.cache_hits += 1
            if self.log_hits:
                print("[BASE CACHE HIT]")
            hidden_states = torch.tensor(
                self.cache[input_hash]["hidden_states"],
                dtype=torch.float32,
                device=input_ids.device
            )
        else:
            self.cache_misses += 1
            if self.log_hits:
                print("[BASE CACHE MISS]")
            with torch.no_grad():
                outputs = self.transformer(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    **kwargs
                )
                hidden_states = outputs.last_hidden_state
            self._save_to_cache(input_hash, hidden_states)

        hidden_states = hidden_states.clone().detach().requires_grad_()

        logits = self.lm_head(hidden_states)

        loss = None
        if labels is not None:
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss_fct = torch.nn.CrossEntropyLoss()
            loss = loss_fct(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1)
            )

        return CausalLMOutputWithPast(
            loss=loss,
            logits=logits,
            past_key_values=None,
            hidden_states=hidden_states,
            attentions=None
        )
