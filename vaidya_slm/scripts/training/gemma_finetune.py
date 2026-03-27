import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# 1. Configuration
MODEL_ID = "google/gemma-2-2b-it"
DATASET_PATH = "../../../ayurveda_finetune.jsonl"
OUTPUT_DIR = "./vaidya-gemma-finetuned"

# 2. BitsAndBytes Config (4-bit quantization for low VRAM)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
)

# 3. Load Model & Tokenizer
print(f"Loading model: {MODEL_ID}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    token=os.getenv("HF_TOKEN") # Required for Gemma access
)
model = prepare_model_for_kbit_training(model)

# 4. LoRA Config
peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "o_proj", "k_proj", "v_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, peft_config)

# 5. Load Dataset
print(f"Loading dataset from: {DATASET_PATH}")
dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

# 6. Training Arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    optim="paged_adamw_32bit",
    save_steps=100,
    logging_steps=10,
    learning_rate=2e-4,
    weight_decay=0.01,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    max_grad_norm=0.3,
    num_train_epochs=3,
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    group_by_length=True,
    report_to="none",
)

# 7. SFT Trainer
# Note: ayurveda_finetune.jsonl already has a "text" field with the correct prompt format.
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    peft_config=peft_config,
    dataset_text_field="text",
    max_seq_length=1024,
    tokenizer=tokenizer,
    args=training_args,
)

# 8. Train
print("Starting training...")
trainer.train()

# 9. Save
trainer.model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Training complete. Weights saved to {OUTPUT_DIR}")
