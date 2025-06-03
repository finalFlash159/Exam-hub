import pytest
import os
import sys
from unittest.mock import patch

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    from app import app
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'test_uploads'
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'GEMINI_API_KEY': 'test_api_key',
        'FLASK_ENV': 'testing'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def sample_exam_data():
    """Sample exam data for testing."""
    return {
        "title": "Test Exam",
        "questions": [
            {
                "id": 1,
                "question": "What is Python?",
                "options": [
                    {"label": "A", "text": "A snake"},
                    {"label": "B", "text": "A programming language"},
                    {"label": "C", "text": "A movie"},
                    {"label": "D", "text": "A book"}
                ],
                "answer": "B",
                "explanation": {
                    "en": "Python is a programming language",
                    "vi": "Python là một ngôn ngữ lập trình"
                }
            }
        ]
    } 