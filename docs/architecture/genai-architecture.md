# 🤖 GenAI Module Architecture

## 🎯 **OVERVIEW**

Exam Hub sử dụng **GenAI Module Pattern** để tạo một domain-driven module chuyên biệt cho tất cả AI/Generative AI functionality. Module này hoàn toàn self-contained và có thể scale thành microservice riêng trong tương lai.

### **Core Principles:**
- **Domain-Driven Design:** GenAI là một business domain riêng biệt
- **Self-Contained:** Module chứa tất cả AI-related logic
- **Provider Agnostic:** Support multiple AI providers (OpenAI, Gemini, Mock)
- **Microservice Ready:** Dễ dàng extract thành separate service
- **Clean Interfaces:** Clear contracts với rest of application

---

## 🏗️ **GENAI MODULE STRUCTURE**

```
app/genai/
├── __init__.py                    # Module exports & initialization
├── clients/                       # External AI Service Clients
│   ├── __init__.py
│   ├── base.py                   # Abstract client interface
│   ├── openai_client.py          # OpenAI GPT integration
│   ├── gemini_client.py          # Google Gemini integration
│   ├── mock_client.py            # Testing & development client
│   └── factory.py                # Client factory pattern
├── generators/                    # Generation Algorithms
│   ├── __init__.py
│   ├── exam_generator.py         # High-level exam generation
│   └── question_generator.py     # Individual question generation
├── services/                      # GenAI Business Logic
│   ├── __init__.py
│   └── genai_service.py          # Main GenAI orchestrator
├── schemas/                       # GenAI Data Models
│   ├── __init__.py
│   ├── requests.py               # Request schemas
│   └── responses.py              # Response schemas
├── prompts/                       # AI Prompt Templates
│   ├── __init__.py
│   ├── exam_prompts.py           # Exam generation prompts
│   └── question_prompts.py       # Question-specific prompts
└── utils/                         # GenAI Utilities
    ├── __init__.py
    └── content_analyzer.py       # Content analysis & preprocessing
```

---

## 🔧 **CORE COMPONENTS**

### **1. Client Layer (`genai/clients/`)**

#### **Base Client Interface:**
```python
# app/genai/clients/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from enum import Enum

class AIProvider(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    GEMINI = "gemini"
    MOCK = "mock"

class BaseAIClient(ABC):
    """Abstract base class for AI service clients"""
    
    @abstractmethod
    async def generate_content(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate content using AI provider"""
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if client is properly configured"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get client capabilities and limits"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check client health and connectivity"""
        pass
```

#### **OpenAI Client Implementation:**
```python
# app/genai/clients/openai_client.py
import openai
from app.core.config import settings
from .base import BaseAIClient

class OpenAIClient(BaseAIClient):
    """OpenAI GPT client for content generation"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.ai_request_timeout
        )
        self.model = settings.openai_model or "gpt-4o-mini"
        self.max_tokens = settings.openai_max_tokens or 2000
    
    async def generate_content(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate content using OpenAI GPT"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": kwargs.get("system_prompt", "")},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                response_format={"type": "json_object"} if kwargs.get("json_mode") else None
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "usage": response.usage.model_dump() if response.usage else None,
                "model": response.model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def is_configured(self) -> bool:
        return bool(settings.openai_api_key)
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "provider": "OpenAI",
            "model": self.model,
            "max_tokens": self.max_tokens,
            "supports_json": True,
            "supports_streaming": True,
            "cost_per_1k_tokens": 0.0005,
            "languages": ["en", "vi", "fr", "es", "de", "ja", "ko", "zh"]
        }
    
    async def health_check(self) -> bool:
        try:
            await self.client.models.retrieve(self.model)
            return True
        except Exception:
            return False
```

