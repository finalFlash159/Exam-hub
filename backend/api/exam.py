import os
import json
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from models import ExamGenerationRequest, SaveExamRequest
from core.config import get_settings
from document_processor import DocumentProcessor
from llm_generator import ExamGenerator

router = APIRouter(prefix="/api", tags=["exam"])
logger = logging.getLogger(__name__)

@router.post("/generate-exam")
async def generate_exam(request: ExamGenerationRequest):
    """Tạo bài kiểm tra từ file đã upload"""
    settings = get_settings()
    upload_folder = settings["upload_folder"]
    
    logger.info(f"Generate exam request - file_id: {request.file_id}, title: {request.exam_title}, count: {request.question_count}")
    
    file_path = os.path.join(upload_folder, request.file_id)
    logger.debug(f"Looking for file at: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail='File not found')

    try:
        logger.info("Processing document...")
        processor = DocumentProcessor()
        extracted_text = processor.extract_text(file_path)
        text_length = len(extracted_text)
        logger.info(f"Extracted {text_length} characters from document")

        if text_length < 100:
            logger.warning(f"Text too short: {text_length} characters")
            raise HTTPException(status_code=400, detail='Không đủ nội dung để tạo câu hỏi')

        logger.info("Starting exam generation with LLM...")
        generator = ExamGenerator()
        exam_data = await generator.generate_from_text_async(extracted_text, request.exam_title, request.question_count)
        
        logger.debug(f"LLM response type: {type(exam_data)}")
        if isinstance(exam_data, dict) and "error" in exam_data:
            logger.error(f"LLM generation error: {exam_data['details']}")
            raise HTTPException(status_code=500, detail=f'Không thể tạo câu hỏi: {exam_data["details"]}')

        questions_count = len(exam_data.get('questions', []))
        logger.info(f"Successfully generated {questions_count} questions")

        response_data = {
            'message': 'Tạo bài kiểm tra thành công',
            'exam_data': exam_data
        }
        logger.debug("Exam generation completed successfully")
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_exam: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=f'Lỗi máy chủ: {str(e)}')

@router.post("/save-exam")
async def save_exam(request: SaveExamRequest):
    """Lưu bài kiểm tra vào hệ thống"""
    settings = get_settings()
    questions_dir = settings["questions_dir"]
    
    try:
        exam_data = request.exam_data
        exam_title = exam_data.get('title', 'Exam Generated')
        questions = exam_data.get('questions', [])

        if not questions:
            raise HTTPException(status_code=400, detail='Không có câu hỏi')

        Path(questions_dir).mkdir(parents=True, exist_ok=True)

        existing_files = [f for f in os.listdir(questions_dir) if f.startswith('questions') and f.endswith('.json')]
        existing_ids = [int(f.replace('questions', '').replace('.json', '')) for f in existing_files if f[9:-5].isdigit()]
        new_id = max(existing_ids) + 1 if existing_ids else 1

        new_file_name = f'questions{new_id}.json'
        file_path = os.path.join(questions_dir, new_file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

        update_index_js(new_id, exam_title, new_file_name, questions_dir)

        return {
            'success': True,
            'message': f"Đã lưu bài kiểm tra '{exam_title}'",
            'exam_id': new_id,
            'file_name': new_file_name
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể lưu bài kiểm tra: {str(e)}")

def update_index_js(exam_id: int, exam_title: str, file_name: str, questions_dir: str):
    """Cập nhật file index.js để thêm bài kiểm tra mới"""
    index_file = '../exam-app/src/data/index.js'

    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()

        import_stmt = f'import questions{exam_id} from \'./questions/{file_name}\';\n'
        insert_pos = content.find('// Map of exam types to question data')
        if insert_pos == -1:
            insert_pos = content.find('export const examData')

        if insert_pos != -1:
            content = content[:insert_pos] + import_stmt + content[insert_pos:]
        else:
            content = import_stmt + content

        exam_entry = f'''
  {exam_id}: {{
    title: "{exam_title}",
    questions: questions{exam_id}
  }},'''

        data_pos = content.find('export const examData = {')
        if data_pos != -1:
            brace_pos = content.find('{', data_pos)
            if brace_pos != -1:
                content = content[:brace_pos+1] + exam_entry + content[brace_pos+1:]

        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)

    except Exception as e:
        raise Exception(f"Không thể cập nhật danh sách bài kiểm tra: {str(e)}") 