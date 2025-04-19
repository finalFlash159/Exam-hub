from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename
from document_processor import DocumentProcessor
from llm_generator import ExamGenerator
import logging

app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response
        
    logger.info("Received upload request")
    
    if 'file' not in request.files:
        logger.error("No file part in the request")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        logger.error(f"File type not allowed: {file.filename}")
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Generate unique filename to avoid collisions
    unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    try:
        file.save(file_path)
        logger.info(f"File saved successfully: {file_path}")
        
        # Process document to extract text
        processor = DocumentProcessor()
        extracted_text = processor.extract_text(file_path)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_id': unique_filename,
            'text_length': len(extracted_text)
        })
    except Exception as e:
        logger.error(f"Error saving or processing file: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/generate-exam', methods=['POST'])
def generate_exam():
    data = request.json
    if not data or 'file_id' not in data:
        return jsonify({'error': 'No file_id provided'}), 400
    
    file_id = data['file_id']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    exam_title = data.get('exam_title', 'Generated Exam')
    question_count = data.get('question_count', 10)
    
    # Process document
    processor = DocumentProcessor()
    extracted_text = processor.extract_text(file_path)
    
    # Generate exam via LLM
    generator = ExamGenerator()
    exam_data = generator.generate_from_text(extracted_text, exam_title, question_count)
    
    return jsonify({
        'message': 'Exam generated successfully',
        'exam_data': exam_data
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # Thay đổi port từ 5000 sang 5001 để tránh xung đột với AirPlay Receiver trên macOS
    app.run(debug=True, host='0.0.0.0', port=5001)
