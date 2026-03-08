from datasets import load_from_disk
from transformers import MT5ForConditionalGeneration, MT5Tokenizer, Seq2SeqTrainingArguments, Seq2SeqTrainer, DataCollatorForSeq2Seq
from peft import get_peft_model, LoraConfig, TaskType

# 1. Load the tokenizer and the Base Model
model_name = "google/mt5-small"
tokenizer = MT5Tokenizer.from_pretrained(model_name)
model = MT5ForConditionalGeneration.from_pretrained(model_name)

# 2. Apply LoRA for efficient training
lora_config = LoraConfig(
    r=8, 
    lora_alpha=32, 
    target_modules=["q", "v"], 
    lora_dropout=0.05,
    task_type=TaskType.SEQ_2_SEQ_LM
)
model = get_peft_model(model, lora_config)

# 3. Load the data we prepped in Phase 2
dataset = load_from_disk("data/doha_hf_dataset")

# 4. Tokenization Function (converts text to numbers)
def preprocess_function(examples):
    inputs = tokenizer(examples["input_text"], max_length=128, truncation=True, padding="max_length")
    targets = tokenizer(examples["target_text"], max_length=128, truncation=True, padding="max_length")
    inputs["labels"] = targets["input_ids"]
    return inputs

tokenized_datasets = dataset.map(preprocess_function, batched=True)

# 5. Define Training Arguments
training_args = Seq2SeqTrainingArguments(
    output_dir="./doha_model_output",
    evaluation_strategy="epoch",
    learning_rate=2e-4,
    per_device_train_batch_size=8,
    num_train_epochs=3, # Start with 3 epochs to see how it performs
    save_strategy="epoch",
)

data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

# 6. Start the Training!
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
    data_collator=data_collator,
    tokenizer=tokenizer,
)

print("Starting training...")
trainer.train()

# 7. Save the final trained model
model.save_pretrained("./final_doha_model")
tokenizer.save_pretrained("./final_doha_model")
print("Model saved successfully!")