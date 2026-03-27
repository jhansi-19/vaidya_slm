from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import ast
import json
import re
from typing import Any, Dict, List, Optional
import uvicorn
import os
from datetime import datetime
from ai.llm_inference import llm_host
from ai.translator import translator
from ai.tts import generate_speech

app = FastAPI(title="Vaidya SLM API", version="1.0", description="Backend for the Ayurvedic AI for Bharat")

# Serve static files (audio, etc.) from static directory
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
os.makedirs(static_dir, exist_ok=True)
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InferenceRequest(BaseModel):
    text: str
    language: str = "en"


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _extract_list_items(block: str) -> List[str]:
    items: List[str] = []
    for line in (block or "").splitlines():
        cleaned = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line).strip()
        if cleaned:
            items.append(cleaned)

    if items:
        return items

    # Fallback when model returns inline prose instead of bullets.
    candidates = [s.strip() for s in re.split(r"(?<=[.!?])\s+", _clean_text(block)) if s.strip()]
    return candidates[:6]


def _to_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [_clean_text(str(v)) for v in value if _clean_text(str(v))]
    if isinstance(value, str) and value.strip():
        return _extract_list_items(value)
    return []


def _normalize_dosha(dosha_value: str) -> str:
    value = _clean_text((dosha_value or "").lower())
    if not value:
        return "Unknown"

    canonical_map = {
        "vata": "Vata",
        "pitta": "Pitta",
        "kapha": "Kapha",
        "vata-pitta": "Vata-Pitta",
        "pitta-vata": "Vata-Pitta",
        "vata-kapha": "Vata-Kapha",
        "kapha-vata": "Vata-Kapha",
        "pitta-kapha": "Pitta-Kapha",
        "kapha-pitta": "Pitta-Kapha",
        "tridosha": "Tridosha",
        "tri-dosha": "Tridosha",
        "unknown": "Unknown",
    }
    return canonical_map.get(value, dosha_value.strip() or "Unknown")


def _normalize_remedy_text(remedy_text: str, remedies: List[str], lifestyle: List[str], dietary: List[str]) -> str:
    text = _clean_text(remedy_text)

    def _build_instructions(items: List[str]) -> str:
        lines = ["Primary preparation and usage:"]
        for idx, item in enumerate(items[:4], 1):
            lines.append(f"{idx}. {item}")
        lines.append("Use 1-2 times daily after food unless symptoms worsen.")
        lines.append("If symptoms are severe or persistent, consult a qualified doctor.")
        return "\n".join(lines)

    if text.startswith("[") and text.endswith("]"):
        parsed_items: List[str] = []
        try:
            maybe_json = json.loads(text)
            if isinstance(maybe_json, list):
                parsed_items = [_clean_text(str(v)) for v in maybe_json if _clean_text(str(v))]
        except Exception:
            try:
                maybe_py = ast.literal_eval(text)
                if isinstance(maybe_py, list):
                    parsed_items = [_clean_text(str(v)) for v in maybe_py if _clean_text(str(v))]
            except Exception:
                parsed_items = []

        if parsed_items:
            return _build_instructions(parsed_items)

    if len(text) < 40 and remedies:
        return _build_instructions(remedies)

    if not text and remedies:
        return _build_instructions(remedies)

    # If remedy text exists but no practical "how to use", append concise guidance from available sections.
    has_how_to = bool(re.search(r"(?i)\b(mix|boil|take|drink|apply|twice|daily|after|before)\b", text))
    if not has_how_to:
        additions: List[str] = []
        if remedies:
            additions.append(f"How to use: {remedies[0]}")
        if lifestyle:
            additions.append(f"Lifestyle support: {lifestyle[0]}")
        if dietary:
            additions.append(f"Diet support: {dietary[0]}")
        if additions:
            return text + "\n\n" + "\n".join(additions)

    return text


