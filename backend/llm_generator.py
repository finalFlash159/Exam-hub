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
        prompt = f"""
        Based on the following text content, generate {question_count} multiple-choice quiz questions.

        TEXT CONTENT:
        {text[:10000]}

        Please create {question_count} quiz questions with 4 options each (labeled A, B, C, D). 
        Format your response as a valid JSON array where each question has the following structure:

        ```json
        [
        {{
            "id": 1,
            "question": "The question text",
            "options": [
            {{ "label": "A", "text": "First option" }},
            {{ "label": "B", "text": "Second option" }},
            {{ "label": "C", "text": "Third option" }},
            {{ "label": "D", "text": "Fourth option" }}
            ],
            "answer": "B",
            "explanation": {{
            "en": "Explanation in English",
            "vi": "Giải thích bằng tiếng Việt"
            }}
        }},
        ...
        ]
        ```
        
        Ensure each question:
        - Is based on the content provided
        - Has exactly one correct answer
        - Has clear and concise explanations
        - Is diverse in difficulty and topic coverage

        Return ONLY the JSON array, no additional text or formatting.
        """
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
                # Làm sạch response
                cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
                json_start = cleaned_text.find('[')
                json_end = cleaned_text.rfind(']') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = cleaned_text[json_start:json_end]
                    return json.loads(json_str)
                else:
                    return json.loads(cleaned_text)
                    
            except json.JSONDecodeError:
                logger.error("Không thể phân tích phản hồi JSON, trả về mảng trống")
                return []
