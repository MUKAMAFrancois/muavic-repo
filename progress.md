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

# Revised Pipeline:
1.  ASR: Whisper
2.  MT: Llama 3.1
3.  TTS: XTTS-v2
4.  Duration Aligner: ("Crucial Step" - Mandatory)
5.  Source Separation: Demucs (Extract background `accompaniment.wav`)
6.  Audio Mixing: `ffmpeg` (Mix `english_tts.wav` + `accompaniment.wav`)
7.  LipSync: Wav2Lip (trained on data)

For now the pipeline will be tested on german videos (10 videos) into english.
   Testing: the web-interface will be developed. the interface having multiple options: a user can upload a video in german and be translated to English. He can also have an option of pasting the youtube link in german and be able to download the translated video. In all cases, the duration of video must nearly match.
   The ASR (Whisper), MT (Llama 3.1), and TTS (XTTS-v2) models are all pre-trained and can be used directly. this helps reducing training time and focusing on training Wav2Lip. We will train the Wav2Lip generator and its "expert" lip-sync discriminator.
   the problem to solve is duration matching.
**Duration Matching (Crucial Step)**: The baseline paper noted this was a major problem.


### Step 7: Deployment (Web Interface)

The frontend and backend tie this all together.

* **Frontend (React):** A simple UI with an "Upload" button, a "YouTube Link" text field, a language selection dropdown, and a "Translate" button. When the user clicks "Translate," it shows a "Processing..." spinner.
* **Backend (FastAPI):** A FastAPI endpoint (e.g., `/dub-video/`) that receives the request and runs. Should run asynchronously.
* **Result:** When the pipeline is finished, the backend sends a success message, and the React frontend displays a "Download Your Video" link pointing to `final_dubbed_video.mp4`.

=> data: https://github.com/facebookresearch/muavic


