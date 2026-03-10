<div align="center">

# 🎙️ VoiceSense

**AI-powered audio transcription & sentiment analysis — runs 100% locally.**

Upload any audio file → get instant transcription + sentiment intelligence.  
Built with **Flask · OpenAI Whisper · HuggingFace Transformers**.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Whisper](https://img.shields.io/badge/Whisper-OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://github.com/openai/whisper)
[![License](https://img.shields.io/badge/License-MIT-A855F7?style=for-the-badge)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](Dockerfile)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎙️ **Transcription** | OpenAI Whisper — `tiny` through `large` models |
| 💬 **Sentiment Analysis** | DistilBERT fine-tuned on SST-2 (POSITIVE / NEGATIVE) |
| 🌍 **Language Detection** | Automatic spoken-language identification |
| 📊 **Confidence Score** | Know how sure the model is about its prediction |
| ⚡ **REST API** | `POST /analyze` from any client |
| 🐳 **Docker Ready** | One command to run anywhere |
| 🧪 **Tests** | Pytest suite with mocked model calls |
| 🚀 **CI/CD** | GitHub Actions for test + Docker build |

---

## 📁 Project Structure

```
voicesense/
├── app.py                    # Flask app — routes, lazy model loading, API
├── config.py                 # Env-driven configuration classes
├── wsgi.py                   # Gunicorn WSGI entry point
├── requirements.txt          # Python dependencies
├── Procfile                  # Cloud deploy (Render / Railway / Heroku)
├── Dockerfile                # Multi-stage production Docker image
├── docker-compose.yml        # Docker Compose with model cache volumes
├── .env.example              # Env var template
├── .gitignore
├── LICENSE
├── static/
│   └── css/
│       └── style.css         # Premium dark UI stylesheet
├── templates/
│   └── index.html            # Single-page frontend
├── tests/
│   ├── __init__.py
│   └── test_app.py           # Pytest suite
└── .github/
    └── workflows/
        └── ci.yml            # GitHub Actions CI/CD
```

---

## 🚀 Quick Start

### Prerequisites

Install `ffmpeg` (required by Whisper):

```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows — https://ffmpeg.org/download.html
```

### Setup

```bash
git clone https://github.com/harshvortex/voicesense.git
cd voicesense

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env          # edit if needed
python app.py
```

Open **http://localhost:5000** 🎉

---

## 🐳 Docker

```bash
# Docker Compose (recommended)
docker-compose up --build

# Or plain Docker
docker build -t voicesense .
docker run -p 5000:5000 voicesense
```

---

## 🔌 API Reference

### `POST /analyze`

Upload an audio file → receive transcription + sentiment.

**Request** — `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `audio` | File | ✅ | Audio file (see supported formats) |

**Supported formats:** `mp3` `wav` `mp4` `m4a` `ogg` `flac` `webm` `wma` — Max **50 MB**

**Success Response** `200`

```json
{
  "success": true,
  "transcription": "I absolutely loved the product, it exceeded my expectations!",
  "sentiment": {
    "label": "POSITIVE",
    "confidence": 99.87
  },
  "language": "EN",
  "word_count": 11,
  "processing_time": "3.2s"
}
```

**Error Response** `400`

```json
{
  "error": "Unsupported file type. Allowed: flac, m4a, mp3, mp4, ogg, wav, webm, wma"
}
```

### `GET /health`

```json
{ "status": "ok", "version": "1.0.0", "service": "voicesense" }
```

### Examples

```bash
# cURL
curl -X POST http://localhost:5000/analyze -F "audio=@recording.mp3"
```

```python
# Python
import requests

with open('recording.mp3', 'rb') as f:
    res = requests.post('http://localhost:5000/analyze', files={'audio': f})
    print(res.json())
```

---

## ⚙️ Configuration

All settings via environment variables or `.env`:

| Variable | Default | Description |
|---|---|---|
| `WHISPER_MODEL` | `base` | `tiny` · `base` · `small` · `medium` · `large` |
| `SENTIMENT_MODEL` | `distilbert-base-uncased-finetuned-sst-2-english` | Any HuggingFace sentiment model |
| `MAX_UPLOAD_MB` | `50` | Max upload size in MB |
| `SECRET_KEY` | `change-me-in-production` | Flask secret key |
| `PORT` | `5000` | Server port |
| `FLASK_DEBUG` | `false` | Debug mode |

### Whisper Model Comparison

| Model | Parameters | VRAM | Relative Speed |
|---|---|---|---|
| `tiny` | 39M | ~1 GB | ~10× |
| `base` | 74M | ~1 GB | ~7× |
| `small` | 244M | ~2 GB | ~4× |
| `medium` | 769M | ~5 GB | ~2× |
| `large` | 1.5B | ~10 GB | 1× |

---

## 🧪 Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## ☁️ Deployment

### Render / Railway / Heroku

1. Push to GitHub
2. Connect repo to your platform
3. Set env vars: `WHISPER_MODEL=base`, `SECRET_KEY=...`
4. Deploy — the `Procfile` handles startup

> **Note:** Whisper downloads model weights (~150 MB for `base`) on first cold start.

---

## 📄 License

[MIT](LICENSE) © [harshvortex](https://github.com/harshvortex)

---

## 🙌 Credits

- [OpenAI Whisper](https://github.com/openai/whisper)
- [HuggingFace Transformers](https://huggingface.co/transformers/)
- [Flask](https://flask.palletsprojects.com/)
