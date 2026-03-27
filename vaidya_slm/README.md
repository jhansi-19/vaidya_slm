# Vaidya SLM: Ayurvedic AI for Bharat

## Project Overview
**Vaidya SLM** is an offline-capable, culturally optimized Small Language Model (SLM) configured to act as an Ayurvedic consultant for rural and offline parts of India. By combining the vast pharmacological history found in classical texts (Charaka Samhita, Sushruta Samhita, Ashtanga Hridayam) with modern INT4 quantized Large Language Model paradigms (<3B parameters) and a deterministic reasoning engine, it brings affordable, voice-first healthcare diagnostics offline.

## Architecture

1. **Frontend (Flutter)**: 
   - Supports multilinguality and voice recording natively.
   - Built for low-end Android devices.
   
2. **Backend (FastAPI)**:
   - Integrates the pipeline locally.
   - **Hybrid Reasoning**: Maps explicit symptoms heavily using a structured knowledge base `knowledge_base.json` to avoid LLM hallucinations, while the SLM handles edge cases, generative language, and instruction processing.

3. **Data & Weights**:
   - `TinyLlama` or `Mistral-1.1B` architecture used as the base.
   - QLoRA (PEFT) utilized for prompt instruction formatting tuned on parsed Ayurvedic prescriptions.
   - Weights merged and converted to `.gguf` to run universally using `llama.cpp` wrapper.

## Directory Structure
```text
c:\ideaverse\vaidya_slm
├── backend/          
│   ├── ai/                 # asr, tts, llm_inference wrappers
│   ├── engine/             # rule_based.py mapping and reasoning logic
│   └── main.py             # FastAPI entry point
├── frontend/               # The Flutter App
├── scripts/          
│   ├── data/               # Scripts mapped for data synthesis
│   └── training/           # Colab notebook and python tools for fine-tuning
└── docs/                   # Demo preparation materials
```

## Running the Project

### Testing the Backend Local API
Navigate to `/backend`
```bash
pip install fastapi uvicorn pydantic
python main.py
```
Test that localhost:8000 is open. The Hybrid Reasoner uses `backend/engine/rule_based.py` implicitly.

### Testing the Flutter Frontend
Make sure you have an emulator or device attached.
```bash
cd frontend
flutter create .          # if missing initialization
flutter pub get
flutter run
```

### Reproducing Training Pipeline
1. Build dataset using Hugging Face (default path used in Colab):
   - `python scripts/data/preprocess_ayurvedic.py --source huggingface --hf-limit 500`
2. Optional mixed mode (archive/kaggle + HF fallback):
   - `python scripts/data/preprocess_ayurvedic.py --source mixed --hf-limit 500`
3. Open `scripts/training/qlora_finetune.ipynb` in Colab.
4. Merge adapters and convert to GGUF using:
   - `python scripts/training/export_gguf.py`

Notes:
- Kaggle is optional and disabled by default. To enable in downloader, set `USE_KAGGLE=1`.
- GGUF conversion follows the stable two-step path: `f16 -> Q4_0` quantization.