def _fix_malformed_json(json_str: str) -> Optional[dict]:
    """Attempt to fix common JSON malformations from LLM output."""
    
    # First, try direct parsing
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Fix 1: Unquoted array items - [Ginger (1g), Warm water (200ml)] -> ["Ginger (1g)", "Warm water (200ml)"]
    def fix_unquoted_arrays(text):
        """Find and fix all arrays with unquoted items."""
        # Find all array patterns
        array_pattern = r'\[([^\[\]]*)\]'
        
        def fix_array_content(match):
            array_content = match.group(1)
            
            # Check if array already has properly quoted items
            if array_content.count('"') > array_content.count(','):
                # Likely already quoted
                return match.group(0)
            
            # Split by comma, respecting parentheses
            items = []
            current_item = ""
            paren_depth = 0
            in_quotes = False
            
            for i, char in enumerate(array_content):
                if char == '"' and (i == 0 or array_content[i-1] != '\\'):
                    in_quotes = not in_quotes
                    current_item += char
                elif char == '(' and not in_quotes:
                    paren_depth += 1
                    current_item += char
                elif char == ')' and not in_quotes:
                    paren_depth -= 1
                    current_item += char
                elif char == ',' and paren_depth == 0 and not in_quotes:
                    item = current_item.strip()
                    if item:
                        # Quote unquoted items
                        if not (item.startswith('"') and item.endswith('"')):
                            item = f'"{item}"'
                        items.append(item)
                    current_item = ""
                else:
                    current_item += char
            
            # Don't forget the last item
            if current_item.strip():
                item = current_item.strip()
                if not (item.startswith('"') and item.endswith('"')):
                    item = f'"{item}"'
                items.append(item)
            
            if items:
                return '[' + ', '.join(items) + ']'
            return match.group(0)
        
        return re.sub(array_pattern, fix_array_content, text)
    
    json_str = fix_unquoted_arrays(json_str)
    
    # Fix 2: Close unclosed arrays and objects
    fixed_str = json_str.rstrip(", \n")
    
    # Fix unclosed quotes
    quote_count = fixed_str.count('"') - fixed_str.count('\\"')
    if quote_count % 2 != 0:
        fixed_str += '"'
    
    # Fix unclosed brackets
    bracket_diff = fixed_str.count('[') - fixed_str.count(']')
    if bracket_diff > 0:
        fixed_str += ']' * bracket_diff
    
    # Fix unclosed braces
    brace_diff = fixed_str.count('{') - fixed_str.count('}')
    if brace_diff > 0:
        fixed_str += '}' * brace_diff
    
    # Try parsing the fixed JSON
    try:
        return json.loads(fixed_str)
    except json.JSONDecodeError:
        pass
    
    return None


