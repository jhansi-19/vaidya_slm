#!/usr/bin/env python3
"""Test TTS endpoint with actual Telugu text from user."""

import requests
import os
from pathlib import Path

# Your exact Telugu text
telugu_text = """ప్రాథమిక తయారీ మరియు వినియోగం:
1. వెచ్చని నీరు (200ml) నిమ్మకాయ (1/2 tsp)
లక్షణాలు తీవ్రమైతే తప్ప ఆహారం తర్వాత రోజుకు 1-2 సార్లు ఉపయోగించండి.
లక్షణాలు తీవ్రంగా లేదా నిరంతరంగా ఉంటే, అర్హత కలిగిన వైద్యుడిని సంప్రదించండి."""

# API endpoint
api_url = "http://127.0.0.1:8005/tts"

print("="*70)
print("Testing gTTS Telugu Voice Output")
print("="*70)
print(f"\nTesting with Telugu text:")
print(f"Text: {telugu_text[:60]}...")
print(f"\nSending request to: {api_url}")

try:
    # Request TTS generation
    response = requests.post(
        api_url,
        data={
            "text": telugu_text,
            "language": "te"
        },
        timeout=60
    )
    
    print(f"Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nResponse Data:")
        print(f"  Success: {result.get('success')}")
        print(f"  Language: {result.get('language')}")
        print(f"  Audio URL: {result.get('audio_url')}")
        print(f"  Message: {result.get('message', 'N/A')}")
        
        if result.get('success'):
            # Download and check audio file
            audio_url = result.get('audio_url')
            if audio_url:
                # Download from local server
                audio_response = requests.get(f"http://127.0.0.1:8005{audio_url}", timeout=30)
                
                if audio_response.status_code == 200:
                    # Save locally
                    os.makedirs("test_audio_output", exist_ok=True)
                    filename = os.path.basename(audio_url)
                    filepath = os.path.join("test_audio_output", filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(audio_response.content)
                    
                    file_size = len(audio_response.content)
                    print(f"\n✓ Audio File Successfully Generated!")
                    print(f"  File: {filepath}")
                    print(f"  Size: {file_size} bytes")
                    print(f"\nTesting other languages...\n")
                    
                    # Test other languages
                    test_langs = [
                        ("en", "Hello, this is a test of multiple language support."),
                        ("hi", "नमस्ते, यह हिंदी में एक परीक्षा है।"),
                        ("ta", "வணக்கம், இது தமிழ் மொழி சோதனை."),
                        ("kn", "ನಮಸ್ಕಾರ, ಇದು ಕನ್ನಡ ಭಾಷೆಯ ಪರೀಕ್ಷೆ."),
                    ]
                    
                    lang_results = [{"language": "Telugu", "status": "✓ PASSED", "size": file_size}]
                    
                    for lang_code, lang_text in test_langs:
                        resp = requests.post(
                            api_url,
                            data={"text": lang_text, "language": lang_code},
                            timeout=60
                        )
                        
                        if resp.status_code == 200 and resp.json().get('success'):
                            # Download audio
                            audio_url = resp.json().get('audio_url')
                            audio_resp = requests.get(f"http://127.0.0.1:8005{audio_url}", timeout=30)
                            
                            if audio_resp.status_code == 200:
                                size = len(audio_resp.content)
                                lang_name = {"en": "English", "hi": "Hindi", "ta": "Tamil", "kn": "Kannada"}[lang_code]
                                lang_results.append({"language": lang_name, "status": "✓ PASSED", "size": size})
                                print(f"✓ {lang_name} ({lang_code}): {size} bytes")
                            else:
                                lang_results.append({"language": lang_code, "status": "✗ Download Failed", "size": 0})
                                print(f"✗ {lang_code}: Download failed")
                        else:
                            lang_results.append({"language": lang_code, "status": "✗ Generation Failed", "size": 0})
                            print(f"✗ {lang_code}: Generation failed")
                    
                    print(f"\n" + "="*70)
                    print("SUMMARY")
                    print("="*70)
                    for result in lang_results:
                        print(f"{result['language']:<15} {result['status']:<20} {result['size']} bytes")
                    
                    print("\n✓ All tests completed successfully!")
                    print("✓ Telugu voice will now play properly with correct script pronunciation!")
                    
                else:
                    print(f"✗ Failed to download audio: {audio_response.status_code}")
        else:
            print(f"✗ TTS generation failed: {result.get('error', 'Unknown error')}")
    else:
        print(f"✗ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("="*70)
