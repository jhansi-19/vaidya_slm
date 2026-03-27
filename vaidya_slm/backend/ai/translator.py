from deep_translator import GoogleTranslator
import time

class IndicTranslator:
    def __init__(self):
        # Supported languages: Telugu, Hindi, English, Marathi, Tamil, Kannada, Malayalam
        self.lang_map = {
            "te": "telugu",
            "hi": "hindi",
            "en": "english",
            "mr": "marathi",
            "ta": "tamil",
            "kn": "kannada",
            "ml": "malayalam"
        }

    def to_english(self, text: str, source_lang: str) -> str:
        if source_lang == "en" or not text:
            return text
        try:
            return GoogleTranslator(source=source_lang, target='en').translate(text)
        except Exception as e:
            print(f"Translation Error (to_en): {e}")
            return text

    def from_english(self, text: str, target_lang: str) -> str:
        if target_lang == "en" or not text:
            return text
        try:
            # GoogleTranslator handles long strings, but for very long ones we might need chunking
            # For our symptoms/remedies, usually it's within limits
            return GoogleTranslator(source='en', target=target_lang).translate(text)
        except Exception as e:
            print(f"Translation Error (from_en): {e}")
            # Add a fallback wait and retry
            time.sleep(1)
            try:
                return GoogleTranslator(source='en', target=target_lang).translate(text)
            except Exception:
                return text

    def from_english_list(self, texts: list, target_lang: str) -> list:
        if target_lang == "en" or not texts:
            return texts
        # Join by double newlines to prevent translation corruption
        combined = "\n\n".join(texts)
        translated_combined = self.from_english(combined, target_lang)
        return [t.strip() for t in translated_combined.split("\n\n")]

# Global singleton
translator = IndicTranslator()
