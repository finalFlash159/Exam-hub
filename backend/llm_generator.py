"""
Exam Generator using LangChain and Google Gemini API
Generates multiple-choice questions from text content
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional

from langchain.schema import HumanMessage
from core.config import create_gemini_instance

logger = logging.getLogger(__name__)


class ExamGenerator:
    """Generate exam questions from text using Google Gemini API"""
    
    def __init__(self):
        """Initialize ExamGenerator with lazy-loaded Gemini instance"""
        self._llm = None
        logger.info("ExamGenerator initialized with lazy loading")
    
    @property
    def llm(self):
        """Lazy-load Gemini instance when needed"""
        if self._llm is None:
            self._llm = create_gemini_instance()
            if self._llm is None:
                raise Exception("Cannot create Gemini instance - API key not configured")
            logger.info("Gemini instance created for ExamGenerator")
        return self._llm
    
    def generate_from_text(self, text: str, exam_title: str, question_count: int = 10) -> Dict[str, Any]:
        """
        Generate exam questions from text (synchronous)
        
        Args:
            text: Source text content
            exam_title: Title for the exam
            question_count: Number of questions to generate
            
        Returns:
            Dict containing exam data or error information
        """
        prompt = self._create_prompt(text, question_count)
        
        try:
            logger.info(f"Generating {question_count} questions from {len(text)} characters")
            
            # Call LangChain to generate questions
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse response from LangChain
            exam_data = self._parse_response(response.content)
            
            return {
                "title": exam_title,
                "questions": exam_data
            }
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return {"error": "Failed to generate questions", "details": str(e)}

    async def generate_from_text_async(self, text: str, exam_title: str, question_count: int = 10) -> Dict[str, Any]:
        """
        Generate exam questions from text (asynchronous)
        
        Args:
            text: Source text content
            exam_title: Title for the exam
            question_count: Number of questions to generate
            
        Returns:
            Dict containing exam data or error information
        """
        prompt = self._create_prompt(text, question_count)
        
        try:
            logger.info(f"Generating {question_count} questions from {len(text)} characters (async)")
            
            # Call LangChain to generate questions (async)
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            # Parse response from LangChain
            exam_data = self._parse_response(response.content)
            
            return {
                "title": exam_title,
                "questions": exam_data
            }
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return {"error": "Failed to generate questions", "details": str(e)}

    def _create_prompt(self, text: str, question_count: int) -> str:
        """Create prompt for question generation"""
        prompt = f"""Create {question_count} multiple-choice questions based on the provided text content.

TEXT CONTENT:
{text[:10000]}

INSTRUCTIONS:
- Generate exactly {question_count} questions
- Each question must have 4 options (A, B, C, D)
- Include explanations in both English and Vietnamese
- Use simple text only - avoid special characters or complex formatting
- Return ONLY valid JSON array, no markdown or extra text

REQUIRED JSON FORMAT:
[
{{
    "id": 1,
    "question": "Question text here",
    "options": [
        {{"label": "A", "text": "Option A text"}},
        {{"label": "B", "text": "Option B text"}},
        {{"label": "C", "text": "Option C text"}},
        {{"label": "D", "text": "Option D text"}}
    ],
    "answer": "A",
    "explanation": {{
        "en": "English explanation",
        "vi": "Vietnamese explanation"
    }}
}}]

IMPORTANT: Return ONLY the JSON array. Do not include markdown formatting, code blocks, or any other text."""
        return prompt.strip()

    def _parse_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse and clean response from Gemini API
        
        Args:
            response_text: Raw response from API
            
        Returns:
            List of question dictionaries
        """
        try:
            logger.info(f"Parsing response: {response_text[:200]}...")
            
            # Find JSON array in response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # Try direct parsing
                return json.loads(response_text)
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSONDecodeError: {e}, attempting to clean response")
            try:
                # Clean response - Step 1: remove markdown
                cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
                
                # Step 2: Fix common escape characters
                cleaned_text = self._fix_json_escapes(cleaned_text)
                
                # Step 3: Find JSON array
                json_start = cleaned_text.find('[')
                json_end = cleaned_text.rfind(']') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = cleaned_text[json_start:json_end]
                    logger.debug(f"Cleaned JSON: {json_str[:300]}...")
                    return json.loads(json_str)
                else:
                    return json.loads(cleaned_text)
                    
            except json.JSONDecodeError as e2:
                logger.error(f"Cannot parse JSON response after cleaning: {e2}")
                logger.debug(f"Raw response: {response_text}")
                return []

    def _fix_json_escapes(self, text: str) -> str:
        """
        Fix invalid escape characters in JSON
        
        Args:
            text: Text to fix
            
        Returns:
            Cleaned text
        """
        try:
            # Fix common escape characters
            fixes = {
                '\\"': '"',      # Fix quote escapes
                '\\n': ' ',      # Replace newlines with spaces
                '\\r': ' ',      # Replace carriage returns
                '\\t': ' ',      # Replace tabs with spaces
                '\\\\': '\\',    # Fix double backslashes
                '\\/': '/',      # Fix forward slash escapes
            }
            
            for old, new in fixes.items():
                text = text.replace(old, new)
            
            # Remove any remaining invalid escape sequences
            # Remove invalid escape sequences like \x, \u without proper format
            text = re.sub(r'\\(?!["\\/bfnrt])', '', text)
            
            return text
            
        except Exception as e:
            logger.warning(f"Error fixing escape characters: {e}")
            return text
