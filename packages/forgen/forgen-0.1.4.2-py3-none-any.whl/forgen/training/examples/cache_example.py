from datasets import Dataset

from forgen.training.trainers.cached_lora import CachedBaseLoRATrainer

data = {
    "text": ["This is a test."] * 10  # identical input repeated
}
ds = Dataset.from_dict(data)
ds = ds.train_test_split(test_size=0.2)

CachedBaseLoRATrainer.train(
    base_model_name="gpt2",
    output_dir="./out_cached_test",
    train_data=ds["train"],
    val_data=ds["test"],
    num_epochs=1,
    batch_size=2,
    micro_batch_size=1,
    use_8bit=True,
    mixed_precision=None,
    cache_path="test_cache.jsonl"
)
