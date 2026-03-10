"""
VoiceSense — test suite.
Run:  pytest tests/ -v
"""

import io
import json
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    res = client.get('/health')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data['status'] == 'ok'
    assert data['service'] == 'voicesense'


def test_index(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b'VoiceSense' in res.data


def test_analyze_no_file(client):
    res = client.post('/analyze')
    assert res.status_code == 400
    assert b'No audio file' in res.data


def test_analyze_bad_extension(client):
    data = {'audio': (io.BytesIO(b'fake'), 'test.txt')}
    res = client.post('/analyze', data=data, content_type='multipart/form-data')
    assert res.status_code == 400
    assert b'Unsupported' in res.data


def test_analyze_success(client):
    whisper_mock = MagicMock()
    whisper_mock.transcribe.return_value = {
        'text': 'I absolutely love this product!',
        'language': 'en',
    }
    sentiment_mock = MagicMock(return_value=[{'label': 'POSITIVE', 'score': 0.9987}])

    with patch('app.get_whisper_model', return_value=whisper_mock), \
         patch('app.get_sentiment_pipeline', return_value=sentiment_mock):
        data = {'audio': (io.BytesIO(b'fake audio bytes'), 'test.mp3')}
        res = client.post('/analyze', data=data, content_type='multipart/form-data')

    assert res.status_code == 200
    body = json.loads(res.data)
    assert body['success'] is True
    assert body['sentiment']['label'] == 'POSITIVE'
    assert body['word_count'] == 6
    assert body['language'] == 'EN'
    assert 'processing_time' in body


def test_analyze_empty_transcription(client):
    whisper_mock = MagicMock()
    whisper_mock.transcribe.return_value = {'text': '', 'language': 'en'}

    with patch('app.get_whisper_model', return_value=whisper_mock):
        data = {'audio': (io.BytesIO(b'silence'), 'silence.wav')}
        res = client.post('/analyze', data=data, content_type='multipart/form-data')

    assert res.status_code == 422