#### **Client Factory:**
```python
# app/genai/clients/factory.py
from typing import Dict, Type, List
from .base import BaseAIClient, AIProvider
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient
from .mock_client import MockClient

class AIClientFactory:
    """Factory for creating AI clients"""
    
    _clients: Dict[AIProvider, Type[BaseAIClient]] = {
        AIProvider.OPENAI: OpenAIClient,
        AIProvider.GEMINI: GeminiClient,
        AIProvider.MOCK: MockClient
    }
    
    @classmethod
    def create_client(cls, provider: AIProvider) -> BaseAIClient:
        """Create AI client instance"""
        if provider not in cls._clients:
            raise ValueError(f"Unsupported AI provider: {provider}")
        
        client_class = cls._clients[provider]
        client = client_class()
        
        if not client.is_configured():
            raise ValueError(f"Client {provider} is not properly configured")
        
        return client
    
    @classmethod
    async def get_available_clients(cls) -> List[Dict[str, Any]]:
        """Get list of available and healthy clients"""
        available = []
        
        for provider, client_class in cls._clients.items():
            try:
                client = client_class()
                
                if client.is_configured():
                    is_healthy = await client.health_check()
                    capabilities = client.get_capabilities()
                    
                    available.append({
                        "provider": provider.value,
                        "is_healthy": is_healthy,
                        "status": "available" if is_healthy else "configured_but_unhealthy",
                        **capabilities
                    })
                else:
                    available.append({
                        "provider": provider.value,
                        "is_healthy": False,
                        "status": "not_configured"
                    })
                    
            except Exception as e:
                available.append({
                    "provider": provider.value,
                    "is_healthy": False,
                    "status": "error",
                    "error": str(e)
                })
        
        return available
```

---

### **2. Prompt Templates (`genai/prompts/`)**

#### **Exam Generation Prompts:**
```python
# app/genai/prompts/exam_prompts.py
from typing import Dict, Any

class ExamPrompts:
    """Centralized exam generation prompts"""
    
    SYSTEM_PROMPT = """You are an expert exam creator. Your task is to generate high-quality, educational exam questions based on provided content.

Requirements:
- Create questions that test understanding, not just memorization
- Ensure questions are clear and unambiguous
- Provide accurate and helpful explanations
- Follow the specified difficulty level
- Return response in valid JSON format
"""

    @staticmethod
    def generate_exam_prompt(
        content: str,
        exam_title: str,
        question_count: int,
        difficulty: str,
        question_types: list
    ) -> str:
        """Generate prompt for full exam creation"""
        
        question_types_str = ", ".join(question_types)
        
        return f"""Based on the following content, create an exam titled "{exam_title}" with {question_count} questions.

CONTENT:
{content}

REQUIREMENTS:
- Difficulty Level: {difficulty}
- Question Types: {question_types_str}
- Each question should test different concepts from the content
- Provide clear explanations for all answers

OUTPUT FORMAT (JSON):
{{
  "exam_title": "{exam_title}",
  "questions": [
    {{
      "question_id": "q1",
      "question_text": "Question here?",
      "question_type": "multiple_choice",
      "options": [
        {{"option_id": "A", "text": "Option A", "is_correct": false}},
        {{"option_id": "B", "text": "Option B", "is_correct": true}},
        {{"option_id": "C", "text": "Option C", "is_correct": false}},
        {{"option_id": "D", "text": "Option D", "is_correct": false}}
      ],
      "correct_answer": "B",
      "explanation": "Explanation here",
      "difficulty": "{difficulty}",
      "points": 1
    }}
  ],
  "metadata": {{
    "total_questions": {question_count},
    "difficulty": "{difficulty}",
    "estimated_duration": 30
  }}
}}

Generate the exam now:"""

    @staticmethod
    def get_difficulty_guidelines(difficulty: str) -> str:
        """Get difficulty-specific guidelines"""
        guidelines = {
            "easy": "Focus on basic concepts, definitions, and direct recall. Questions should be straightforward.",
            "medium": "Test understanding and application of concepts. Include some analysis and synthesis.",
            "hard": "Require critical thinking, complex analysis, and application to new situations."
        }
        return guidelines.get(difficulty, guidelines["medium"])
```

#### **Question-Specific Prompts:**
```python
# app/genai/prompts/question_prompts.py
class QuestionPrompts:
    """Prompts for specific question types"""
    
    MULTIPLE_CHOICE_PROMPT = """Create a multiple choice question with 4 options (A, B, C, D) where exactly one option is correct.
    
Requirements:
- Question should be clear and specific
- All options should be plausible
- Incorrect options should be reasonable but clearly wrong
- Provide explanation for why the correct answer is right
"""

    TRUE_FALSE_PROMPT = """Create a true/false question that tests a specific concept.
    
Requirements:
- Statement should be clear and unambiguous
- Avoid trick questions or overly complex statements
- Provide explanation for the correct answer
"""

    SHORT_ANSWER_PROMPT = """Create a short answer question that requires 1-3 sentences to answer.
    
Requirements:
- Question should test understanding, not just recall
- Answer should be specific and measurable
- Provide sample correct answer and key points
"""
```

---

### **3. Content Analysis (`genai/utils/`)**

