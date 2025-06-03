import pytest
import json
import os
from unittest.mock import patch, Mock

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_test_connection(client):
    """Test connection endpoint."""
    response = client.get('/api/test-connection')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data

def test_upload_no_file(client):
    """Test upload endpoint with no file."""
    response = client.post('/api/upload')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_upload_empty_filename(client):
    """Test upload endpoint with empty filename."""
    data = {'file': (b'', '')}
    response = client.post('/api/upload', data=data)
    assert response.status_code == 400

@patch('app.DocumentProcessor')
def test_upload_valid_file(mock_processor, client):
    """Test upload endpoint with valid file."""
    # Mock the document processor
    mock_instance = Mock()
    mock_instance.extract_text.return_value = "Sample extracted text"
    mock_processor.return_value = mock_instance
    
    # Create a test file
    data = {'file': (b'test content', 'test.pdf')}
    response = client.post('/api/upload', 
                          data=data,
                          content_type='multipart/form-data')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'file_id' in response_data
    assert 'text_length' in response_data

def test_generate_exam_no_file_id(client):
    """Test generate exam endpoint without file_id."""
    response = client.post('/api/generate-exam',
                          data=json.dumps({}),
                          content_type='application/json')
    assert response.status_code == 400

def test_generate_exam_file_not_found(client):
    """Test generate exam endpoint with non-existent file."""
    data = {'file_id': 'nonexistent_file.pdf'}
    response = client.post('/api/generate-exam',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 404

@patch('app.ExamGenerator')
@patch('app.DocumentProcessor')
def test_generate_exam_success(mock_processor, mock_generator, client, sample_exam_data):
    """Test successful exam generation."""
    # Mock document processor
    mock_proc_instance = Mock()
    mock_proc_instance.extract_text.return_value = "Sample text for exam generation"
    mock_processor.return_value = mock_proc_instance
    
    # Mock exam generator
    mock_gen_instance = Mock()
    mock_gen_instance.generate_from_text.return_value = sample_exam_data
    mock_generator.return_value = mock_gen_instance
    
    # Create a temporary file for testing
    test_file_path = 'uploads/test_file.pdf'
    os.makedirs('uploads', exist_ok=True)
    with open(test_file_path, 'w') as f:
        f.write("test content")
    
    try:
        data = {
            'file_id': 'test_file.pdf',
            'exam_title': 'Test Exam',
            'question_count': 5
        }
        response = client.post('/api/generate-exam',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'exam_data' in response_data
        
    finally:
        # Clean up
        if os.path.exists(test_file_path):
            os.remove(test_file_path) 