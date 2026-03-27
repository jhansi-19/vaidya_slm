# Vaidya SLM - Ayurvedic Medical Assistant

A speech-enabled AI system for Ayurvedic medicine consultation with multilingual support.

## Features

- **LLM Inference**: Gemma 2 2B quantized model for Ayurvedic medicine
- **RAG System**: 446-chunk knowledge base with hybrid similarity scoring
- **Text-to-Speech**: gTTS with 10+ language support (Hindi, Telugu, Tamil, etc.)
- **Speech-to-Text**: Mock ASR
- **Multilingual**: Support for Indian and English languages
- **Translation**: Automatic translation between languages

## Architecture

### Backend
- `vaidya_slm/backend/main.py` - FastAPI server
- `vaidya_slm/backend/ai/llm_inference.py` - LLM inference with RAG integration
- `vaidya_slm/backend/ai/rag.py` - Knowledge retrieval engine
- `vaidya_slm/backend/ai/tts.py` - Google Text-to-Speech integration
- `vaidya_slm/backend/ai/asr.py` - Mock speech recognition
- `vaidya_slm/backend/ai/translator.py` - Language translation

### Frontend
- `vaidya_slm/frontend_web/` - React web interface
- `vaidya_slm/frontend/` - Dart Flutter app

### Models
- `vaidya_slm/models/gemma-2-2b-it.Q4_K_M.gguf` - Quantized LLM
- `vaidya_slm/models/vaidya-gemma-adapter.gguf` - Domain adapter

## Setup

```bash
# Install dependencies
pip install -r vaidya_slm/requirements.txt

# Start LLM server (llama-cpp)
./tools/llama-cpp-bin/llama-server.exe -m ./vaidya_slm/models/gemma-2-2b-it.Q4_K_M.gguf --host 127.0.0.1 --port 8008

# Start backend
cd vaidya_slm/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8005
```

## API Endpoints

- `POST /infer` - Get Ayurvedic diagnosis and remedies
- `POST /tts` - Convert text to speech
- `POST /asr` - Convert speech to text
- `POST /detect-language` - Detect input language

## Knowledge Base

- **Source**: 446 Ayurvedic medical chunks
- **Format**: JSONL with text and metadata
- **Matching**: Hybrid similarity (70% keyword + 30% sequence)
- **Relevance**: 38-48% average match score

## Status

- ✓ LLM Inference (Gemma 2)
- ✓ RAG Integration (446 chunks)
- ✓ Text-to-Speech (gTTS)
- ✓ Speech to Text
- ✓ Translation
- ✓ Multilingual Support
