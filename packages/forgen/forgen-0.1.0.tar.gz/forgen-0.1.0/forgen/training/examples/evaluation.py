import time
from datasets import load_dataset
from forgen.training.trainers.cached_lora import CachedBaseLoRATrainer
from forgen.training.trainers.lora import LoRATrainer

# Load a subset of the HUPD dataset
# For demonstration, we'll use a small sample. Adjust the parameters as needed for larger datasets.
print("📥 Loading HUPD dataset subset...")
dataset = load_dataset(
    'HUPD/hupd', 'sample',
    trust_remote_code=True,
    uniform_split=True
)

# Split the dataset into training and validation sets
print("🔀 Splitting dataset into train and validation sets...")
# ✅ CORRECT - split the 'train' subset from the dataset dict
split = dataset['train'].train_test_split(test_size=0.2)
train_dataset = split['train']
val_dataset = split['test']


# ---------------------
# ✅ Training with caching
# ---------------------
print("\n📦 Running CachedBaseLoRATrainer...")
start_cached = time.time()
CachedBaseLoRATrainer.train(
    base_model_name="gpt2",
    output_dir="./out_cached_hupd",
    train_data=train_dataset,
    val_data=val_dataset,
    text_column="abstract",  # Adjust based on the dataset's available fields
    num_epochs=1,
    batch_size=4,
    micro_batch_size=2,
    use_8bit=True,
    mixed_precision=None,
    cache_path="base_forward_cache.jsonl"
)
end_cached = time.time()
cached_duration = end_cached - start_cached
print(f"\n✅ Cached training time: {cached_duration:.2f} seconds")

# ---------------------
# ❌ Training without caching
# ---------------------
print("\n📦 Running LoRATrainer (no cache)...")
start_nocache = time.time()
LoRATrainer.train(
    base_model_name="gpt2",
    output_dir="./out_nocache_hupd",
    train_data=train_dataset,
    val_data=val_dataset,
    text_column="abstract",  # Adjust based on the dataset's available fields
    num_epochs=1,
    batch_size=4,
    micro_batch_size=2,
    use_8bit=True,
    mixed_precision=None
)
end_nocache = time.time()
nocache_duration = end_nocache - start_nocache
print(f"\n✅ Non-cached training time: {nocache_duration:.2f} seconds")

# ---------------------
# 🚀 Compare
# ---------------------
speedup = nocache_duration / cached_duration if cached_duration > 0 else 0
print(f"\n🚀 Speedup from caching: {speedup:.2f}x faster")
