import time
from forgen.training.trainers.cached_lora import CachedBaseLoRATrainer
from forgen.training.trainers.lora import LoRATrainer
from datasets import load_dataset

# Load MS MARCO dataset
dataset = load_dataset("ms_marco", "v2.1", split="train")

# Optional quick mode
QUICK_MODE = True  # Toggle this to False for full training

if QUICK_MODE:
    dataset = dataset.select(range(int(0.001 * len(dataset))))  # 1% subset

# Train/val split
dataset = dataset.train_test_split(test_size=0.2)
train_dataset = dataset["train"]
val_dataset = dataset["test"]


# 🧠 Run Cached Training
print("\n📦 Running CachedBaseLoRATrainer...")
start_cached = time.time()
CachedBaseLoRATrainer.train(
    base_model_name="gpt2",
    output_dir="./out_cached_ms_marco",
    train_data=train_dataset,
    val_data=val_dataset,
    text_column="query",
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
    output_dir="./out_nocache_ms_marco",
    train_data=train_dataset,
    val_data=val_dataset,
    text_column="question",
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