```python
# app/genai/utils/content_analyzer.py
import re
from typing import Dict, List, Any

class ContentAnalyzer:
    """Utility class for analyzing and preprocessing content"""
    
    @staticmethod
    def analyze_content(content: str) -> Dict[str, Any]:
        """Analyze content and provide metadata"""
        
        # Basic metrics
        word_count = len(content.split())
        char_count = len(content)
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        
        # Content complexity analysis
        avg_sentence_length = ContentAnalyzer._calculate_avg_sentence_length(content)
        reading_level = ContentAnalyzer._estimate_reading_level(content)
        
        # Topic extraction (basic keyword analysis)
        keywords = ContentAnalyzer._extract_keywords(content)
        
        # Question generation recommendations
        recommended_question_count = min(max(word_count // 100, 5), 50)
        
        return {
            "metrics": {
                "word_count": word_count,
                "character_count": char_count,
                "paragraph_count": paragraph_count,
                "avg_sentence_length": avg_sentence_length
            },
            "analysis": {
                "reading_level": reading_level,
                "complexity": "high" if avg_sentence_length > 20 else "medium" if avg_sentence_length > 15 else "low",
                "keywords": keywords[:10]  # Top 10 keywords
            },
            "recommendations": {
                "question_count": recommended_question_count,
                "difficulty": "medium",  # Default, can be adjusted based on content
                "question_types": ["multiple_choice", "true_false"] if word_count < 500 else ["multiple_choice", "true_false", "short_answer"]
            }
        }
    
    @staticmethod
    def _calculate_avg_sentence_length(content: str) -> float:
        """Calculate average sentence length"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0
        
        total_words = sum(len(sentence.split()) for sentence in sentences)
        return total_words / len(sentences)
    
    @staticmethod
    def _estimate_reading_level(content: str) -> str:
        """Estimate reading level based on content complexity"""
        avg_sentence_length = ContentAnalyzer._calculate_avg_sentence_length(content)
        
        if avg_sentence_length < 10:
            return "elementary"
        elif avg_sentence_length < 15:
            return "middle_school"
        elif avg_sentence_length < 20:
            return "high_school"
        else:
            return "college"
    
    @staticmethod
    def _extract_keywords(content: str) -> List[str]:
        """Extract key terms from content (basic implementation)"""
        # Remove common stop words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        # Extract words (simple tokenization)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Filter out stop words
        keywords = [word for word in words if word not in stop_words]
        
        # Count frequency and return most common
        from collections import Counter
        word_freq = Counter(keywords)
        
        return [word for word, count in word_freq.most_common(20)]
    
    @staticmethod
    def chunk_content(content: str, max_chunk_size: int = 4000) -> List[str]:
        """Split large content into manageable chunks for AI processing"""
        if len(content) <= max_chunk_size:
            return [content]
        
        # Try to split by paragraphs first
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk + paragraph) <= max_chunk_size:
                current_chunk += paragraph + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If paragraphs are too long, split by sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= max_chunk_size:
                final_chunks.append(chunk)
            else:
                # Split by sentences
                sentences = re.split(r'[.!?]+', chunk)
                current_sentence_chunk = ""
                
                for sentence in sentences:
                    if len(current_sentence_chunk + sentence) <= max_chunk_size:
                        current_sentence_chunk += sentence + '. '
                    else:
                        if current_sentence_chunk:
                            final_chunks.append(current_sentence_chunk.strip())
                        current_sentence_chunk = sentence + '. '
                
                if current_sentence_chunk:
                    final_chunks.append(current_sentence_chunk.strip())
        
        return final_chunks
```

---

### **4. Generation Logic (`genai/generators/`)**