def _extract_model_sections(model_text: str) -> Dict[str, Any]:
    parsed = {
        "dosha": "Unknown",
        "dosha_confidence": 0.0,
        "dosha_reason": "",
        "remedy": "",
        "remedies": [],
        "lifestyle": [],
        "dietary": [],
    }

    # Best-case: model follows JSON schema.
    # Clean out markdown code blocks and internal unquoted strings if present
    cleaned_model_text = re.sub(r"```json|```", "", model_text or "").strip()
    
    json_match = re.search(r"\{[\s\S]*\}", cleaned_model_text)
    if json_match:
        json_str = json_match.group(0)
        
        # Try to fix and parse JSON using improved logic
        obj = _fix_malformed_json(json_str)

        if isinstance(obj, dict):
            parsed["dosha"] = _normalize_dosha(str(obj.get("dosha") or obj.get("predicted_dosha") or "Unknown"))
            try:
                parsed["dosha_confidence"] = float(obj.get("dosha_confidence") or 0.0)
            except Exception:
                parsed["dosha_confidence"] = 0.0
            parsed["dosha_reason"] = _clean_text(str(obj.get("dosha_reason") or obj.get("reason") or ""))
            parsed["remedy"] = _clean_text(str(obj.get("primary_remedy") or obj.get("remedy") or ""))
            parsed["remedies"] = _to_list(obj.get("natural_remedies") or obj.get("remedies") or [])
            parsed["lifestyle"] = _to_list(obj.get("lifestyle") or obj.get("lifestyle_changes") or [])
            parsed["dietary"] = _to_list(obj.get("dietary") or obj.get("diet") or obj.get("dietary_changes") or [])
        else:
            # If JSON parsed but wasn't a dict, clear text for fallback
            cleaned_model_text = ""
            
    # Stop fallback from parsing raw invalid JSON string as plain text
    if json_match and (parsed["remedy"] or parsed["remedies"]):
        pass
    elif json_match and not parsed["remedy"]:
        # If it was attempted JSON but failed, clear text so fallback doesn't output raw JSON.
        cleaned_model_text = ""

    if parsed["remedy"] or parsed["remedies"] or parsed["lifestyle"] or parsed["dietary"] or parsed["dosha"] != "Unknown":
        return parsed

    # Fallback parser for heading-based plain text responses.
    text = cleaned_model_text or ""
    heading_re = re.compile(
        r"(?im)^\s*(dosha|primary remedy|natural remedies?|natural medications?|lifestyle(?:\s*&\s*diet(?:ary)?|\s*and\s*diet(?:ary)?)?|diet(?:ary)?(?:\s*changes?)?)\s*:?\s*$"
    )
    matches = list(heading_re.finditer(text))

    if matches:
        for idx, match in enumerate(matches):
            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            block = text[start:end].strip()
            heading = match.group(1).lower()

            if heading == "dosha":
                parsed["dosha"] = _normalize_dosha(block.splitlines()[0] if block else "Unknown")
            elif "primary" in heading:
                parsed["remedy"] = _clean_text(block)
            elif "natural" in heading:
                parsed["remedies"] = _extract_list_items(block)
            elif "diet" in heading and "lifestyle" in heading:
                combined = _extract_list_items(block)
                midpoint = max(1, len(combined) // 2)
                parsed["lifestyle"] = combined[:midpoint]
                parsed["dietary"] = combined[midpoint:]
            elif "lifestyle" in heading:
                parsed["lifestyle"] = _extract_list_items(block)
            elif "diet" in heading:
                parsed["dietary"] = _extract_list_items(block)

    if not parsed["remedy"]:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", _clean_text(text)) if s.strip()]
        parsed["remedy"] = sentences[0] if sentences else _clean_text(text)
        if not parsed["remedies"]:
            parsed["remedies"] = sentences[1:4]
        if not parsed["lifestyle"]:
            parsed["lifestyle"] = sentences[4:7]
        if not parsed["dietary"]:
            parsed["dietary"] = sentences[7:10]

    if parsed["dosha"] == "Unknown":
        dosha_inline = re.search(r"(?i)\b(vata|pitta|kapha|tridosha)\b", text)
        if dosha_inline:
            parsed["dosha"] = _normalize_dosha(dosha_inline.group(1))

    return parsed

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Vaidya SLM Backend is running."}

@app.get("/model-status")
def model_status():
    return llm_host.status()

@app.post("/asr")
async def asr_endpoint(audio: UploadFile = File(...)):
    # Simulating OpenAI Whisper / AI4Bharat IndicASR pipeline
    return {"transcription": "I have acidity and headache", "detected_language": "en"}

@app.post("/detect-language")
def detect_lang(request: InferenceRequest):
    # Simulating HuggingFace Language Detection
    return {"language": "en", "confidence": 0.99}

@app.post("/infer")
def infer(request: InferenceRequest):
    source_lang = request.language

    # Step 1: Translate input to English if needed
    english_query = translator.to_english(request.text, source_lang)

    # Step 2: Model-only inference (Gemma).
    model_response = llm_host.query(english_query, "en")
    structured = _extract_model_sections(model_response)

    is_model_unavailable = (
        "Model file not found" in model_response
        or "runtime unavailable" in model_response.lower()
        or "unavailable" in model_response.lower()
    )

    remedies_en = structured["remedies"][:6]
    lifestyle_en = structured["lifestyle"][:5]
    dietary_en = structured["dietary"][:5]
    final_remedy_en = _normalize_remedy_text(structured["remedy"] or model_response, remedies_en, lifestyle_en, dietary_en)
    final_dosha = _normalize_dosha(structured.get("dosha", "Unknown"))
    dosha_confidence = float(structured.get("dosha_confidence", 0.0) or 0.0)

    reason = "Model-only response generated from Gemma."
    if structured.get("dosha_reason"):
        reason = f"{reason} Dosha reasoning: {structured['dosha_reason']}"
    if is_model_unavailable:
        reason = "Model-only mode enabled, but Gemma runtime is unavailable."

    # Step 4: Translate EVERYTHING back to the source language
    final_remedy = translator.from_english(final_remedy_en, source_lang)

    # Translate lists in bulk to avoid rate limiting
    translated_remedies = translator.from_english_list(remedies_en, source_lang)
    translated_lifestyle = translator.from_english_list(lifestyle_en, source_lang)
    translated_dietary = translator.from_english_list(dietary_en, source_lang)

    return {
        "input": request.text,
        "dosha": final_dosha,
        "dosha_confidence": round(max(0.0, min(1.0, dosha_confidence)), 3),
        "reason": reason,
        "remedy": final_remedy,
        "remedies": translated_remedies,
        "lifestyle": translated_lifestyle,
        "dietary": translated_dietary,
        "model_used": not is_model_unavailable
    }

@app.post("/dosha")
def get_dosha(request: InferenceRequest):
    source_lang = request.language
    english_query = translator.to_english(request.text, source_lang)
    model_response = llm_host.query(english_query, "en")
    structured = _extract_model_sections(model_response)
    dosha = _normalize_dosha(structured.get("dosha", "Unknown"))
    confidence = float(structured.get("dosha_confidence", 0.0) or 0.0)
    return {
        "dosha": dosha,
        "dosha_confidence": round(max(0.0, min(1.0, confidence)), 3),
        "model_used": "unavailable" not in model_response.lower()
    }

@app.post("/remedy")
def get_remedy(request: InferenceRequest):
    source_lang = request.language
    english_query = translator.to_english(request.text, source_lang)
    model_response = llm_host.query(english_query, "en")
    structured = _extract_model_sections(model_response)
    remedy_en = structured["remedy"] or model_response
    return {"remedy": translator.from_english(remedy_en, source_lang)}

@app.post("/tts")
def tts_endpoint(text: str = Form(...), language: str = Form(default="en")):
    """
    Text-to-Speech endpoint supporting multiple languages.
    Generates .wav audio files for the given text in the specified language.
    """
    try:
        if not text or len(text.strip()) == 0:
            return {
                "success": False,
                "error": "Text cannot be empty",
                "audio_url": None
            }
        
        # Create output directory if it doesn't exist
        audio_dir = os.path.join(os.path.dirname(__file__), "..", "static", "audio")
        os.makedirs(audio_dir, exist_ok=True)
        
        # Generate unique filename with timestamp and language code
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        audio_filename = f"response_{language}_{timestamp}.mp3"
        audio_path = os.path.join(audio_dir, audio_filename)
        
        # Generate audio
        success = generate_speech(text, audio_path, lang=language)
        
        if success and os.path.exists(audio_path):
            # Return relative URL path for frontend to access
            audio_url = f"/static/audio/{audio_filename}"
            return {
                "success": True,
                "audio_url": audio_url,
                "language": language,
                "message": f"TTS generated successfully for {language}."
            }
        else:
            return {
                "success": False,
                "error": "Failed to generate audio file",
                "audio_url": None,
                "language": language
            }
    
    except Exception as e:
        print(f"TTS Endpoint Error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "audio_url": None
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
