import time
import random
from datasets import Dataset

from forgen.training.trainers.cached_lora import CachedBaseLoRATrainer
from forgen.training.trainers.lora import LoRATrainer

# 1. Generate more varied shared questions
categories = ["capital", "population", "currency", "language"]
questions = [
    f"What is the {cat} of country {i}?" for i in range(100) for cat in categories
]  # 40 total

# 2. Create unique answer sets
answers_sets = {
    "factual": [f"Fact-{i % 50}-{cat}" for i, cat in enumerate(categories * 100)],
    "codes": [f"C{i:03}-{cat[:2].upper()}" for i, cat in enumerate(categories * 100)],
    "humor": [f"{cat.title()}? Probably vibes. 😄" for cat in categories * 100]
}

# 3. Build one dataset (choose one)
dataset = Dataset.from_dict({
    "text": questions,
    "label": answers_sets["factual"]
})

# Optional quick mode
QUICK_MODE = True  # Toggle this to False for full training
if QUICK_MODE:
    dataset = dataset.select(range(int(0.5 * len(dataset))))  # 50% for quick run

# Train/val split
dataset = dataset.train_test_split(test_size=0.2)
train_dataset = dataset["train"]
val_dataset = dataset["test"]

# 🧠 Run Cached Training
print("\n📦 Running CachedBaseLoRATrainer...")
start_cached = time.time()
CachedBaseLoRATrainer.train(
    base_model_name="gpt2",
    output_dir="./out_cached_custom",
    train_data=train_dataset,
    val_data=val_dataset,
    text_column="text",  # <- fix from "query"
    num_epochs=1,
    batch_size=4,
    micro_batch_size=2,
    use_8bit=True,
    mixed_precision=None,
    cache_path="base_forward_cache.jsonl"
)
end_cached = time.time()
print(f"✅ Cached training time: {end_cached - start_cached:.2f} sec")

# 🚫 Run Non-Cached Training
print("\n📦 Running LoRATrainer...")
start_nocache = time.time()
LoRATrainer.train(
    base_model_name="gpt2",
    output_dir="./out_nocache_custom",
    train_data=train_dataset,
    val_data=val_dataset,
    text_column="text",  # <- fix from "question"
    num_epochs=1,
    batch_size=4,
    micro_batch_size=2,
    use_8bit=True,
    mixed_precision=None
)
end_nocache = time.time()
print(f"✅ Non-cached training time: {end_nocache - start_nocache:.2f} sec")

# 🚀 Compare
speedup = (end_nocache - start_nocache) / (end_cached - start_cached)
print(f"\n🚀 Speedup from caching: {speedup:.2f}x faster")
