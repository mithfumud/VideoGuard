# 🎬 VideoGuard

> Multimodal video copyright detection with audio + visual intelligence and traceable ownership records.

---

## 🔗 Live App

👉 **Try the app here:** _[https://videoguard.streamlit.app/]_  


---

## 🚀 Overview

VideoGuard is built to solve a real problem: **detecting video plagiarism beyond exact file matching**.

In practice, copied videos are rarely identical. They’re trimmed, re-encoded, slightly edited, or modified in audio.  
This project takes a **content-aware approach**, combining audio and visual signals to produce a reliable similarity verdict.

It’s not just a model — it’s a **complete workflow**:
- analyze content,
- decide similarity,
- track ownership,
- and generate reports.

---

## ✨ Key Features

- 🎧 **Audio + Video Analysis**  
  Uses both sound and visuals instead of relying on a single signal.

- 📊 **Similarity Scoring System**  
  Produces a final score with a clear verdict:
  - `COPY`
  - `ORIGINAL`

- 🔍 **Flexible Comparison**
  - Compare with a reference video  
  - Or scan against a registry of originals

- 🧾 **Ownership Registry**
  Stores metadata like:
  - owner name
  - content hash
  - timestamp
  - provenance identifiers

- 📄 **PDF Report Export**
  Generate clean reports with:
  - score breakdown
  - final verdict
  - ownership details

- ⚙️ **Configurable Pipeline**
  Easily tune:
  - threshold
  - fusion weights
  - frame sampling rate

---

## 🧠 How It Works

### Step-by-step pipeline:

1. **Upload Video**  
   User uploads a new video (optionally with a reference).

2. **Duplicate Check**  
   SHA-256 hashing quickly detects exact matches.

3. **Preprocessing**
   - Extract audio (WAV)
   - Sample video frames

4. **Feature Extraction**
   - Audio → MFCC + chroma features  
   - Video → pHash + ORB + HSV histogram

5. **Similarity Calculation**
   Each modality produces a score between `0` and `1`.

6. **Score Fusion**

   ```
   final = (audio_weight × audio_score) + (video_weight × video_score)
   ```

7. **Decision Engine**
   - If score ≥ threshold → `COPY`
   - Else → `ORIGINAL`

8. **Output**
   - Register ownership (if original)
   - Show matched record (if copy)
   - Export PDF report

---

## 🏗️ Project Structure

```
project/
├─ app.py
├─ config.yaml
├─ requirements.txt
├─ data/
│  ├─ registry.json
│  └─ video_store/
├─ src/
│  ├─ core/
│  ├─ adapters/
│  ├─ report/
└─ tests/
```

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit  
- **Computer Vision**: OpenCV, imagehash, Pillow  
- **Audio Processing**: librosa, scipy, numpy  
- **Media Handling**: FFmpeg  
- **Reporting**: fpdf2  
- **Testing**: pytest  
- **Runtime**: Python 3.11  

---

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

---

## 💡 Usage

### Register Original Content
- Upload a video  
- Leave reference empty  
- If marked `ORIGINAL`, it gets stored in registry  

### Check for Copyright Violation
- Upload a video  
- (Optional) add reference  
- View similarity score + verdict  

### Export Report
- Generate a PDF with full analysis details  

---

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
analysis:
  audio_weight: 0.5
  video_weight: 0.5
  threshold: 0.75
  frame_sample_rate: 1
```

---

## 🧩 Engineering Highlights

- Clean modular architecture (`core`, `adapters`, `report`)
- Adapter pattern for future blockchain/IPFS integration
- Efficient processing (hashing + frame sampling)
- Handles missing audio / invalid inputs gracefully
- Designed with real product workflow in mind

---

## 🧪 Testing

```bash
pytest -q
```

---

## ⚠️ Limitations

- Uses a **mock registry** (not real blockchain yet)
- Limited test coverage for edge cases
- No production deployment setup (Docker/CI)

---

## 🛣️ Roadmap

- Real provenance backend (IPFS + smart contracts)
- Better robustness against edits and noise
- Performance benchmarking
- Full deployment pipeline