```python
# app/genai/generators/exam_generator.py
from typing import Dict, Any, List
import json
import logging
from ..clients.factory import AIClientFactory
from ..clients.base import AIProvider
from ..prompts.exam_prompts import ExamPrompts
from ..utils.content_analyzer import ContentAnalyzer
from ..schemas.requests import ExamGenerationRequest
from ..schemas.responses import ExamGenerationResponse

logger = logging.getLogger(__name__)

class ExamGenerator:
    """High-level exam generation orchestrator"""
    
    def __init__(self):
        self.content_analyzer = ContentAnalyzer()
        self.prompts = ExamPrompts()
    
    async def generate_exam(
        self, 
        request: ExamGenerationRequest,
        provider: AIProvider = AIProvider.GEMINI
    ) -> ExamGenerationResponse:
        """Generate complete exam from content"""
        
        try:
            # 1. Analyze content
            content_analysis = self.content_analyzer.analyze_content(request.content)
            logger.info(f"Content analysis: {content_analysis['metrics']['word_count']} words")
            
            # 2. Adjust request based on analysis
            adjusted_request = self._adjust_request_based_on_analysis(request, content_analysis)
            
            # 3. Create AI client
            ai_client = AIClientFactory.create_client(provider)
            
            # 4. Generate exam content
            exam_result = await self._generate_exam_content(ai_client, adjusted_request)
            
            # 5. Validate and format response
            return self._format_exam_response(exam_result, provider, content_analysis)
            
        except Exception as e:
            logger.error(f"Exam generation failed: {e}")
            return ExamGenerationResponse(
                success=False,
                error=str(e),
                provider=provider.value
            )
    
    def _adjust_request_based_on_analysis(
        self, 
        request: ExamGenerationRequest, 
        analysis: Dict[str, Any]
    ) -> ExamGenerationRequest:
        """Adjust generation request based on content analysis"""
        
        # Adjust question count based on content length
        recommended_count = analysis["recommendations"]["question_count"]
        if request.question_count > recommended_count:
            logger.warning(f"Requested {request.question_count} questions, but content supports {recommended_count}")
            request.question_count = min(request.question_count, recommended_count)
        
        # Suggest question types based on content complexity
        if analysis["analysis"]["complexity"] == "low":
            request.question_types = ["multiple_choice", "true_false"]
        elif analysis["analysis"]["complexity"] == "high":
            request.question_types.extend(["short_answer"])
        
        return request
    
    async def _generate_exam_content(
        self, 
        ai_client, 
        request: ExamGenerationRequest
    ) -> Dict[str, Any]:
        """Generate exam content using AI client"""
        
        # Create generation prompt
        prompt = self.prompts.generate_exam_prompt(
            content=request.content,
            exam_title=request.exam_title,
            question_count=request.question_count,
            difficulty=request.difficulty,
            question_types=request.question_types
        )
        
        # Generate content
        result = await ai_client.generate_content(
            prompt=prompt,
            system_prompt=self.prompts.SYSTEM_PROMPT,
            temperature=0.7,
            json_mode=True
        )
        
        if not result["success"]:
            raise Exception(f"AI generation failed: {result['error']}")
        
        # Parse JSON response
        try:
            exam_data = json.loads(result["content"])
            return exam_data
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response from AI: {e}")
    
    def _format_exam_response(
        self, 
        exam_data: Dict[str, Any], 
        provider: AIProvider,
        content_analysis: Dict[str, Any]
    ) -> ExamGenerationResponse:
        """Format final exam response"""
        
        return ExamGenerationResponse(
            success=True,
            exam_data=exam_data,
            provider=provider.value,
            content_analysis=content_analysis,
            generated_at=datetime.utcnow()
        )
```

---

### **5. Main GenAI Service (`genai/services/`)**

```python
# app/genai/services/genai_service.py
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.services.document_service import DocumentService
from ..generators.exam_generator import ExamGenerator
from ..clients.base import AIProvider
from ..clients.factory import AIClientFactory
from ..schemas.requests import ExamGenerationRequest
from ..schemas.responses import ExamGenerationResponse

logger = logging.getLogger(__name__)

class GenAIService:
    """Main GenAI service for orchestrating AI operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.document_service = DocumentService(db)
        self.exam_generator = ExamGenerator()
    
    async def generate_exam_from_file(
        self,
        file_id: str,
        user_id: str,
        exam_title: str,
        question_count: int = 10,
        difficulty: str = "medium",
        provider: AIProvider = AIProvider.GEMINI,
        question_types: Optional[list] = None
    ) -> Dict[str, Any]:
        """Generate exam from uploaded file"""
        
        try:
            logger.info(f"Generating exam from file {file_id} using {provider}")
            
            # 1. Get file content
            content_result = await self.document_service.get_file_content(file_id, user_id)
            if not content_result["success"]:
                return {
                    "success": False,
                    "error": content_result["error"],
                    "file_id": file_id
                }
            
            # 2. Validate content
            content = content_result["content"]
            if len(content.strip()) < 100:
                return {
                    "success": False,
                    "error": "Insufficient content for exam generation (minimum 100 characters)",
                    "file_id": file_id,
                    "content_length": len(content)
                }
            
            # 3. Create generation request
            generation_request = ExamGenerationRequest(
                content=content,
                exam_title=exam_title,
                question_count=question_count,
                difficulty=difficulty,
                question_types=question_types or ["multiple_choice"]
            )
            
            # 4. Generate exam
            exam_response = await self.exam_generator.generate_exam(
                request=generation_request,
                provider=provider
            )
            
            # 5. Format response
            if exam_response.success:
                return {
                    "success": True,
                    "exam_data": exam_response.exam_data,
                    "file_id": file_id,
                    "provider": exam_response.provider,
                    "content_length": len(content),
                    "content_analysis": exam_response.content_analysis,
                    "generated_at": exam_response.generated_at
                }
            else:
                return {
                    "success": False,
                    "error": exam_response.error,
                    "file_id": file_id,
                    "provider": exam_response.provider
                }
            
        except Exception as e:
            logger.error(f"GenAI service error for file {file_id}: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "file_id": file_id
            }
    
    async def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get available AI providers"""
        return await AIClientFactory.get_available_clients()
    
    async def test_provider_health(self, provider: AIProvider) -> Dict[str, Any]:
        """Test specific provider health"""
        try:
            client = AIClientFactory.create_client(provider)
            is_healthy = await client.health_check()
            capabilities = client.get_capabilities()
            
            return {
                "provider": provider.value,
                "is_configured": client.is_configured(),
                "is_healthy": is_healthy,
                "capabilities": capabilities
            }
            
        except Exception as e:
            return {
                "provider": provider.value,
                "is_configured": False,
                "is_healthy": False,
                "error": str(e)
            }
```

