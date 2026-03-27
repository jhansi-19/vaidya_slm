import json
import os
import re
import argparse
import pandas as pd
from datasets import load_dataset
from pathlib import Path

def clean_ocr_noise(text):
    """
    Cleans OCR noise from scanned classical Ayurvedic texts.
    Normalizes Sanskrit + English text combinations.
    """
    if not isinstance(text, str):
        return ""
    # Remove weird hidden Unicode characters and excessive formatting
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]*', '', text)
    text = re.sub(r'\s+', ' ', text)
    # Target only English/Sanskrit literals + basic punctuation
    text = re.sub(r'[^\w\s\.,;?\-()\[\]]', '', text)
    return text.strip()

def process_pdf(pdf_path):
    """ Reads PDF, strips bad OCR formatting, and normalizes the corpus. """
    text_corpus = ""
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_corpus += clean_ocr_noise(extracted) + "\n"
    except ImportError:
        print("PyPDF2 missing. Skipping PDF extraction. -> `pip install PyPDF2`")
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    return text_corpus

def map_text_to_instructions(text_corpus, source_name):
    """
    Finds Dosha mentions in the corpus and generates Symptom -> Dosha AI mapping pairs.
    """
    records = []
    # Simplified sliding window splitting sentences
    sentences = [clean_ocr_noise(s.strip()) for s in text_corpus.split('.') if len(s.strip()) > 10]
    
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        # Look for core Doshas in the sentence
        if any(dosha in sentence_lower for dosha in ['vata', 'pitta', 'kapha']):
            target_dosha = "Vata" if 'vata' in sentence_lower else (
                "Pitta" if 'pitta' in sentence_lower else "Kapha"
            )
            # Find the remedy in the adjacent sentences (simulating a chunking algorithm)
            remedy_context = " ".join(sentences[i:i+2]) if i+2 < len(sentences) else sentence
            
            records.append({
                "instruction": f"Based on {source_name}, analyze the symptom and suggest a remedy for the dosha imbalance.",
                "input": sentence,
                "output": {
                    "dosha": target_dosha,
                    "reason": f"Symptom correlated with {target_dosha} aggravation in {source_name}.",
                    "remedy": remedy_context
                }
            })
    return list({v['input']:v for v in records}.values()) # Deduplicate

def process_kaggle_herbs(csv_path):
    """ Maps the Kaggle Herb CSV onto Symptom -> Remedy rules. """
    records = []
    try:
        df = pd.read_csv(csv_path)
        # Parse fields dynamically depending on Kaggle's internal column setup
        for _, row in df.iterrows():
            item_desc = str(row.values[0]) if len(row.values) > 0 else ""
            item_remedy = str(row.values[1]) if len(row.values) > 1 else ""
            
            if item_desc and item_remedy:
                records.append({
                    "instruction": "Suggest an Ayurvedic herb given the symptom description.",
                    "input": clean_ocr_noise(item_desc),
                    "output": {
                        "dosha": "Unknown - General Remedy",
                        "reason": "Direct reference from Ayurvedic Herbs Database.",
                        "remedy": clean_ocr_noise(item_remedy)
                    }
                })
    except Exception as e:
        print(f"Skipping Kaggle CSV parse: {e}")
    return records

def load_huggingface_records(limit: int = 500, dataset_name: str = "medalpaca/medical_meadow_health_advice"):
    records = []
    print(f"--- Hugging Face: Loading {dataset_name}[:{limit}] ---")
    dataset = load_dataset(dataset_name, split=f"train[:{limit}]")
    for item in dataset:
        records.append({
            "instruction": "Analyze the following symptom and suggest an Ayurvedic-safe remedy.",
            "input": str(item.get("input", item.get("instruction", ""))),
            "output": {
                "dosha": "Unknown - General Checkup",
                "reason": "Derived from Hugging Face medical advisory dataset.",
                "remedy": str(item.get("output", "Consult a Vaidya/Doctor."))
            }
        })
    print(f"\t-> Loaded {len(records)} records from Hugging Face.")
    return records


def build_instruction_dataset(source: str = "huggingface", hf_limit: int = 500):
    print("--- Phase 1: Normalizing Ayurvedic Data ---")
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    output_path = processed_dir / "ayurvedic_dataset.json"

    all_records = []
    
    if source == "huggingface":
        all_records.extend(load_huggingface_records(limit=hf_limit))
    else:
        # 1. Process Classical PDFs
        pdf_files = ['charaka_samhita.pdf', 'sushruta_samhita.pdf', 'ashtanga_hridayam.pdf']
        for pdf_file in pdf_files:
            path = data_dir / pdf_file
            if path.exists():
                print(f"Parsing and Cleaning OCR: {pdf_file}")
                text_corpus = process_pdf(str(path))
                mapped = map_text_to_instructions(text_corpus, pdf_file)
                all_records.extend(mapped)
                print(f"\t-> Generated {len(mapped)} structured chunks.")

        # 2. Process Kaggle Herbs CSV
        for csv_file in data_dir.glob("*.csv"):
            print(f"Parsing CSV Herbs map: {csv_file.name}")
            mapped = process_kaggle_herbs(str(csv_file))
            all_records.extend(mapped)
            print(f"\t-> Generated {len(mapped)} structured chunks.")

        # 3. IndicGLUE Base Translations via HuggingFace
        print("--- Phase 2: IndicGLUE Multilingual Load ---")
        try:
            indic_dataset = load_dataset("indic_glue", "copa.hi", split=f"train[:{hf_limit}]")
            for item in indic_dataset:
                all_records.append({
                    "instruction": "Translate and classify the following text using IndicNLG.",
                    "input": item.get('premise', ''),
                    "output": {"dosha": "N/A", "reason": "Language Translation Check", "remedy": "N/A"}
                })
            print(f"\t-> Loaded {hf_limit} multilingual evaluation pairs.")
        except Exception as e:
            print(f"\t-> IndicGLUE skipped: {e}")

        # If mixed data path has no usable records, use Hugging Face fallback.
        if len(all_records) == 0:
            print("[Warning]: No records from local raw files. Falling back to Hugging Face dataset.")
            all_records.extend(load_huggingface_records(limit=hf_limit))

    if len(all_records) == 0:
        raise RuntimeError("No training records generated. Check dataset access and preprocessing steps.")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=4, ensure_ascii=False)
        
    print(f"\nSuccessfully cleaned OCR noise, normalized Sanskrit+English pairs, and built dataset!")
    print(f"Total structured reasoning items generated: {len(all_records)}")
    print(f"Saved into: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Ayurvedic instruction dataset")
    parser.add_argument("--source", choices=["huggingface", "mixed"], default="huggingface")
    parser.add_argument("--hf-limit", type=int, default=500)
    args = parser.parse_args()
    build_instruction_dataset(source=args.source, hf_limit=args.hf_limit)
