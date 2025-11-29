import os
import subprocess
from pathlib import Path
import shutil

# Import custom modules
from asr import ASRProcessor
from mt import MTProcessor
from tts import TTSProcessor
from duration_aligner import DurationAligner

def extract_audio_from_video(video_path, output_wav_path):
    """
    Extracts audio from video using ffmpeg.
    Returns True if successful.
    """
    if output_wav_path.exists():
        print(f"   Using existing extracted audio: {output_wav_path}")
        return True
        
    print(f"   Extracting audio from video -> {output_wav_path.name}")
    try:
        # -y = overwrite, -vn = no video, -ac = 1 channel (mono for TTS ref)
        cmd = f'ffmpeg -y -v error -i "{video_path}" -vn -acodec pcm_s16le -ar 22050 -ac 1 "{output_wav_path}"'
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error extracting audio: {e}")
        return False

def run_dubbing_pipeline(video_path, source_lang, target_lang="english"):
    """
    Runs the full End-to-End Dubbing Pipeline.
    """
    video_path = Path(video_path)
    output_dir = video_path.parent / "dubbing_output"
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n🎥 Starting Dubbing Pipeline for: {video_path.name}")
    print(f"🌍 {source_lang} -> {target_lang}")
    
    # --- Step 0: Pre-Extraction (CRITICAL FIX) ---
    # We must create a clean .wav file for ASR and TTS to use.
    # Tools like torchaudio/Whisper sometimes fail on raw MP4 containers.
    print("\n--- Step 0: Audio Extraction ---")
    ref_audio_path = output_dir / "original_audio_extracted.wav"
    success = extract_audio_from_video(video_path, ref_audio_path)
    
    if not success:
        print("🛑 Pipeline stopped due to audio extraction failure.")
        return None

    # --- Step 1: Source Separation (Demucs) ---
    print("\n--- Step 1: Source Separation (Placeholder) ---")
    # In reality, you'd run Demucs on 'ref_audio_path' here.
    accompaniment_path = None 
    
    # --- Step 2: ASR (Whisper) ---
    print("\n--- Step 2: ASR (Whisper) ---")
    asr = ASRProcessor()
    # Now we pass the WAV file, not the MP4
    asr_result = asr.transcribe(ref_audio_path, language=None) 
    
    segments_path = output_dir / "segments.json"
    asr.save_segments(asr_result, segments_path)
    
    # --- Step 3: MT (NLLB) ---
    print("\n--- Step 3: MT (Translation) ---")
    mt = MTProcessor()
    
    translated_segments = []
    for seg in asr_result['segments']:
        text = seg['text']
        trans_text = mt.translate(text, source_lang=source_lang, target_lang=target_lang)
        
        new_seg = seg.copy()
        new_seg['text'] = trans_text
        translated_segments.append(new_seg)

    # --- Step 4: TTS (Coqui) ---
    print("\n--- Step 4: TTS (Voice Cloning) ---")
    tts = TTSProcessor()
    tts_clips_dir = output_dir / "tts_clips"
    tts_clips_dir.mkdir(exist_ok=True)
    
    for i, seg in enumerate(translated_segments):
        text = seg['text']
        clip_path = tts_clips_dir / f"segment_{i}.wav"
        
        # Now we pass the WAV file as the speaker reference
        tts.generate_audio(
            text=text, 
            speaker_wav_path=str(ref_audio_path), 
            output_path=str(clip_path), 
            language="en"
        )

    # --- Step 5: Duration Aligner ---
    print("\n--- Step 5: Duration Alignment ---")
    aligner = DurationAligner()
    clean_speech_track = output_dir / "aligned_speech_clean.wav"
    
    aligner.align_and_merge(
        video_path=str(video_path), # Aligner needs total video duration
        tts_clips_dir=tts_clips_dir,
        segments_json_path=segments_path,
        output_path=clean_speech_track
    )

    # --- Step 6: Wav2Lip (Placeholder) ---
    print("\n--- Step 6: Wav2Lip (Inference) ---")
    print(f"COMMAND: python inference.py --checkpoint_path ... --face {video_path} --audio {clean_speech_track}")
    
    print("\n✅ Pipeline Finished! Output Audio: ", clean_speech_track)
    return clean_speech_track

if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.parent
    TEST_VIDEO = BASE_DIR / "data/mtedx/video/de/train/0JI-oFgsdXw.mp4" 
    
    if TEST_VIDEO.exists():
        run_dubbing_pipeline(TEST_VIDEO, source_lang="german")
    else:
        print(f"Video not found: {TEST_VIDEO}")