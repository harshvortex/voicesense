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

### Core AI Features
| Feature | Description |
|---|---|
| 🎙️ **Transcription** | OpenAI Whisper — `tiny` through `large` models |
| 💬 **Sentiment Analysis** | DistilBERT fine-tuned on SST-2 (POSITIVE / NEGATIVE) |
| 🌍 **Language Detection** | Automatic spoken-language identification |
| 📊 **Confidence Score** | Know how sure the model is about its prediction |
| 🔊 **Audio Formats** | MP3, WAV, M4A, AAC, OGG, FLAC, WebM, WMA |

### User & Cloud Features
| Feature | Description |
|---|---|
| 🔐 **User Authentication** | Email/password registration & login with Supabase Auth |
| 📱 **Voice History** | Save, search, and manage all analyzed audio clips |
| 👤 **User Profiles** | Customizable profiles with avatars and statistics |
| ☁️ **Cloud Storage** | Secure audio file storage with Supabase |
| 📊 **Statistics** | Track sentiment trends and usage analytics |
| ⚙️ **Settings** | Privacy controls, theme, language preferences |
| 📲 **PWA Ready** | Install as app on mobile & desktop devices |

### Infrastructure
| Feature | Description |
|---|---|
| ⚡ **REST API** | `POST /analyze` from any client |
| 🚀 **Vercel Ready** | One-click deployment to Vercel serverless |
| 🗄️ **Supabase Integration** | PostgreSQL database + Auth + Storage |
| 🐳 **Docker Ready** | One command to run anywhere |
| 🧪 **Tests** | Pytest suite with mocked model calls |
| 🌐 **CORS Support** | Cross-origin requests enabled |

---

## 📁 Project Structure

```
voicesense/
├── app.py                    # Flask app — routes, auth, API
├── auth_utils.py             # Authentication & session management
├── supabase_utils.py         # Database & storage operations
├── config.py                 # Env-driven configuration classes
├── wsgi.py                   # Gunicorn WSGI entry point
├── api/
│   ├── index.py              # Vercel serverless entry point
│   └── requirements.txt       # Lightweight deps for Vercel
├── vercel.json               # Vercel deployment config
├── requirements.txt          # Python dependencies
├── .env.example              # Env var template
├── .gitignore
├── LICENSE
├── DEPLOYMENT.md             # Deployment guide
├── PRE_DEPLOYMENT_CHECKLIST   # Pre-deployment checklist
├── static/
│   ├── css/
│   │   ├── style.css         # Main UI stylesheet
│   │   ├── auth.css          # Auth pages styling
│   │   ├── dashboard.css     # Dashboard styling
│   │   ├── history.css       # Voice history styling
│   │   └── profile.css       # Profile page styling
│   ├── js/
│   │   └── service-worker.js # PWA service worker
│   ├── icons/                # PWA app icons
│   └── screenshots/          # PWA screenshots
├── templates/
│   ├── index.html            # Homepage
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── dashboard.html        # Main dashboard
│   ├── history.html          # Voice clip history
│   └── profile.html          # User profile page
├── scripts/
│   ├── 01-init-db.sql        # Database initialization
│   └── migrate_db.py         # Migration helper
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

### With Authentication (Requires Supabase)

Before starting with auth features, set up Supabase:

```bash
# 1. Create .env from .env.example
cp .env.example .env

# 2. Add your Supabase credentials:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_ANON_KEY=your-anon-key
# ... etc

# 3. Initialize database (see SETUP_GUIDE.md)
# 4. Start the app
python app.py
```

Register a new account at http://localhost:5000/register

---

## 🚀 Deploy to Vercel

One-click deployment with authentication and cloud storage:

```bash
# 1. Ensure code is pushed to GitHub
git push origin main

# 2. Go to vercel.com and import this repository
# 3. Add environment variables (see DEPLOYMENT.md)
# 4. Deploy!
```

**Full deployment guide:** See [DEPLOYMENT.md](DEPLOYMENT.md)

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
