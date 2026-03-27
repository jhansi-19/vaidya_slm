import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

# Configuration
BASE_MODEL = "google/gemma-2-2b-it"
ADAPTER_PATH = "../../models/finetuned"
SAVE_PATH = "./vaidya-slm-merged"

# Try to get token from env or ask user
token = os.getenv("HF_TOKEN")
if not token:
    token = input("Enter your Hugging Face Token: ")

print(f"Loading base model: {BASE_MODEL}")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=token)
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="cpu", # Use CPU to avoid VRAM issues on local machine
    token=token,
)

print(f"Merging LoRA adapters from: {ADAPTER_PATH}")
model = PeftModel.from_pretrained(model, ADAPTER_PATH)
model = model.merge_and_unload()

print(f"Saving merged model to: {SAVE_PATH}")
model.save_pretrained(SAVE_PATH)
tokenizer.save_pretrained(SAVE_PATH)

print("Merge complete! Now run 'python export_gguf.py' to generate the final GGUF file.")
