from datasets import Dataset, DatasetDict
import random

from forgen.training.trainers.lora import LoRATrainer


def generate_patent_qa_dataset():
    # Seed for reproducibility
    random.seed(42)

    # Example question templates
    patent_qas = [
        {"q": "What is a patent?", "a": "A patent is a form of intellectual property that gives the inventor exclusive rights to their invention."},
        {"q": "How long does a utility patent last in the US?", "a": "A utility patent in the US typically lasts for 20 years from the filing date."},
        {"q": "What is prior art in patent law?", "a": "Prior art refers to any evidence that your invention is already known before your filing date."},
        {"q": "What is a provisional patent application?", "a": "It is a preliminary application that allows inventors to secure a filing date without a formal patent claim."},
        {"q": "Can software be patented?", "a": "Yes, software can be patented if it demonstrates a novel and non-obvious technical process."},
        {"q": "What is the difference between a patent and a trademark?", "a": "A patent protects inventions; a trademark protects brand names, logos, and slogans."},
        {"q": "What is the purpose of a patent claim?", "a": "A patent claim defines the scope of protection granted by the patent."},
        {"q": "What is a design patent?", "a": "A design patent protects the ornamental design of a functional item."},
        {"q": "What is the USPTO?", "a": "The USPTO is the United States Patent and Trademark Office."},
        {"q": "What happens when a patent expires?", "a": "Once a patent expires, the invention enters the public domain and can be freely used."}
    ]

    # Shuffle and split into train/val
    random.shuffle(patent_qas)
    train_split = patent_qas[:7]
    val_split = patent_qas[7:]

    def to_dataset(split):
        return Dataset.from_list([
            {"text": f"Q: {item['q']} A:", "answer": item["a"]} for item in split
        ])

    dataset = DatasetDict({
        "train": to_dataset(train_split),
        "validation": to_dataset(val_split)
    })

    return dataset

from datasets import load_from_disk


from datasets import load_dataset

dataset = load_dataset("pile", "uspto")
# dataset = load_dataset("bookcorpus")
# dataset = load_dataset("wikihow", "all")


# Example usage
if __name__ == "__main__":
    # dataset = generate_patent_qa_dataset()
    # dataset.save_to_disk("patent_qa_dataset")
    #
    # print("✅ Patent Q&A dataset saved to: patent_qa_dataset")
    # print(dataset)

    dataset = load_from_disk("patent_qa_dataset")

    LoRATrainer.train(
        base_model_name="gpt2",
        output_dir="./gpt2-lora-patent",
        train_data=dataset["train"],
        val_data=dataset["validation"],
        batch_size=4,
        micro_batch_size=2,
        num_epochs=3,
        learning_rate=5e-5,
        use_4bit=False,
        use_8bit=True,
        mixed_precision="fp16",
        save_steps=10,
        logging_steps=2
    )
