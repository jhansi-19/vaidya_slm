import os
import subprocess
import sys
from pathlib import Path


def run_checked(cmd, cwd=None):
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def detect_convert_script(llama_cpp_dir: Path) -> Path:
    preferred = llama_cpp_dir / "convert_hf_to_gguf.py"
    legacy = llama_cpp_dir / "convert-hf-to-gguf.py"
    if preferred.exists():
        return preferred
    if legacy.exists():
        return legacy
    raise FileNotFoundError("Could not find convert_hf_to_gguf.py in llama.cpp")


def detect_quantize_binary(llama_cpp_dir: Path) -> Path:
    candidates = [
        llama_cpp_dir / "build" / "bin" / "llama-quantize",
        llama_cpp_dir / "build" / "bin" / "llama-quantize.exe",
        llama_cpp_dir / "build" / "bin" / "quantize",
        llama_cpp_dir / "build" / "bin" / "quantize.exe",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError("Could not find quantization binary in llama.cpp/build/bin")

def main():
    print("====================================")
    print("Vaidya SLM GGUF Export & Quantization")
    print("====================================")

    base_dir = Path(__file__).resolve().parent.parent.parent
    llama_cpp_dir = base_dir / "scripts" / "training" / "llama.cpp"
    models_dir = base_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    if not llama_cpp_dir.exists():
        print("[1/4] Cloning llama.cpp repository...")
        run_checked(["git", "clone", "https://github.com/ggerganov/llama.cpp.git", str(llama_cpp_dir)])

    print("[2/4] Installing llama.cpp requirements...")
    pip_cmd = [sys.executable, "-m", "pip", "install", "-r", str(llama_cpp_dir / "requirements.txt")]
    run_checked(pip_cmd)

    merged_model_dir = base_dir / "scripts" / "training" / "vaidya-slm-merged"
    f16_model = models_dir / "vaidya-slm-1.1b-instruct-f16.gguf"
    q4_model = models_dir / "vaidya-slm-1.1b-instruct-q4_0.gguf"

    if not merged_model_dir.exists():
        print(f"Directory {merged_model_dir} not found.")
        print("Please place merged model files first (output of LoRA merge).")
        return

    print(f"[3/4] Converting HF Model ({merged_model_dir}) to f16 GGUF...")
    convert_script = detect_convert_script(llama_cpp_dir)
    run_checked([
        sys.executable,
        str(convert_script),
        str(merged_model_dir),
        "--outfile",
        str(f16_model),
        "--outtype",
        "f16",
    ])

    print("[4/4] Building llama.cpp quantizer and generating Q4_0 model...")
    run_checked(["cmake", "-B", "build", "-DCMAKE_BUILD_TYPE=Release"], cwd=str(llama_cpp_dir))
    run_checked(["cmake", "--build", "build", "-j4"], cwd=str(llama_cpp_dir))

    quantize_bin = detect_quantize_binary(llama_cpp_dir)
    run_checked([
        str(quantize_bin),
        str(f16_model),
        str(q4_model),
        "Q4_0",
    ])

    print(f"Quantization successful. Edge model saved at: {q4_model}")

if __name__ == "__main__":
    main()
