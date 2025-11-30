import torch
import os
import sys
import re
from pydub import AudioSegment

# 1. Set Environment Variable to agree to Coqui License automatically
os.environ["COQUI_TOS_AGREED"] = "1"

from TTS.api import TTS

class TTSProcessor:
    _model_cache = None

    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if TTSProcessor._model_cache is None:
            print(f"🚀 Loading TTS Model ({model_name}) on {self.device}...")
            try:
                tts = TTS(model_name)
                if self.device == "cuda":
                    tts.to(self.device)
                TTSProcessor._model_cache = tts
                print("✅ TTS Model loaded successfully.")
            except Exception as e:
                print(f"❌ Error loading TTS Model: {e}")
                if sys.platform == 'win32': 
                    print("Hint: On Windows, enable 'Long Paths'.")
                raise
        else:
            print("✅ Using cached TTS Model.")
            
        self.tts = TTSProcessor._model_cache

    def split_text_into_chunks(self, text, max_chars=200):
        """
        Splits long text into smaller chunks based on punctuation
        to avoid XTTS token limit errors.
        """
        if len(text) <= max_chars:
            return [text]
            
        # Split by sentence endings first (. ? !)
        sentences = re.split(r'(?<=[.?!])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chars:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
                
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    def generate_audio(self, text, speaker_wav_path, output_path, language="en"):
        if not os.path.exists(speaker_wav_path):
            raise FileNotFoundError(f"Speaker ref not found: {speaker_wav_path}")
            
        # print(f"🎙️ TTS Request: '{text[:30]}...'")
        
        # 1. Check if text needs chunking
        chunks = self.split_text_into_chunks(text)
        
        if len(chunks) == 1:
            # --- FAST PATH (Standard Generation) ---
            try:
                self.tts.tts_to_file(
                    text=chunks[0],
                    speaker_wav=speaker_wav_path,
                    language=language,
                    file_path=output_path
                )
                return output_path
            except Exception as e:
                print(f"⚠️ Standard TTS failed: {e}. Trying fallback...")

        # --- SLOW PATH (Chunk & Merge) ---
        # If we are here, text was too long or failed. We create parts and merge them.
        print(f"   ⚠️ Long text detected ({len(text)} chars). Splitting into {len(chunks)} parts...")
        
        combined_audio = AudioSegment.empty()
        temp_files = []
        
        try:
            for i, chunk in enumerate(chunks):
                if not chunk.strip(): continue
                
                # Save temp file
                temp_file = f"{output_path}_part{i}.wav"
                temp_files.append(temp_file)
                
                self.tts.tts_to_file(
                    text=chunk,
                    speaker_wav=speaker_wav_path,
                    language=language,
                    file_path=temp_file
                )
                
                # Load and append
                part_audio = AudioSegment.from_file(temp_file)
                combined_audio += part_audio
                
            # Export final merged file
            combined_audio.export(output_path, format="wav")
            print(f"💾 Merged Audio saved to: {output_path}")
            
        except Exception as e:
            print(f"❌ Error during Chunk/Merge: {e}")
            raise
            
        finally:
            # Cleanup temp files
            for f in temp_files:
                if os.path.exists(f):
                    os.remove(f)

        return output_path

if __name__ == "__main__":
    print("TTS Module with Chunking Ready.")