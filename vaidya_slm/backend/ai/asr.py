def transcribe_audio(file_path: str, lang: str = "en") -> str:
    """
    Mock implementation of an ASR pipeline.
    In production, this would load an ai4bharat/indicwav2vec or whisper-small pipeline.
    """
    print(f"Loading ASR model for {lang}...")
    print(f"Transcribing {file_path}")
    
    # Simulating transcription output
    return "I have acidity and headache"
