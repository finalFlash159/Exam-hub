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
    
    logger.info("Starting save exam process...")
    logger.debug(f"Questions directory: {questions_dir}")
    
    try:
        exam_data = request.exam_data
        exam_title = exam_data.get('title', 'Exam Generated')
        questions = exam_data.get('questions', [])

        logger.info(f"Saving exam: '{exam_title}' with {len(questions)} questions")

        if not questions:
            logger.error("No questions provided")
            raise HTTPException(status_code=400, detail='Không có câu hỏi')

        Path(questions_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Questions directory created/verified: {questions_dir}")

        # Tìm ID mới thông minh hơn - check cả file questions và examData
        existing_files = [f for f in os.listdir(questions_dir) if f.startswith('questions') and f.endswith('.json')]
        file_ids = [int(f.replace('questions', '').replace('.json', '')) for f in existing_files if f[9:-5].isdigit()]
        
        # Đọc index.js để check IDs đã dùng trong examData
        index_file = '../exam-app/src/data/index.js'
        used_ids = set(file_ids)
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_content = f.read()
            
            # Extract tất cả IDs từ examData (dạng "số:")
            import re
            id_matches = re.findall(r'(\d+):\s*\{', index_content)
            used_ids.update(int(id_str) for id_str in id_matches)
            
        except Exception as e:
            logger.warning(f"Không thể đọc index.js để check IDs: {e}")
        
        # Tìm ID nhỏ nhất chưa được sử dụng
        new_id = 1
        while new_id in used_ids:
            new_id += 1
            
        logger.info(f"Selected new exam ID: {new_id} (used IDs: {sorted(used_ids)})")

        new_file_name = f'questions{new_id}.json'
        file_path = os.path.join(questions_dir, new_file_name)

        logger.info(f"Saving to file: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        logger.info(f"Questions file saved successfully")

        logger.info("Updating index.js...")
        update_index_js(new_id, exam_title, new_file_name, questions_dir)
        logger.info("index.js updated successfully")

        response_data = {
            'success': True,
            'message': f"Đã lưu bài kiểm tra '{exam_title}'",
            'exam_id': new_id,
            'file_name': new_file_name
        }
        logger.info(f"Save exam completed successfully: {response_data}")
        return response_data

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

        # 1. Thêm import statement ở đúng vị trí (cùng với các import khác)
        import_stmt = f'import questions{exam_id} from \'./questions/{file_name}\';\n'
        
        # Tìm vị trí cuối cùng của các import statements (trước import { getExamDuration })
        import_position = content.find('import { getExamDuration }')
        if import_position != -1:
            # Thêm import trước import { getExamDuration }
            content = content[:import_position] + import_stmt + content[import_position:]
        else:
            # Fallback: thêm ở đầu file
            content = import_stmt + content
        
        # 2. Thêm exam entry vào examData object
        exam_entry = f'''  {exam_id}: {{
    title: "{exam_title}",
    questions: questions{exam_id},
    ...calculateExamInfo(questions{exam_id})
  }},
'''

        # Tìm vị trí cuối của examData object (trước dấu } cuối)
        exam_data_start = content.find('export const examData = {')
        if exam_data_start != -1:
            # Tìm dấu } đóng của examData object
            brace_count = 0
            closing_brace_pos = -1
            
            for i in range(exam_data_start, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        closing_brace_pos = i
                        break
            
            if closing_brace_pos != -1:
                # Thêm exam mới trước dấu } cuối
                content = content[:closing_brace_pos] + exam_entry + content[closing_brace_pos:]
            else:
                logger.error("Không tìm thấy closing brace của examData")
                raise Exception("Không thể tìm vị trí để thêm exam mới")
        else:
            logger.error("Không tìm thấy examData export")
            raise Exception("Không thể tìm examData trong index.js")

        # 3. Ghi lại file
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.info(f"Successfully updated index.js: added import and exam entry for ID {exam_id}")

    except Exception as e:
        raise Exception(f"Không thể cập nhật danh sách bài kiểm tra: {str(e)}") 