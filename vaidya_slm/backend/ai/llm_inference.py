import os
import subprocess
import requests
import json
import time
from typing import Optional
from .rag import get_rag  # RAG integration for knowledge-enhanced responses


class GGUFLLMHost:
    def __init__(self, model_path: str, cli_path: Optional[str] = None):
        self.model_path = os.path.abspath(model_path)
        self.cli_path = self._resolve_cli_path(cli_path)
        self._python_runtime = None
        self._runtime_error = None
        self.server_url = "http://127.0.0.1:8008"
        self._server_warmed_up = False
        self._first_server_query_done = False

        try:
            from llama_cpp import Llama  # type: ignore

            self._python_runtime = Llama(
                model_path=self.model_path,
                n_ctx=1024,
                n_threads=4,
                verbose=False,
            )
        except Exception as exc:
            self._runtime_error = str(exc)

    def _resolve_cli_path(self, cli_path: Optional[str]) -> Optional[str]:
        if cli_path and os.path.exists(cli_path):
            return os.path.abspath(cli_path)

        env_cli = os.getenv("LLAMA_CLI_PATH")
        if env_cli and os.path.exists(env_cli):
            return os.path.abspath(env_cli)

        candidates = [
            r"c:\idea1\tools\llama-cpp-bin\llama-cli.exe",
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "llama-cpp-bin", "llama-cli.exe"),
            os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "training", "llama.cpp", "build", "bin", "llama-cli.exe"),
            os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "training", "llama.cpp", "build", "bin", "llama-cli"),
            os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "training", "llama.cpp", "build", "bin", "main.exe"),
            os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "training", "llama.cpp", "build", "bin", "main"),
        ]
        for candidate in candidates:
            abs_candidate = os.path.abspath(candidate)
            if os.path.exists(abs_candidate):
                return abs_candidate
        return None

    def is_model_ready(self) -> bool:
        return os.path.exists(self.model_path)

    def is_runtime_available(self) -> bool:
        return self._python_runtime is not None or self.cli_path is not None
    
    def _is_server_ready(self, timeout: int = 5) -> bool:
        """Check if llama-server is ready to accept requests."""
        try:
            resp = requests.get(f"{self.server_url}/health", timeout=timeout)
            return resp.status_code == 200
        except Exception:
            return False
    
    def _wait_for_server_ready(self, max_wait: int = 30) -> bool:
        """Wait for llama-server to be ready with exponential backoff."""
        start_time = time.time()
        wait_time = 0.5
        max_wait_time = 5
        
        while time.time() - start_time < max_wait:
            if self._is_server_ready(timeout=2):
                return True
            time.sleep(wait_time)
            wait_time = min(wait_time * 1.5, max_wait_time)
        
        return False
    
    def _warm_up_server(self) -> None:
        """Send a dummy request to warm up the model on first use."""
        if self._server_warmed_up:
            return
        
        try:
            if not self._wait_for_server_ready():
                print("DEBUG: Llama-server not ready after waiting. Proceeding anyway...")
                
            # Send a warm-up request with minimal content
            system_prompt = (
                "You are Vaidya SLM, an expert Ayurvedic assistant. "
                "Return ONLY valid JSON with keys: dosha, dosha_confidence, dosha_reason, primary_remedy, natural_remedies, lifestyle, dietary."
            )
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Hi"}
                ],
                "max_tokens": 50,
                "temperature": 0.2,
            }
            response = requests.post(
                f"{self.server_url}/v1/chat/completions",
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                self._server_warmed_up = True
                print("DEBUG: Llama-server warmed up successfully")
            else:
                print(f"DEBUG: Warm-up returned status {response.status_code}")
        except Exception as e:
            print(f"DEBUG: Warm-up request failed: {str(e)}")

    def status(self):
        server_ready = False
        try:
            resp = requests.get(f"{self.server_url}/health", timeout=1)
            server_ready = resp.status_code == 200
        except:
            pass

        return {
            "model_path": self.model_path,
            "model_exists": self.is_model_ready(),
            "python_runtime": self._python_runtime is not None,
            "cli_path": self.cli_path,
            "server_live": server_ready,
            "runtime_error": self._runtime_error,
        }

    def _build_prompt(self, user_text: str, lang: str = "en") -> str:
        # Prompt instructs model to return structured JSON for robust parsing.
        return (
            "<start_of_turn>user\n"
            "Provide a comprehensive Ayurvedic response as strict JSON with keys:\n"
            "dosha (one of: Vata, Pitta, Kapha, Vata-Pitta, Pitta-Kapha, Vata-Kapha, Tridosha, Unknown),\n"
            "dosha_confidence (0 to 1 number), dosha_reason (short string),\n"
            "primary_remedy (string), natural_remedies (array of 3-6 strings), "
            "lifestyle (array of 3-5 strings), dietary (array of 3-5 strings).\n"
            "primary_remedy must include clear preparation and usage steps (quantity, frequency, timing).\n"
            "No markdown, no prose outside JSON. If symptoms are severe, include immediate doctor consultation in primary_remedy.\n\n"
            f"Language: {lang}\n"
            f"User symptoms: {user_text}<end_of_turn>\n"
            "<start_of_turn>model\n"
        )

    def _query_server(self, user_text: str, lang: str = "en") -> Optional[str]:
        # Warm up the server on first query
        if not self._first_server_query_done:
            self._warm_up_server()
            self._first_server_query_done = True
        
        try:
            # Retrieve relevant Ayurvedic knowledge using RAG
            rag = get_rag()
            augmented_text, retrieved_chunks = rag.augment_query(user_text, top_k=3)
            
            # Comprehensive system prompt ensuring complete output
            system_prompt = (
                "You are Vaidya SLM, an expert Ayurvedic assistant with deep knowledge of Ayurveda. "
                "Your response MUST be ONLY valid JSON (no markdown, no extra text) with exactly these keys: "
                "dosha, dosha_confidence, dosha_reason, primary_remedy, natural_remedies, lifestyle, dietary.\n\n"
                
                "CRITICAL REQUIREMENTS:\n"
                "1. dosha: MUST be exactly one of [Vata, Pitta, Kapha, Vata-Pitta, Pitta-Kapha, Vata-Kapha, Tridosha, Unknown]\n"
                "2. dosha_confidence: MUST be a number from 0.0 to 1.0 (never empty)\n"
                "3. dosha_reason: MUST be a clear, concise explanation (minimum 10 words)\n"
                "4. primary_remedy: MUST include preparation method, dosage, frequency, and timing (never empty or generic)\n"
                "5. natural_remedies: MUST be a JSON array with 4-6 specific remedies (never empty), format: [\"item (dose)\", \"item (dose)\"]\n"
                "6. lifestyle: MUST be a JSON array with 4-5 specific lifestyle recommendations (never empty)\n"
                "7. dietary: MUST be a JSON array with 4-5 specific dietary items/guidelines (never empty)\n\n"
                
                "FORMATTING RULES:\n"
                "- ALL arrays MUST use valid JSON format with double quotes\n"
                "- ALL text MUST use double quotes for string values\n"
                "- NO markdown, NO prose, ONLY valid JSON\n"
                "- EVERY field MUST be populated (no null, no empty values)\n\n"
                
                "OUTPUT ONLY THE JSON OBJECT, NOTHING ELSE."
            )
            
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": augmented_text}  # Use RAG-augmented query
                ],
                "max_tokens": 1000,
                "temperature": 0.2,
                "top_p": 0.9,
                "frequency_penalty": 0.5,
                "presence_penalty": 0.2
            }
            # Use /v1/chat/completions for better model adherence
            response = requests.post(f"{self.server_url}/v1/chat/completions", json=payload, timeout=60)
            if response.status_code == 200:
                content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                if content and len(content) > 10:  # Validate response has meaningful content
                    return content
                else:
                    print(f"DEBUG: Llama-server returned empty/short chat response. Full response: {response.text}")
            else:
                print(f"DEBUG: Llama-server chat status {response.status_code}. Response: {response.text}")
        except Exception as e:
            print(f"DEBUG: Exception during llama-server chat query: {str(e)}")
        return None

    def _query_python_runtime(self, prompt: str) -> str:
        output = self._python_runtime(
            prompt,
            max_tokens=180,
            temperature=0.2,
            stop=["\n\nUser", "###"],
        )
        return output["choices"][0]["text"].strip()

    def _query_cli_runtime(self, prompt: str) -> str:
        command = [
            self.cli_path,
            "-m",
            self.model_path,
            "-p",
            prompt,
            "-n",
            "180",
            "--temp",
            "0.2",
        ]
        process = subprocess.run(command, capture_output=True, text=True, check=False)
        if process.returncode != 0:
            raise RuntimeError(process.stderr.strip() or "llama.cpp cli failed")
        text = process.stdout.strip()
        return text[-1000:].strip()

    def query(self, user_text: str, lang: str = "en") -> str:
        if not self.is_model_ready():
            return f"Model file not found. Please verify {self.model_path}."

        # Try persistent server first (Chat API)
        response = self._query_server(user_text, lang)
        if response:
            return response

        # Fallback to local runtimes
        prompt = self._build_prompt(user_text, lang)

        # Fallback to python runtime
        try:
            if self._python_runtime is not None:
                response = self._query_python_runtime(prompt)
                if response:
                    return response
        except Exception:
            pass

        # Fallback to CLI (Slowest)
        try:
            if self.cli_path is not None:
                response = self._query_cli_runtime(prompt)
                if response:
                    return response
        except Exception:
            pass

        return "Model runtime unavailable. Install llama-cpp-python or build llama.cpp binary for local inference."


DEFAULT_MODEL_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "models",
        "gemma-2-2b-it.Q4_K_M.gguf",
    )
)

llm_host = GGUFLLMHost(model_path=DEFAULT_MODEL_PATH)
