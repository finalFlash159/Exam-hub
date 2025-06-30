import os
import json
import logging
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# Load environment variables from .env file
load_dotenv()

# Thiết lập logging chi tiết
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExamGenerator:
    def __init__(self):
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            
            if not api_key:
                raise Exception("❌ Không tìm thấy GEMINI_API_KEY trong file .env")
            
            # Khởi tạo LangChain ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=api_key,
                temperature=0.7,
                max_tokens=8192,
                top_p=0.8
            )
            
            logger.info("✅ Đã khởi tạo ExamGenerator với LangChain và Gemini API")
            
        except Exception as e:
            logger.error(f"Lỗi khởi tạo ExamGenerator: {str(e)}")
            raise Exception(f"Không thể khởi tạo ExamGenerator: {str(e)}")

    def generate_from_text(self, text, exam_title, question_count=10):
        """Synchronous method để tương thích với code hiện tại"""
        prompt = self._create_prompt(text, question_count)
        
        try:
            logger.info(f"Đang tạo câu hỏi với {len(text)} ký tự và {question_count} câu hỏi")
            
            # Gọi LangChain để tạo câu hỏi (sync)
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse response từ LangChain
            exam_data = self._parse_response(response.content)
            
            return {
                "title": exam_title,
                "questions": exam_data
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo câu hỏi: {str(e)}")
            return {"error": "Không thể tạo câu hỏi", "details": str(e)}

    async def generate_from_text_async(self, text, exam_title, question_count=10):
        """Asynchronous method cho FastAPI"""
        prompt = self._create_prompt(text, question_count)
        
        try:
            logger.info(f"Đang tạo câu hỏi với {len(text)} ký tự và {question_count} câu hỏi (async)")
            
            # Gọi LangChain để tạo câu hỏi (async)
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            # Parse response từ LangChain
            exam_data = self._parse_response(response.content)
            
            return {
                "title": exam_title,
                "questions": exam_data
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo câu hỏi: {str(e)}")
            return {"error": "Không thể tạo câu hỏi", "details": str(e)}

    def _create_prompt(self, text, question_count):
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

    def _parse_response(self, response_text):
        try:
            logger.info(f"Phản hồi từ LangChain: {response_text[:200]}...")
            
            # Tìm JSON array trong response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # Thử parse trực tiếp
                return json.loads(response_text)
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSONDecodeError: {e}, đang thử làm sạch phản hồi")
            try:
                # Làm sạch response - bước 1: loại bỏ markdown
                cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
                
                # Bước 2: Fix các escape characters phổ biến
                cleaned_text = self._fix_json_escapes(cleaned_text)
                
                # Bước 3: Tìm JSON array
                json_start = cleaned_text.find('[')
                json_end = cleaned_text.rfind(']') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = cleaned_text[json_start:json_end]
                    logger.debug(f"Cleaned JSON: {json_str[:300]}...")
                    return json.loads(json_str)
                else:
                    return json.loads(cleaned_text)
                    
            except json.JSONDecodeError as e2:
                logger.error(f"Không thể phân tích phản hồi JSON sau khi làm sạch: {e2}")
                logger.debug(f"Raw response: {response_text}")
                return []

    def _fix_json_escapes(self, text):
        """Sửa các ký tự escape không hợp lệ trong JSON"""
        try:
            # Fix các escape characters phổ biến
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
            import re
            # Remove invalid escape sequences like \x, \u without proper format
            text = re.sub(r'\\(?!["\\/bfnrt])', '', text)
            
            return text
            
        except Exception as e:
            logger.warning(f"Lỗi khi sửa escape characters: {e}")
            return text
