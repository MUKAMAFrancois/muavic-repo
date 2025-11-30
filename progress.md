Important Note on English: The MuAViC script cannot auto-download English because it relies on LRS3, which requires a manual download (it's a single massive zip file, not individual YouTube links). For this "1-Hour Test", skip downloading English via this script. Use the other 4 languages to validate your Wav2Lip/Dubbing pipeline.

### Commands
# 1. Install dependencies
pip install -r requirements.txt
pip install yt-dlp

# 2. Download French (Limit: 10 videos)
python get_data.py --root-path ./data --src-lang fr

# 3. Download Russian (Limit: 10 videos)
python get_data.py --root-path ./data --src-lang ru

# 4. Download Spanish (Limit: 10 videos)
python get_data.py --root-path ./data --src-lang es

# 5. Download German (Limit: 10 videos)
python get_data.py --root-path ./data --src-lang de

### The Corrected Pipeline Order

Here is the revised, industry-standard flow:

1.  ASR: Whisper (Get Text + Timestamps)
2.  MT: NLLB-200 (Translate Text)
3.  TTS: Coqui TTS (Generate Clean English Audio)
4.  Duration Aligner: Align Clean TTS to Video Duration (Pad/Speed up)
5.  Source Separation: Demucs (Extract `accompaniment.wav`)
6.  LipSync (Wav2Lip):
       Input: `original_video.mp4` + `aligned_clean_tts.wav`
       Output: `lip_synced_video_clean.mp4` (Video with English lips + Clean English Voice)
7.  Final Mixing:
       Input: `lip_synced_video_clean.mp4` + `accompaniment.wav`
       Tool: `ffmpeg`
       Action: Merge the background audio with the clean speech video.
8.  Final Result: Dubbed, Aligned, Background-Preserved Video.
**Duration Matching (Crucial Step)**: The baseline paper noted this was a major problem.


### Step 7: Deployment (Web Interface)

The frontend and backend tie this all together.

* **Frontend (React):** A simple UI with an "Upload" button, a "YouTube Link" text field, a language selection dropdown, and a "Translate" button. When the user clicks "Translate," it shows a "Processing..." spinner.
* **Backend (FastAPI):** A FastAPI endpoint (e.g., `/dub-video/`) that receives the request and runs. Should run asynchronously.
* **Result:** When the pipeline is finished, the backend sends a success message, and the React frontend displays a "Download Your Video" link pointing to `final_dubbed_video.mp4`.

=> data: https://github.com/facebookresearch/muavic


## Select the correct interpreter:
Open the Command Palette in VS Code (Ctrl+Shift+P or Cmd+Shift+P).
Type "Python: Select Interpreter".

## Error installing: TTS
      List all python versions: py -0
      # 1. Create a Python 3.10 environment
      conda create -n dubbing_env python=3.10 -y

      # 2. Activate it
      conda activate dubbing_env

      # 3. Install PyTorch (Required before TTS)
      # (Visit pytorch.org to get the exact command for your CUDA version if you have a GPU)
      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

      # 4. Install Coqui TTS
      pip install TTS

      # 5. Install Coqui TTS
# Assuming you installed Python 3.10 executable
      py -3.10 -m venv .venv_310 
      Or: py -3.11 -m venv .venv_311
      .venv_310\Scripts\activate
      pip install TTS