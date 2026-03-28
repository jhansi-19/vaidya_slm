# Vaidya SLM - Multilingual Ayurvedic AI Doctor

A localized, speech-enabled AI system for Ayurvedic medicine consultation with seamless multilingual support, specifically tailored for Indian contexts.

## 🎯 Problem Statement

Traditional Ayurvedic knowledge is vast and highly nuanced, but it is often inaccessible to the general public, especially those who primarily speak regional Indic languages. Furthermore, existing generic Large Language Models (LLMs) lack specialized medical guardrails and deep roots in traditional Ayurvedic diagnosis and remedies. People in rural or semi-urban areas face language barriers, technological barriers (typing), and a lack of reliable, locally-run AI systems for personalized health inquiries.

## 🚀 What We Built

**Vaidya SLM** (Small Language Model) is a robust, end-to-end AI consultation platform that bridges the gap between ancient Ayurvedic wisdom and modern localized AI inference. 

We built a **fully private, locally hosted AI assistant** powered by a fine-tuned Gemma-2 2B model. It utilizes a custom Retrieval-Augmented Generation (RAG) pipeline to fetch accurate Ayurvedic remedies from a curated JSONL knowledge base. To overcome literacy and language barriers, the system is natively integrated with Real-Time Speech-to-Text (ASR) and Text-to-Speech (TTS), automatically translating between English and various Indian languages (Hindi, Telugu, Tamil, etc.).

### Key Architectural Components

- **Local LLM Engine**: A highly optimized `llama.cpp` inference server running a quantized Gemma-2 2B model (`Q4_K_M`) and custom LoRA adapters (`vaidya-gemma-adapter.gguf`).
- **Ayurvedic RAG System**: Custom hybrid-similarity vector retrieval (70% keyword + 30% sequence) against 446 specialized medical chunks. Ensures the AI's answers are grounded in verifiable texts.
- **Multilingual Voice Interface**: Includes an integrated pipeline for Voice input (ASR) and automated Voice output (gTTS) across 10+ languages (e.g., Telugu, Hindi).
- **Translation Layer**: Automatic context-aware translation to ensure the core medical reasoning in English is accurately delivered to users in their native language context.
- **Client Interfaces**: A React/Web-based UI (`frontend_pro`) and a Flutter app (`frontend`) for easy interaction.

## 📦 Project Structure

- `vaidya_slm/backend/`: Python FastAPI Backend integrating AI modules (RAG, LLM Inference, ASR, TTS, Translator).
- `vaidya_slm/frontend_pro/`: Web frontend interface.
- `vaidya_slm/models/`: Directory housing the GGUF models and adapters.
- `tools/llama-cpp-bin/`: Compiled Llama.cpp binaries for ultra-fast local inference.
- `scripts/`: Scripts for data preprocessing, GGUF conversion, and QLoRA fine-tuning.

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.10+
- Node.js (if working on the React/Vite web apps)
- Git Large File Storage (Git LFS) for model downloading

### 2. Install Backend Dependencies
```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate # Mac/Linux

# Install requirements
pip install -r vaidya_slm/backend/requirements.txt
# (or install FastAPI, Uvicorn, gTTS, requests, etc. if no requirements.txt exists)
```

### 3. Setup Models
Ensure the following models are present inside `c:\idea1\vaidya_slm\models\`:
- `gemma-2-2b-it.Q4_K_M.gguf` (Quantized base model)
- `vaidya-gemma-adapter.gguf` (Fine-tuned adapter)
- `vaidya-slm-1.1b-instruct-q4_0.gguf` (Optional fallback)

## 🏃‍♂️ How to Run

To run the full stack locally, you need to open **three separate terminals** and leave them running concurrently.

### Terminal 1: Start the Local LLM Server (llama.cpp)
This starts the highly optimized inference engine.
```bash
cd c:\idea1\tools\llama-cpp-bin
llama-server.exe -m c:\idea1\vaidya_slm\models\gemma-2-2b-it.Q4_K_M.gguf --host 127.0.0.1 --port 8008 --ctx-size 2048
```
*Health Check: Visit `http://127.0.0.1:8008/health`*

### Terminal 2: Start the FastAPI Backend
This service handles RAG, TTS, Translation, and API coordination between the frontend and the LLM.
```bash
# Ensure your virtual environment is activated!
cd c:\idea1\vaidya_slm\backend
c:\idea1\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8005
```
*API Docs: Visit `http://localhost:8005/docs`*

### Terminal 3: Start the Web Frontend
This launches a quick HTTP server for the web interface.
```bash
cd c:\idea1\vaidya_slm\frontend_pro
python -m http.server 8000
```
*UI Web App: Visit `http://localhost:8000`*

## 🔌 Core API Endpoints (Backend)
- `POST /infer`: Primary generation endpoint. Takes the user's symptoms, runs RAG retrieval against the Ayurvedic knowledge base, and queries the LLM.
- `POST /tts`: Converts the text response into vernacular speech audio.
- `POST /asr`: Processes user voice audio and converts to text via mocked/planned ASR implementation.
- `POST /detect-language`: Used internally for dynamic routing between language pairs.

## 🔮 Future Roadmap
- Fully integrate localized IndicASR/Whisper models to replace the mocked speech-to-text.
- Expand the Ayurvedic RAG chunk database.
- Productionize the Flutter mobile application (`vaidya_slm/frontend`).
