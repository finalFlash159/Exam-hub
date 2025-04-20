from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename
from document_processor import DocumentProcessor
from llm_generator import ExamGenerator
import logging
import json
import shutil
from pathlib import Path

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
    
    try:
        # Process document
        processor = DocumentProcessor()
        extracted_text = processor.extract_text(file_path)
        
        logger.info(f"Đã trích xuất {len(extracted_text)} ký tự từ tài liệu")
        
        if len(extracted_text) < 100:
            return jsonify({'error': 'Không đủ nội dung cho việc tạo câu hỏi'}), 400
        
        # Generate exam via LLM
        logger.info(f"Đang tạo bài kiểm tra '{exam_title}' với {question_count} câu hỏi")
        generator = ExamGenerator()
        exam_data = generator.generate_from_text(extracted_text, exam_title, question_count)
        
        # Kiểm tra kết quả có lỗi không
        if "error" in exam_data:
            logger.error(f"Lỗi tạo câu hỏi: {exam_data['details']}")
            return jsonify({
                'error': 'Không thể tạo câu hỏi', 
                'details': exam_data['details']
            }), 500
            
        logger.info(f"Đã tạo thành công {len(exam_data.get('questions', []))} câu hỏi")
        return jsonify({
            'message': 'Tạo bài kiểm tra thành công',
            'exam_data': exam_data
        })
    except Exception as e:
        logger.error(f"Lỗi xử lý tài liệu hoặc tạo câu hỏi: {str(e)}")
        return jsonify({'error': f'Lỗi máy chủ: {str(e)}'}), 500

# Thêm đường dẫn đến thư mục questions
QUESTIONS_DIR = '../exam-app/src/data/questions'

@app.route('/api/save-exam', methods=['POST'])
def save_exam():
    """Lưu bài kiểm tra vào hệ thống và cập nhật index.js"""
    try:
        data = request.json
        if not data or 'exam_data' not in data:
            return jsonify({'error': 'Không có dữ liệu bài kiểm tra'}), 400
        
        exam_data = data['exam_data']
        exam_title = exam_data.get('title', 'Exam Generated')
        questions = exam_data.get('questions', [])
        
        if not questions:
            return jsonify({'error': 'Không có câu hỏi trong bài kiểm tra'}), 400
        
        # Đảm bảo thư mục questions tồn tại
        Path(QUESTIONS_DIR).mkdir(parents=True, exist_ok=True)
        
        # Tìm ID cho bài kiểm tra mới
        existing_files = [f for f in os.listdir(QUESTIONS_DIR) if f.startswith('questions') and f.endswith('.json')]
        existing_ids = [int(f.replace('questions', '').replace('.json', '')) for f in existing_files if f[9:-5].isdigit()]
        new_id = max(existing_ids) + 1 if existing_ids else 1
        
        # Tạo tên file mới
        new_file_name = f'questions{new_id}.json'
        file_path = os.path.join(QUESTIONS_DIR, new_file_name)
        
        # Lưu câu hỏi vào file JSON mới
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Đã lưu bài kiểm tra vào {file_path}")
        
        # Cập nhật file index.js để thêm bài kiểm tra mới
        update_index_js(new_id, exam_title, new_file_name)
        
        return jsonify({
            'success': True,
            'message': f"Bài kiểm tra '{exam_title}' đã được thêm vào hệ thống",
            'exam_id': new_id,
            'file_name': new_file_name
        })
        
    except Exception as e:
        logger.error(f"Lỗi khi lưu bài kiểm tra: {str(e)}")
        return jsonify({'error': f"Không thể lưu bài kiểm tra: {str(e)}"}), 500

def update_index_js(exam_id, exam_title, file_name):
    """Cập nhật file index.js để thêm bài kiểm tra mới"""
    index_file = '../exam-app/src/data/index.js'
    
    try:
        # Đọc nội dung file index.js
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Thêm câu import mới
        import_statement = f'import questions{exam_id} from \'./questions/{file_name}\';\n'
        import_position = content.find('// Map of exam types to question data')
        if import_position == -1:
            import_position = content.find('export const examData')
        
        if import_position != -1:
            content = content[:import_position] + import_statement + content[import_position:]
        else:
            # Nếu không tìm thấy vị trí, thêm vào đầu file
            content = import_statement + content
        
        # Thêm bài kiểm tra mới vào đối tượng examData
        exam_entry = f'''
  {exam_id}: {{
    title: "{exam_title}",
    questions: questions{exam_id}
  }},'''
        
        # Tìm vị trí để chèn bài kiểm tra mới
        exam_data_position = content.find('export const examData = {')
        if exam_data_position != -1:
            bracket_position = content.find('{', exam_data_position)
            if bracket_position != -1:
                content = content[:bracket_position+1] + exam_entry + content[bracket_position+1:]
        
        # Ghi lại nội dung file
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Đã cập nhật file index.js với bài kiểm tra mới (ID: {exam_id})")
        
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật file index.js: {str(e)}")
        raise Exception(f"Không thể cập nhật danh sách bài kiểm tra: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    """Endpoint để kiểm tra kết nối đến backend và API Gemini"""
    try:
        # Kiểm tra API key và kết nối
        if not GEMINI_API_KEY:
            return jsonify({
                'backend': True,
                'gemini': False,
                'message': 'API KEY không tồn tại'
            })
        
        # Thực hiện một generate content đơn giản để kiểm tra API
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello!")
        
        return jsonify({
            'status': 'success',
            'backend': True,
            'gemini': True,
            'message': 'Kết nối thành công đến backend và Gemini API'
        })
        
    except Exception as e:
        logger.error(f"Lỗi kết nối Gemini API: {str(e)}")
        return jsonify({
            'status': 'error',
            'backend': True,
            'gemini': False,
            'message': f'Lỗi kết nối Gemini API: {str(e)}'
        })

if __name__ == '__main__':
    # Thay đổi port từ 5000 sang 5001 để tránh xung đột với AirPlay Receiver trên macOS
    app.run(debug=True, host='0.0.0.0', port=5001)
