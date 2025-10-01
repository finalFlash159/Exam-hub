import pytest
import os
import sys
from unittest.mock import patch, Mock
from dotenv import load_dotenv

# Load .env file before running tests
# Get the backend directory path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(backend_dir, '.env')
load_dotenv(env_path)

# Add the backend directory to Python path
sys.path.insert(0, backend_dir)

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    # Mock the dependencies that might not be available in CI
    with patch('document_processor.DocumentProcessor') as mock_processor, \
         patch('llm_generator.ExamGenerator') as mock_generator:
        
        # Configure mocks
        mock_processor.return_value.extract_text.return_value = "Test extracted text"
        mock_generator.return_value.generate_from_text.return_value = {
            "title": "Test Exam",
            "questions": [{"id": 1, "question": "Test?", "answer": "A"}]
        }
        
        # Now import the app
        from app import app
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = 'test_uploads'
        
        # Create test upload folder
        os.makedirs('test_uploads', exist_ok=True)
        
        with app.test_client() as client:
            with app.app_context():
                yield client
        
        # Cleanup
        import shutil
        if os.path.exists('test_uploads'):
            shutil.rmtree('test_uploads')

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