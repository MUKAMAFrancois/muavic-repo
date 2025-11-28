import torch
import os
import sys

# 1. Set Environment Variable to agree to Coqui License automatically
# This is crucial for running on AWS/Colab without user interaction
os.environ["COQUI_TOS_AGREED"] = "1" # License Handling: XTTS requires agreeing to a license. This code accepts it automatically via os.environ

from TTS.api import TTS

class TTSProcessor:
    _model_cache = None

    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
        """
        Initializes the XTTS-v2 Model.
        """
        # Auto-detect device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Singleton Pattern: Load model only if not already loaded
        if TTSProcessor._model_cache is None:
            print(f"...Loading TTS Model ({model_name}) on {self.device}...")
            try:
                # Initialize TTS with the model name
                # gpu=True/False is handled by .to(device) in newer versions or init flag
                tts = TTS(model_name)
                
                # Move to GPU if available
                if self.device == "cuda":
                    tts.to(self.device)
                
                TTSProcessor._model_cache = tts
                print("Good: TTS Model loaded successfully.")
            except Exception as e:
                print(f"!!! Error loading TTS Model: {e}")
                # Common fix for Windows path length issues
                if sys.platform == 'win32': 
                    print("Hint: On Windows, enable 'Long Paths' if you see file not found errors.")
                raise
        else:
            print("Good: Using cached TTS Model.")
            
        self.tts = TTSProcessor._model_cache

    def generate_audio(self, text, speaker_wav_path, output_path, language="en"):
        """
        Generates audio using Voice Cloning.
        """
        if not os.path.exists(speaker_wav_path):
            raise FileNotFoundError(f"Speaker reference audio not found: {speaker_wav_path}")
            
        print(f"...Generating TTS for: '{text[:30]}...'")
        
        try:
            # XTTS Inference
            self.tts.tts_to_file(
                text=text,
                speaker_wav=speaker_wav_path,
                language=language,
                file_path=output_path
            )
            print(f"Good: Audio saved to: {output_path}")
            return output_path
        except Exception as e:
            print(f"!!! Error during generation: {e}")
            raise

# --- Testing Block ---
if __name__ == "__main__":
    from pathlib import Path
    
    # Define Paths (Relative for portability)
    # Using the same file we used for ASR/MT testing
    BASE_DIR = Path(__file__).parent.parent 
    REF_AUDIO = BASE_DIR / "data/muavic/de/audio/train/_Hk4MOw9gsA/_Hk4MOw9gsA_0000.wav"
    OUTPUT_FILE = "test_tts_output.wav"
    
    # Text we got from the Translation Step
    TRANSLATED_TEXT = "It's so nice to be back in Tübingen."
    
    if REF_AUDIO.exists():
        tts = TTSProcessor()
        
        tts.generate_audio(
            text=TRANSLATED_TEXT,
            speaker_wav_path=str(REF_AUDIO),
            output_path=OUTPUT_FILE,
            language="en" 
        )
        
        print(f"Good: Test Complete! Generated: {OUTPUT_FILE}")
    else:
        print(f"!! Reference file not found at {REF_AUDIO}")