#!/usr/bin/env python3
"""Test gTTS for proper Telugu and multi-language support."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'vaidya_slm', 'backend'))

from ai.tts import generate_speech
import shutil

# Create test output directory
test_dir = "test_audio_gtts"
if os.path.exists(test_dir):
    shutil.rmtree(test_dir)
os.makedirs(test_dir)

print("="*70)
print("Testing gTTS for Multi-Language Support (Proper Script Handling)")
print("="*70)

# Test cases with actual script text
test_cases = [
    {
        "language": "te",
        "lang_name": "Telugu",
        "text": "ప్రాథమిక తయారీ మరియు వినియోగం: ఎక్కువ నీరు అవసరం. గోరువెచ్చని నీరు రెండు వందల మిల్లీలీటర్."
    },
    {
        "language": "en",
        "lang_name": "English",
        "text": "Basic preparation and consumption: Warm water two hundred milliliters with half teaspoon of lemon."
    },
    {
        "language": "hi",
        "lang_name": "Hindi",
        "text": "बुनियादी तैयारी और खपत: गर्म पानी दो सौ मिलीलीटर आधा चम्मच नींबू के साथ।"
    },
    {
        "language": "ta",
        "lang_name": "Tamil",
        "text": "அடிப்படை தயாரிப்பு மற்றும் நுகர்வு: சூடான நீர் இருநூறு மில்லிலிட்டர் அரை ஸ்பூன் எலுமிச்சை கொண்டு।"
    },
    {
        "language": "kn",
        "lang_name": "Kannada",
        "text": "ಮೂಲಭೂತ ತಯಾರಿ ಮತ್ತು ಬಳಕೆ: ಬೆಚ್ಚಗನ ನೀರು ಎರಡುನೂರು ಮಿಲಿಲೀಟರ್ ಅರ್ಧ ಸ್ಪೂನ್ ನಿಂಬೆಯೊಂದಿಗೆ।"
    }
]

# Run tests
print("\nGenerating audio files with proper language support:\n")
results = []

for idx, test in enumerate(test_cases, 1):
    lang_code = test["language"]
    lang_name = test["lang_name"]
    text = test["text"]
    
    output_file = os.path.join(test_dir, f"test_{lang_code}.mp3")
    
    print(f"[TEST {idx}] Language: {lang_name} ({lang_code})")
    print(f"  Text: {text[:50]}...")
    print(f"  Output: {output_file}")
    
    try:
        success = generate_speech(text, output_file, lang=lang_code)
        
        if success and os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            results.append({
                "language": lang_name,
                "code": lang_code,
                "status": "✓ PASSED",
                "file_size": file_size,
                "file": output_file
            })
            print(f"  Result: ✓ SUCCESS - Audio generated ({file_size} bytes)\n")
        else:
            results.append({
                "language": lang_name,
                "code": lang_code,
                "status": "✗ FAILED",
                "file_size": 0,
                "file": output_file
            })
            print(f"  Result: ✗ FAILED - Audio not generated\n")
    except Exception as e:
        results.append({
            "language": lang_name,
            "code": lang_code,
            "status": f"✗ ERROR: {str(e)[:40]}",
            "file_size": 0,
            "file": output_file
        })
        print(f"  Result: ✗ ERROR - {str(e)}\n")

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print(f"\n{'Language':<15} {'Code':<6} {'Status':<40} {'Size':<10}")
print("-" * 71)
for result in results:
    status = result["status"]
    size_str = f"{result['file_size']} bytes" if result['file_size'] > 0 else "N/A"
    print(f"{result['language']:<15} {result['code']:<6} {status:<40} {size_str:<10}")

# Overall result
passed = sum(1 for r in results if "✓ PASSED" in r["status"])
total = len(results)
print("-" * 71)
print(f"TOTAL: {passed}/{total} tests passed")

if passed == total:
    print("\n✓ All tests PASSED! gTTS is working correctly with proper language support.")
else:
    print(f"\n✗ {total - passed} test(s) FAILED. Check the error messages above.")

print(f"\nAudio files location: {os.path.abspath(test_dir)}")
print("="*70)
