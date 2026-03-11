"""VoiceSense — Configuration (env-driven)."""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    SECRET_KEY         = os.environ.get('SECRET_KEY', 'change-me-in-production')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_UPLOAD_MB', 50)) * 1024 * 1024
    WHISPER_MODEL      = os.environ.get('WHISPER_MODEL', 'base')
    SENTIMENT_MODEL    = os.environ.get(
        'SENTIMENT_MODEL',
        'distilbert-base-uncased-finetuned-sst-2-english',
    )


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DEBUG   = True


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     DevelopmentConfig,
}
