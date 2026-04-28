# 🎬 VideoGuard

> Multimodal video copyright detection with audio + visual intelligence and mock provenance records.

---

## 🔗 Live App

👉 **Try the app here:** https://videoguard.streamlit.app/

---

## 🚀 Overview

VideoGuard is built to solve a real problem: **detecting video plagiarism beyond exact file matching**.

In real scenarios, copied videos are often trimmed, re-encoded, lightly edited, or modified in audio.  
VideoGuard uses a **content-aware multimodal approach** by combining audio and visual similarity signals.

This is not just a model demo — it is an **end-to-end workflow**:
- analyze content  
- decide similarity  
- register ownership metadata  
- generate downloadable reports  

---

## ✨ Key Features

- 🎧 **Multimodal Analysis (Audio + Visual)**  
  Uses both sound and frames for more robust detection.

- 📊 **Deterministic Similarity Scoring**  
  Produces normalized scores (`0.0 → 1.0`) with final verdict:
  - `COPY`
  - `ORIGINAL`

- 🔍 **Flexible Comparison Modes**
  - Compare with a reference video  
  - Auto-scan registry to find best match  

- 🧾 **Ownership Registry Workflow**
  Stores:
  - owner name  
  - SHA-256 video hash  
  - timestamp  
  - mock CID / transaction hash  

- 📄 **PDF Report Export**
  Includes:
  - audio/video/final scores  
  - threshold  
  - verdict  
  - provenance metadata  

- ⚙️ **Configurable Pipeline**
  Easily tune:
  - threshold  
  - fusion weights  
  - frame sampling rate  

---

## 🧠 How It Works

### Step-by-step pipeline

1. **Upload Video**  
   Upload a new video (reference optional).

2. **Exact Duplicate Check**  
   SHA-256 hashing detects exact matches instantly.

3. **Preprocessing**
   - Extract audio (WAV)
   - Sample frames at configured interval

4. **Feature Extraction**
   - **Audio:** MFCC + chroma  
   - **Video:** pHash + ORB + HSV histogram  

5. **Similarity Calculation**  
   Each modality outputs a score between `0.0` and `1.0`.

6. **Score Fusion**

   ```text
   final = (audio_weight * audio_score) + (video_weight * video_score)
   ```

7. **Decision Engine**
   - If `final_score >= threshold` → `COPY`  
   - Else → `ORIGINAL`

8. **Output Actions**
   - `ORIGINAL` → register in provenance registry  
   - `COPY` → show matched ownership details  
   - Export PDF report  

---

## 🏗️ Project Structure

```
project/
├─ app.py
├─ config.yaml
├─ requirements.txt
├─ runtime.txt
├─ packages.txt
├─ data/
│  ├─ registry.json
│  └─ video_store/
├─ src/
│  ├─ config.py
│  ├─ core/
│  │  ├─ preprocessor.py
│  │  ├─ audio_analyzer.py
│  │  ├─ video_analyzer.py
│  │  ├─ fusion.py
│  │  └─ decision_engine.py
│  ├─ adapters/
│  │  ├─ base.py
│  │  └─ mock_adapter.py
│  └─ report/
│     └─ report_generator.py
└─ tests/
   └─ test_pipeline.py
```

---

## 🛠️ Tech Stack

- **Frontend/UI:** Streamlit  
- **Computer Vision:** OpenCV, imagehash, Pillow  
- **Audio Processing:** librosa, scipy, numpy  
- **Media Handling:** ffmpeg-python + system FFmpeg  
- **Reporting:** fpdf2  
- **Testing:** pytest  
- **Runtime:** Python 3.11  

---

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Ensure FFmpeg is installed

FFmpeg must be available in your system PATH.

### 3. Run the app

```bash
python -m streamlit run app.py
```

---

## 💡 Usage

### Register Original Content
- Upload a video  
- Leave reference empty  
- Enter owner name  
- Run analysis  
- If verdict is `ORIGINAL`, it is stored in registry  

### Check Suspected Copy
- Upload a video  
- (Optional) add reference  
- Or compare with registry  
- View scores + verdict  

### Export Report
- Download PDF with full analysis  

---

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
analysis:
  audio_weight: 0.5
  video_weight: 0.5
  threshold: 0.75
  frame_sample_rate: 1

provenance:
  backend: mock
```

---

## 🧩 Engineering Highlights

- Modular architecture (`core`, `adapters`, `report`)
- Multimodal scoring with explainable components
- Visual similarity via pHash + ORB + HSV
- Audio similarity via MFCC + chroma
- Adapter pattern for future blockchain/IPFS integration
- Handles missing audio, invalid inputs, and edge cases
- Product-oriented UX (analysis flow, registry, reports)

---

## 🧪 Testing

```bash
pytest -q
```

**Current checks:**
- identical videos → `COPY`  
- score always in `[0.0, 1.0]`  

---

## ⚠️ Limitations

- Uses **mock registry (JSON)** — no real blockchain yet  
- Limited test coverage  
- No deployment setup (Docker/CI/CD)

---

## 🛣️ Roadmap

- Real provenance backend (IPFS + smart contracts)  
- Improve robustness to edits/noise  
- Add benchmarking suite  
- Add Docker + CI/CD  

