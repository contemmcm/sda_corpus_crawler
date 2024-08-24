from datasets import Dataset
from transformers import GPT2Tokenizer, GPT2Config
from transformers import GPT2LMHeadModel
from transformers import Trainer, TrainingArguments
from transformers import DataCollatorForLanguageModeling

from crawler.models import Document

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token
tokenizer.pad_token_id = tokenizer.eos_token_id


def load_documents():
    """
    Load all documents from the database.
    """

    texts = [doc.text_revised for doc in Document.objects.all()]

    return Dataset.from_dict({"text": texts})


def tokenize_function(examples):
    """
    Tokenize the text examples.
    """
    return tokenizer(
        examples["text"], padding="max_length", truncation=True, max_length=1024
    )


def run():

    dataset = load_documents()

    tokenized_dataset = dataset.map(
        tokenize_function, batched=True, num_proc=4, remove_columns=["text"]
    )

    # Define model configuration
    config = GPT2Config(
        vocab_size=len(tokenizer),
        n_positions=1024,
        n_ctx=1024,
        n_embd=768,
        n_layer=12,
        n_head=12,
    )

    # Initialize the model
    model = GPT2LMHeadModel(config)
    model.config.pad_token_id = tokenizer.pad_token_id

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # Set to False since GPT-2 is not trained with masked language modeling
    )

    # Define training arguments
    training_args = TrainingArguments(
        output_dir="./gpt2-scratch",
        overwrite_output_dir=True,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        save_steps=10_000,
        save_total_limit=2,
        prediction_loss_only=True,
        logging_dir="./logs",
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    trainer.train()

    model.save_pretrained("./gpt2-scratch")
    tokenizer.save_pretrained("./gpt2-scratch")


if __name__ == "__main__":
    run()
