"""
VoiceSense — Audio Sentiment Analyzer
Flask application with OpenAI Whisper transcription & HuggingFace sentiment analysis.

Set DEMO_MODE=true to run without ML dependencies (returns mock data).
"""

import os
import tempfile
import logging
import time
import random
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from config import Config

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s  %(name)s — %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger('voicesense')

# ── App ───────────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config.from_object(Config)

# ── Demo mode (Vercel / lightweight environments) ─────────────────────────────
DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() == 'true'

if DEMO_MODE:
    logger.info('🎭 Running in DEMO MODE — ML models are disabled, returning mock data.')

# ── Lazy model loading ────────────────────────────────────────────────────────
_whisper_model = None
_sentiment_pipeline = None


def get_whisper_model():
    """Load OpenAI Whisper model on first request (lazy)."""
    global _whisper_model
    if _whisper_model is None:
        import whisper
        name = app.config.get('WHISPER_MODEL', 'base')
        logger.info('Loading Whisper model: %s …', name)
        _whisper_model = whisper.load_model(name)
        logger.info('Whisper model loaded.')
    return _whisper_model


def get_sentiment_pipeline():
    """Load HuggingFace sentiment pipeline on first request (lazy)."""
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        from transformers import pipeline
        name = app.config.get(
            'SENTIMENT_MODEL',
            'distilbert-base-uncased-finetuned-sst-2-english',
        )
        logger.info('Loading sentiment model: %s …', name)
        _sentiment_pipeline = pipeline('sentiment-analysis', model=name)
        logger.info('Sentiment pipeline loaded.')
    return _sentiment_pipeline


# ── Demo data ─────────────────────────────────────────────────────────────────
DEMO_TRANSCRIPTS = [
    "This is an absolutely wonderful product. I've been using it for weeks and it has completely "
    "transformed my workflow. The interface is intuitive, the performance is stellar, and the "
    "customer support team has been incredibly responsive whenever I had questions.",

    "I'm really disappointed with this purchase. The quality is far below what was advertised, "
    "and when I tried to get a refund, the process was confusing and took forever. I wouldn't "
    "recommend this to anyone looking for a reliable solution.",

    "The presentation went okay today. There were some good points raised about the quarterly "
    "numbers and the team seemed generally aligned on the next steps. We'll need to follow up "
    "on a few action items before the deadline next Friday.",
]

DEMO_SENTIMENTS = [
    {'label': 'POSITIVE', 'confidence': 98.72},
    {'label': 'NEGATIVE', 'confidence': 96.34},
    {'label': 'POSITIVE', 'confidence': 67.91},
]


def generate_demo_response():
    """Return a realistic-looking mock analysis result."""
    idx = random.randint(0, len(DEMO_TRANSCRIPTS) - 1)
    transcript = DEMO_TRANSCRIPTS[idx]
    sentiment = DEMO_SENTIMENTS[idx]
    time.sleep(random.uniform(1.0, 2.5))  # simulate processing delay
    return {
        'success': True,
        'transcription': transcript,
        'sentiment': sentiment,
        'language': 'EN',
        'word_count': len(transcript.split()),
        'processing_time': f'{random.uniform(1.5, 4.0):.1f}s',
        'demo': True,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'm4a', 'ogg', 'flac', 'webm', 'wma','acc'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html', demo_mode=DEMO_MODE)


@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'service': 'voicesense',
        'demo_mode': DEMO_MODE,
    })


@app.route('/analyze', methods=['POST'])
def analyze():
    start = time.time()

    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided.'}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Unsupported file type. Allowed: {", ".join(sorted(ALLOWED_EXTENSIONS))}',
        }), 400

    # ── Demo mode — return mock data ──────────────────────────────────────
    if DEMO_MODE:
        logger.info('DEMO: Simulating analysis for %s', file.filename)
        return jsonify(generate_demo_response())

    # ── Real mode — ML processing ─────────────────────────────────────────
    filename = secure_filename(file.filename)
    temp_path = os.path.join(tempfile.gettempdir(), filename)
    file.save(temp_path)
    logger.info('Saved upload → %s', temp_path)

    try:
        # 1 — Transcribe
        model = get_whisper_model()
        result = model.transcribe(temp_path)
        transcription = result['text'].strip()
        language = result.get('language', 'unknown').upper()

        if not transcription:
            return jsonify({'error': 'Could not transcribe audio. Try a clearer recording.'}), 422

        # 2 — Sentiment
        pipe = get_sentiment_pipeline()
        sent = pipe(transcription[:1000])[0]
        label = sent['label'].upper()
        confidence = round(sent['score'] * 100, 2)

        elapsed = round(time.time() - start, 2)
        word_count = len(transcription.split())
        logger.info('Result → lang=%s  sent=%s (%s%%)  words=%d  time=%ss',
                     language, label, confidence, word_count, elapsed)

        return jsonify({
            'success': True,
            'transcription': transcription,
            'sentiment': {'label': label, 'confidence': confidence},
            'language': language,
            'word_count': word_count,
            'processing_time': f'{elapsed}s',
        })

    except Exception as exc:
        logger.exception('Processing error')
        return jsonify({'error': f'Processing failed: {exc}'}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ── Error handlers ────────────────────────────────────────────────────────────
@app.errorhandler(413)
def file_too_large(e):
    max_mb = app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024) // (1024 * 1024)
    return jsonify({'error': f'File too large. Max size is {max_mb} MB.'}), 413


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found.'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error.'}), 500


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
