#!/usr/bin/env python3
"""
Test script to verify TTS functionality for multiple languages.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'vaidya_slm', 'backend'))

from ai.tts import generate_speech

def test_tts_multilingual():
    """Test TTS for multiple languages."""
    
    test_cases = [
        {
            "lang": "en",
            "text": "Hello, this is a test of text to speech in English."
        },
        {
            "lang": "hi",
            "text": "नमस्ते, यह हिंदी में पाठ से भाषण की एक परीक्षा है।"
        },
        {
            "lang": "te",
            "text": "నమస్కారం, ఇది తెలుగులో పాఠం నుండి ప్రసంగ పరీక్ష."
        },
        {
            "lang": "ta",
            "text": "வணக்கம், இது தமிழில் உரையிலிருந்து பேச்சு परीक्षा."
        },
        {
            "lang": "ml",
            "text": "അസലാമുഅലൈകും, ഇത് മലയാളത്തിലെ പാഠത്തിൽ നിന്നുള്ള സ്പീച്ച് ടെസ്റ്റ്."
        }
    ]
    
    output_dir = "test_audio_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("Testing TTS for Multiple Languages")
    print("=" * 80)
    
    for test in test_cases:
        lang = test["lang"]
        text = test["text"]
        audio_file = os.path.join(output_dir, f"test_{lang}.wav")
        
        print(f"\n[TEST] Language: {lang}")
        print(f"Text: {text[:60]}...")
        print(f"Output: {audio_file}")
        
        try:
            success = generate_speech(text, audio_file, lang=lang)
            if success:
                file_size = os.path.getsize(audio_file)
                print(f"Result: SUCCESS - Audio generated ({file_size} bytes)")
            else:
                print(f"Result: FAILED - Could not generate audio")
        except Exception as e:
            print(f"Result: ERROR - {str(e)}")
    
    print("\n" + "=" * 80)
    print("Multi-language TTS Test Complete")
    print("=" * 80)
    print(f"\nAudio files saved in: {output_dir}")
    print("\nSupported Languages:")
    print("  en - English")
    print("  hi - Hindi")
    print("  te - Telugu")
    print("  ta - Tamil")
    print("  ml - Malayalam")
    print("  kn - Kannada")
    print("  gu - Gujarati")
    print("  mr - Marathi")
    print("  bn - Bengali")
    print("  pa - Punjabi")


if __name__ == "__main__":
    test_tts_multilingual()
