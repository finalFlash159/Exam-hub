"""
Exam API endpoints for generating and saving exams
Handles document processing and LLM-based question generation
"""

import os
import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Set

from fastapi import APIRouter, HTTPException
from models import ExamGenerationRequest, SaveExamRequest
from core.config import get_settings
from document_processor import DocumentProcessor
from llm_generator import ExamGenerator

router = APIRouter(prefix="/api", tags=["exam"])
logger = logging.getLogger(__name__)


@router.post("/generate-exam")
async def generate_exam(request: ExamGenerationRequest) -> Dict[str, Any]:
    """Generate exam questions from uploaded file"""
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
            raise HTTPException(status_code=400, detail='Insufficient content to generate questions')

        logger.info("Starting exam generation with LLM...")
        generator = ExamGenerator()
        exam_data = await generator.generate_from_text_async(
            extracted_text, 
            request.exam_title, 
            request.question_count
        )
        
        logger.debug(f"LLM response type: {type(exam_data)}")
        if isinstance(exam_data, dict) and "error" in exam_data:
            logger.error(f"LLM generation error: {exam_data['details']}")
            raise HTTPException(status_code=500, detail=f'Failed to generate questions: {exam_data["details"]}')

        questions_count = len(exam_data.get('questions', []))
        logger.info(f"✅ Successfully generated {questions_count} questions")

        response_data = {
            'message': 'Exam generated successfully',
            'exam_data': exam_data
        }
        logger.debug("Exam generation completed successfully")
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_exam: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=f'Server error: {str(e)}')


@router.post("/save-exam")
async def save_exam(request: SaveExamRequest) -> Dict[str, Any]:
    """Save exam to the system"""
    settings = get_settings()
    questions_dir = settings["questions_dir"]
    
    logger.info("Starting save exam process...")
    logger.debug(f"Questions directory: {questions_dir}")
    
    try:
        exam_data = request.exam_data
        exam_title = exam_data.get('title', 'Generated Exam')
        questions = exam_data.get('questions', [])

        logger.info(f"Saving exam: '{exam_title}' with {len(questions)} questions")

        if not questions:
            logger.error("No questions provided")
            raise HTTPException(status_code=400, detail='No questions to save')

        # Ensure questions directory exists
        Path(questions_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Questions directory verified: {questions_dir}")

        # Find next available ID
        new_id = _find_next_exam_id(questions_dir)
        logger.info(f"Selected new exam ID: {new_id}")

        # Save questions file
        new_file_name = f'questions{new_id}.json'
        file_path = os.path.join(questions_dir, new_file_name)

        logger.info(f"Saving to file: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        logger.info("Questions file saved successfully")

        # Update index.js
        logger.info("Updating index.js...")
        _update_index_js(new_id, exam_title, new_file_name)
        logger.info("✅ index.js updated successfully")

        response_data = {
            'success': True,
            'message': f"Exam '{exam_title}' saved successfully",
            'exam_id': new_id,
            'file_name': new_file_name
        }
        logger.info(f"Save exam completed successfully: {response_data}")
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving exam: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save exam: {str(e)}")


def _find_next_exam_id(questions_dir: str) -> int:
    """
    Find the next available exam ID by checking existing files and index.js
    
    Args:
        questions_dir: Directory containing question files
        
    Returns:
        Next available exam ID
    """
    # Get IDs from existing question files
    existing_files = [f for f in os.listdir(questions_dir) if f.startswith('questions') and f.endswith('.json')]
    file_ids = [int(f.replace('questions', '').replace('.json', '')) for f in existing_files if f[9:-5].isdigit()]
    
    # Check IDs used in index.js
    index_file = '../exam-app/src/data/index.js'
    used_ids: Set[int] = set(file_ids)
    
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            index_content = f.read()
        
        # Extract all IDs from examData (format "number:")
        id_matches = re.findall(r'(\d+):\s*\{', index_content)
        used_ids.update(int(id_str) for id_str in id_matches)
        
    except Exception as e:
        logger.warning(f"Cannot read index.js to check IDs: {e}")
    
    # Find smallest unused ID
    new_id = 1
    while new_id in used_ids:
        new_id += 1
        
    logger.debug(f"Used IDs: {sorted(used_ids)}, Next ID: {new_id}")
    return new_id


def _update_index_js(exam_id: int, exam_title: str, file_name: str) -> None:
    """
    Update index.js file to add new exam entry
    
    Args:
        exam_id: ID of the new exam
        exam_title: Title of the exam
        file_name: Name of the questions file
    """
    index_file = '../exam-app/src/data/index.js'

    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Add import statement in correct position
        import_stmt = f'import questions{exam_id} from \'./questions/{file_name}\';\n'
        
        # Find position after other imports (before import { getExamDuration })
        import_position = content.find('import { getExamDuration }')
        if import_position != -1:
            content = content[:import_position] + import_stmt + content[import_position:]
        else:
            # Fallback: add at the beginning
            content = import_stmt + content
        
        # 2. Add exam entry to examData object
        exam_entry = f'''  {exam_id}: {{
    title: "{exam_title}",
    questions: questions{exam_id},
    ...calculateExamInfo(questions{exam_id})
  }},
'''

        # Find examData object and add entry before closing brace
        exam_data_start = content.find('export const examData = {')
        if exam_data_start != -1:
            # Find closing brace of examData object
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
                content = content[:closing_brace_pos] + exam_entry + content[closing_brace_pos:]
            else:
                logger.error("Cannot find closing brace of examData")
                raise Exception("Cannot find position to add new exam")
        else:
            logger.error("Cannot find examData export")
            raise Exception("Cannot find examData in index.js")

        # 3. Write updated content
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.info(f"Successfully updated index.js: added import and exam entry for ID {exam_id}")

    except Exception as e:
        logger.error(f"Error updating index.js: {e}")
        raise 