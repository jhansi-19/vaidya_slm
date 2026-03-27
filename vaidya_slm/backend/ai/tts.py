from gtts import gTTS
import os
from typing import Optional

def generate_speech(text: str, output_path: str, lang: str = "en") -> bool:
    """
    Generate speech audio file using Google Text-to-Speech (gTTS).
    Supports multiple Indian languages and English with proper script handling.
    
    Args:
        text: Text to convert to speech (supports Telugu script, Hindi script, etc.)
        output_path: Path where audio file will be saved (.mp3 format)
        lang: Language code (en, hi, te, ta, ml, kn, gu, mr, bn, pa)
    
    Returns:
        True if successful, False otherwise
    """
    # Language code mapping for gTTS
    lang_code_map = {
        'en': 'en',      # English
        'hi': 'hi',      # Hindi
        'te': 'te',      # Telugu
        'ta': 'ta',      # Tamil
        'ml': 'ml',      # Malayalam
        'kn': 'kn',      # Kannada
        'gu': 'gu',      # Gujarati
        'mr': 'mr',      # Marathi
        'bn': 'bn',      # Bengali
        'pa': 'pa',      # Punjabi
    }
    
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Get language code, default to English
        gtts_lang = lang_code_map.get(lang.lower(), 'en')
        
        # Create gTTS object with specified language
        # slow=False for normal speed, slow=True for slower speech
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        
        # Change file extension to .mp3 (gTTS generates mp3 files)
        if not output_path.endswith('.mp3'):
            mp3_path = output_path.replace('.wav', '.mp3')
        else:
            mp3_path = output_path
        
        # Save to file
        tts.save(mp3_path)
        
        print(f"TTS: Generated audio for {lang} (gTTS): {mp3_path}")
        return os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 0
        
    except Exception as e:
        print(f"TTS Error ({lang}): {str(e)}")
        return False
