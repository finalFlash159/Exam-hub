"""
Exam Service
Business logic for exam generation, processing, and management
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Use new import paths
from app.utils.document_processor import DocumentProcessor
from app.utils.ai_generator import ExamGenerator

# Temporarily use old config import during migration
try:
    from app.core.config import get_settings
except ImportError:
    from core.config import get_settings

logger = logging.getLogger(__name__)


class ExamService:
    """Service for handling exam-related business logic"""
    
    def __init__(self):
        """Initialize service with required dependencies"""
        self.document_processor = DocumentProcessor()
        self.ai_generator = ExamGenerator()
        logger.info("ExamService initialized")
    
    async def generate_exam_from_file(
        self, 
        file_id: str, 
        exam_title: str, 
        question_count: int
    ) -> Dict[str, Any]:
        """
        Generate exam questions from uploaded file
        
        Args:
            file_id: ID of uploaded file
            exam_title: Title for the exam
            question_count: Number of questions to generate
            
        Returns:
            Dict containing exam data and metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If content is insufficient
            Exception: For other generation errors
        """
        logger.info(f"Generate exam request - file_id: {file_id}, title: {exam_title}, count: {question_count}")
        
        # Get file path
        settings = get_settings()
        upload_folder = settings["upload_folder"]
        file_path = os.path.join(upload_folder, file_id)
        
        logger.debug(f"Looking for file at: {file_path}")
        
        # Validate file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract text from document
        logger.info("Processing document...")
        extracted_text = self.document_processor.extract_text(file_path)
        text_length = len(extracted_text)
        logger.info(f"Extracted {text_length} characters from document")
        
        # Validate content length
        if text_length < 100:
            logger.warning(f"Text too short: {text_length} characters")
            raise ValueError("Insufficient content to generate questions")
        
        # Generate exam using AI
        logger.info("Starting exam generation with LLM...")
        exam_data = await self.ai_generator.generate_from_text_async(
            extracted_text, 
            exam_title, 
            question_count
        )
        
        # Validate generation result
        if isinstance(exam_data, dict) and "error" in exam_data:
            logger.error(f"LLM generation error: {exam_data['details']}")
            raise Exception(f"Failed to generate questions: {exam_data['details']}")
        
        questions_count = len(exam_data.get('questions', []))
        logger.info(f"Successfully generated {questions_count} questions")
        
        # Return structured response
        result = {
            'message': 'Exam generated successfully',
            'exam_data': exam_data,
            'metadata': {
                'source_file': file_id,
                'text_length': text_length,
                'questions_generated': questions_count,
                'generation_method': 'LLM'
            }
        }
        
        logger.debug("Exam generation completed successfully")
        return result
    
    async def save_exam(self, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save exam to persistent storage
        
        Args:
            exam_data: Complete exam data to save
            
        Returns:
            Dict with save result and metadata
            
        Raises:
            ValueError: If exam data is invalid
            Exception: For save errors
        """
        logger.info("Starting save exam process...")
        
        # Extract exam details
        exam_title = exam_data.get('title', 'Generated Exam')
        questions = exam_data.get('questions', [])
        
        logger.info(f"Saving exam: '{exam_title}' with {len(questions)} questions")
        
        # Validate exam data
        if not questions:
            logger.error("No questions provided")
            raise ValueError("No questions to save")
        
        # Get save path
        settings = get_settings()
        questions_dir = settings["questions_dir"]
        
        # Ensure directory exists
        Path(questions_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Questions directory verified: {questions_dir}")
        
        # Find next available ID
        new_id = self._find_next_exam_id(questions_dir)
        logger.info(f"Selected new exam ID: {new_id}")
        
        # Save questions file
        new_file_name = f'questions{new_id}.json'
        file_path = os.path.join(questions_dir, new_file_name)
        
        logger.info(f"Saving to file: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        logger.info("Questions file saved successfully")
        
        # Update index.js (TODO: Move to repository layer later)
        logger.info("Updating index.js...")
        self._update_index_js(new_id, exam_title, new_file_name)
        logger.info("index.js updated successfully")
        
        # Return save result
        result = {
            'success': True,
            'message': f"Exam '{exam_title}' saved successfully",
            'exam_id': new_id,
            'file_name': new_file_name,
            'metadata': {
                'questions_count': len(questions),
                'save_method': 'file_system',
                'save_path': file_path
            }
        }
        
        logger.info(f"Save exam completed successfully: {result}")
        return result
    
    def _find_next_exam_id(self, questions_dir: str) -> int:
        """Find the next available exam ID"""
        # Implementation copied from original API
        # TODO: Move to repository layer
        used_ids = set()
        
        for file_name in os.listdir(questions_dir):
            if file_name.startswith('questions') and file_name.endswith('.json'):
                try:
                    id_str = file_name[9:-5]  # Remove 'questions' prefix and '.json' suffix
                    if id_str.isdigit():
                        used_ids.add(int(id_str))
                except (ValueError, IndexError):
                    continue
        
        # Find the smallest available ID starting from 1
        next_id = 1
        while next_id in used_ids:
            next_id += 1
            
        return next_id
    
    def _update_index_js(self, exam_id: int, exam_title: str, file_name: str):
        """Update frontend index.js file"""
        # Implementation copied from original API  
        # TODO: Move to repository layer
        settings = get_settings()
        questions_dir = settings["questions_dir"]
        index_path = os.path.join(os.path.dirname(questions_dir), 'index.js')
        
        if not os.path.exists(index_path):
            logger.warning(f"index.js not found at {index_path}")
            return
        
        # Read current content
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Add import statement
        import_stmt = f'import questions{exam_id} from \'./questions/{file_name}\';\n'
        import_position = content.find('import { getExamDuration }')
        if import_position != -1:
            content = content[:import_position] + import_stmt + content[import_position:]
        else:
            content = import_stmt + content
        
        # 2. Add exam entry
        exam_entry = f'''
  {exam_id}: {{
    title: "{exam_title}",
    questions: questions{exam_id},
    duration: getExamDuration(questions{exam_id}),
    difficulty: "Medium"
  }},'''
        
        exams_position = content.find('const exams = {')
        if exams_position != -1:
            brace_position = content.find('{', exams_position) + 1
            content = content[:brace_position] + exam_entry + content[brace_position:]
        
        # Write updated content
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Successfully updated index.js: added import and exam entry for ID {exam_id}")
    
    async def get_exam_by_id(self, exam_id: int) -> Optional[Dict[str, Any]]:
        """
        Get exam by ID (placeholder for future database implementation)
        
        Args:
            exam_id: ID of exam to retrieve
            
        Returns:
            Exam data if found, None otherwise
        """
        # TODO: Implement when database layer is added
        logger.info(f"get_exam_by_id called with ID: {exam_id}")
        return None
    
    async def list_exams(self) -> Dict[str, Any]:
        """
        List all available exams (placeholder for future database implementation)
        
        Returns:
            List of exam summaries
        """
        # TODO: Implement when database layer is added
        logger.info("list_exams called")
        return {"exams": [], "count": 0} 