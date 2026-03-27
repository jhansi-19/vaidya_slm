import os
import requests
import subprocess
import zipfile
from pathlib import Path

def download_file(url, output_path):
    print(f"Downloading {url} to {output_path}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data" / "raw"
    data_dir.mkdir(parents=True, exist_ok=True)
    use_kaggle = os.getenv("USE_KAGGLE", "0") == "1"
    
    # 1. Classical Ayurvedic Texts from Archive.org
    datasets = {
        "charaka_samhita.pdf": "https://archive.org/download/CharakaSamhitaVol1/CharakaSamhitaVol1_text.pdf",
        "sushruta_samhita.pdf": "https://archive.org/download/sushrutasamhita00kunjgoog/sushrutasamhita00kunjgoog_bw.pdf", 
        "ashtanga_hridayam.pdf": "https://archive.org/download/AsthangaHridayamSanskritEnglsih/AsthangaHridayam%20Sanskrit%20%20Englsih.pdf"
    }

    print("--- Phase 1: Downloading Primary Data References ---")
    for filename, url in datasets.items():
        output_file = data_dir / filename
        if not output_file.exists():
            download_file(url, output_file)
        else:
            print(f"{filename} already exists. Skipping download.")

    # 2. Kaggle dataset: optional, disabled by default.
    # Use USE_KAGGLE=1 only if credentials are configured and the dataset is reachable.
    if use_kaggle:
        print("\n--- Phase 2: Downloading Kaggle Ayurvedic Herbs ---")
        print("Requires Kaggle CLI configured (~/.kaggle/kaggle.json).")
        try:
            subprocess.run([
                "kaggle", "datasets", "download",
                "-d", "harshavardhan21/ayurvedic-herbs",
                "-p", str(data_dir), "--unzip"
            ], check=True)
            print("Successfully unzipped Ayurvedic Herbs database.")
        except Exception as e:
            print(f"[Warning]: Kaggle download failed. Continuing with Hugging Face data path. {e}")
    else:
        print("\n--- Phase 2: Kaggle download skipped ---")
        print("Set USE_KAGGLE=1 to enable Kaggle dataset download.")

    # 3. Hugging Face-first data path.
    print("\n--- Phase 3: Hugging Face data path ---")
    print("Primary supervised dataset generation is handled in preprocess_ayurvedic.py via Hugging Face.")
    print("Archive/Kaggle files are optional enrichment sources.")

if __name__ == "__main__":
    main()
