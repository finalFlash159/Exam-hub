import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("API KEY không tồn tại trong file .env - vui lòng thêm GEMINI_API_KEY=your_api_key")

# Cấu hình API Gemini
genai.configure(api_key=GEMINI_API_KEY)

class ExamGenerator:
    def __init__(self):
        try:
            # Liệt kê các model có sẵn để debug
            available_models = [m.name for m in genai.list_models()]
            logger.info(f"Các model có sẵn: {available_models}")
            
            # Sử dụng phiên bản mới nhất của Gemini
            model_name = "models/gemini-1.5-pro" if "models/gemini-1.5-pro" in str(available_models) else "models/gemini-pro"
            logger.info(f"Sử dụng model: {model_name}")
            
            # Khởi tạo model
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            logger.error(f"Lỗi khởi tạo model: {str(e)}")
            raise Exception(f"Không thể khởi tạo model: {str(e)}")
    
    def generate_from_text(self, text, exam_title, question_count=10):
        """
        Generate an exam with multiple-choice questions from the provided text
        
        Args:
            text: The document text content
            exam_title: Title for the generated exam
            question_count: Number of questions to generate (default: 10)
            
        Returns:
            JSON-formatted exam data conforming to the Exam Hub format
        """
        # Create a prompt for the LLM
        prompt = self._create_prompt(text, question_count)
        
        try:
            # Generate response from Gemini
            logger.info(f"Đang tạo câu hỏi với {len(text)} ký tự và {question_count} câu hỏi")
            
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Parse the response to extract JSON
            exam_data = self._parse_response(response.text)
            
            # Add exam title to the data dictionary
            exam_data_with_meta = {
                "title": exam_title,
                "questions": exam_data
            }
            
            return exam_data_with_meta
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo câu hỏi: {str(e)}")
            return {"error": "Không thể tạo câu hỏi", "details": str(e)}
    
    def _create_prompt(self, text, question_count):
            """Create a prompt for the LLM to generate exam questions"""
            
            prompt = f"""
            Based on the following text content, generate {question_count} multiple-choice quiz questions.
            
            TEXT CONTENT:
            {text[:10000]}  # Limiting to first 10000 chars to stay within token limits
            
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
                "answer": "B",  // The correct option label
                "explanation": {{
                "en": "Explanation in English"
                "vi": "Giải thích bằng tiếng Việt"
                }}
            }},
            // More questions...
            ]
            ```
            
            Ensure each question:
            1. Is based on the content provided
            2. Has exactly one correct answer
            3. Has clear and concise explanations
            4. Is diverse in difficulty and topic coverage
            
            Return ONLY the JSON array, no additional text or formatting.
            """
            

            prompt = prompt.strip()
            
            return prompt
    
    def _parse_response(self, response_text):
        """Extract and parse JSON from LLM response"""
        try:
            # Ghi log phản hồi gốc để debug
            logger.info(f"Phản hồi gốc từ LLM: {response_text[:200]}...")
            
            # Tìm phần JSON trong phản hồi
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                logger.info(f"Đã tìm thấy chuỗi JSON từ vị trí {json_start} đến {json_end}")
                return json.loads(json_str)
            else:
                # Nếu không tìm thấy dấu ngoặc, thử phân tích toàn bộ văn bản
                logger.info("Không tìm thấy dấu ngoặc vuông, thử phân tích toàn bộ văn bản")
                return json.loads(response_text)
                
        except json.JSONDecodeError as e:
            # Nếu phân tích thất bại, thử làm sạch phản hồi
            logger.warning(f"JSONDecodeError: {str(e)}, đang thử làm sạch phản hồi")
            try:
                # Xóa các dấu code block nếu có
                cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
                return json.loads(cleaned_text)
            except json.JSONDecodeError:
                # Nếu vẫn thất bại, trả về phản hồi dự phòng
                logger.error("Không thể phân tích phản hồi JSON, trả về mảng trống")
                return []