---

## 🔗 **INTEGRATION WITH MAIN APPLICATION**

### **Main Services Integration:**
```python
# app/services/exam_service.py
from app.genai.services.genai_service import GenAIService
from app.genai.clients.base import AIProvider

class ExamService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.genai_service = GenAIService(db_session)  # Use GenAI service
        # ... other dependencies
    
    async def generate_exam_from_file(
        self, 
        file_id: str, 
        user_id: str, 
        config: dict
    ) -> Dict[str, Any]:
        """Generate exam using GenAI service"""
        
        provider = AIProvider(config.get("ai_client", "gemini"))
        
        return await self.genai_service.generate_exam_from_file(
            file_id=file_id,
            user_id=user_id,
            exam_title=config["exam_title"],
            question_count=config.get("question_count", 10),
            difficulty=config.get("difficulty", "medium"),
            provider=provider,
            question_types=config.get("question_types", ["multiple_choice"])
        )
```

### **API Integration:**
```python
# app/api/upload.py
from app.genai.services.genai_service import GenAIService
from app.genai.clients.base import AIProvider

@router.get("/ai/providers")
async def get_available_ai_providers(
    current_user: User = CurrentUser,
    db: AsyncSession = Depends(get_db_session)
):
    """Get available AI providers"""
    genai_service = GenAIService(db)
    providers = await genai_service.get_available_providers()
    
    return {
        "providers": providers,
        "total": len(providers),
        "default": "gemini"
    }

@router.post("/{file_id}/generate-exam")
async def generate_exam_from_file(
    file_id: str,
    request: ExamFromFileRequest,
    current_user: User = CurrentUser,
    db: AsyncSession = Depends(get_db_session)
):
    """Generate exam from uploaded file using GenAI"""
    genai_service = GenAIService(db)
    
    result = await genai_service.generate_exam_from_file(
        file_id=file_id,
        user_id=current_user.id,
        exam_title=request.exam_title,
        question_count=request.question_count,
        difficulty=request.difficulty,
        provider=AIProvider(request.ai_client),
        question_types=request.question_types
    )
    
    return result
```

---

## 📊 **BENEFITS OF GENAI MODULE**

### **✅ Domain-Driven Design:**
- **Clear boundaries** - All AI logic in one module
- **Business focus** - GenAI is a distinct business capability
- **Self-contained** - Module can evolve independently

### **✅ Scalability:**
- **Microservice ready** - Easy to extract as separate service
- **Team ownership** - AI team owns genai/ module
- **Independent deployment** - Can be deployed separately

### **✅ Maintainability:**
- **Single responsibility** - Module only handles AI/GenAI
- **Clear interfaces** - Well-defined contracts with main app
- **Testing isolation** - AI logic can be tested independently

### **✅ Extensibility:**
- **New AI providers** - Easy to add new clients
- **New AI features** - Text generation, image analysis, etc.
- **Advanced prompting** - Centralized prompt management

---

## 🚀 **MIGRATION STRATEGY**

### **From Current State:**
1. **Create GenAI module structure**
2. **Move existing AI code** from `utils/ai_generator.py`
3. **Refactor to new interfaces**
4. **Update service integrations**
5. **Test and validate**

### **Implementation Order:**
1. **Week 1:** GenAI module foundation + Mock client
2. **Week 2:** Real AI clients (OpenAI, Gemini)
3. **Week 3:** Integration + Testing + Documentation

---

*GenAI Module Architecture - Ready for Implementation! 🚀*
