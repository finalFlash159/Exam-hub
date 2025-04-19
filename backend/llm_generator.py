import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class ExamGenerator:
    def __init__(self):
        # Get available generative model
        self.model = genai.GenerativeModel('gemini-pro')
    
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
        
        # Generate response from Gemini
        response = self.model.generate_content(prompt)
        
        # Parse the response to extract JSON
        try:
            exam_data = self._parse_response(response.text)
            
            # Add exam title to the data dictionary
            exam_data_with_meta = {
                "title": exam_title,
                "questions": exam_data
            }
            
            return exam_data_with_meta
            
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return {"error": "Failed to generate exam questions", "details": str(e)}
    
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
        
        return prompt
    
    def _parse_response(self, response_text):
        """Extract and parse JSON from LLM response"""
        # Try to extract JSON from the response
        try:
            # Find JSON array in the response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # If we couldn't find brackets, try parsing the whole text
                return json.loads(response_text)
                
        except json.JSONDecodeError:
            # If parsing fails, try to clean up the response
            # Remove code block markers if present
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
