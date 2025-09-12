# 🤖 AI Architecture Documentation

## 🎯 **OVERVIEW**

Exam Hub sử dụng **AI Client Pattern** để tích hợp đa nhà cung cấp AI, cho phép người dùng lựa chọn giữa OpenAI GPT và Google Gemini để tạo đề thi từ tài liệu.

### **Core Principles:**
- **Provider Agnostic:** Dễ dàng thêm/thay đổi AI provider
- **Async First:** Non-blocking AI operations  
- **Error Resilient:** Graceful handling của AI failures
- **Cost Conscious:** Token tracking và usage monitoring
- **Quality Focused:** Response validation và fallback mechanisms

---

## 🏗️ **ARCHITECTURE OVERVIEW**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer    │    │  Service Layer  │    │  Client Layer   │
│                │    │                 │    │                 │
│ POST /generate │◄──►│   AIService     │◄──►│  OpenAIClient   │
│ GET /clients   │    │                 │    │  GeminiClient   │
│                │    │ ClientFactory   │    │  MockClient     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Schemas       │    │ Document        │    │ External APIs   │
│                 │    │ Service         │    │                 │
│ ExamRequest     │    │                 │    │ OpenAI API      │
│ ExamResponse    │    │ Content         │    │ Gemini API      │
│ ClientInfo      │    │ Extraction      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 📁 **MODULE STRUCTURE**

### **Directory Layout:**
```
app/ai/
├── __init__.py
├── clients/                    # AI Service Clients
│   ├── __init__.py
│   ├── base.py                # Abstract base client
│   ├── openai_client.py       # OpenAI GPT integration
│   ├── gemini_client.py       # Google Gemini integration
│   └── mock_client.py         # Testing & development
├── services/                   # Business Logic Layer
│   ├── __init__.py
│   ├── ai_service.py          # Main AI orchestrator
│   └── client_factory.py      # Client instantiation
└── schemas/                    # Data Models
    ├── __init__.py
    ├── requests.py            # API request schemas
    └── responses.py           # API response schemas
```

---

## 🔧 **CORE COMPONENTS**

### **1. Base AI Client Interface**

```python
# app/ai/clients/base.py
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List

class AIClientType(str, Enum):
    """Supported AI service providers"""
    OPENAI = "openai"
    GEMINI = "gemini"
    MOCK = "mock"

class BaseAIClient(ABC):
    """Abstract base class for AI service clients"""
    
    @abstractmethod
    async def generate_exam(self, request: ExamGenerationRequest) -> Dict[str, Any]:
        """Generate exam questions from content"""
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if client is properly configured with API keys"""
        pass
    
    @abstractmethod
    def get_client_info(self) -> Dict[str, Any]:
        """Get client capabilities and information"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Verify client connectivity and health"""
        pass
```

### **2. OpenAI Client Implementation**

```python
# app/ai/clients/openai_client.py
import openai
from app.core.config import settings

class OpenAIClient(BaseAIClient):
    """OpenAI GPT client for exam generation"""
    
    def __init__(self):
        """Initialize OpenAI async client"""
        self.client = openai.AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.ai_request_timeout
        )
        self.model = settings.openai_model or "gpt-4o-mini"
        self.max_tokens = settings.openai_max_tokens or 2000
    
    async def generate_exam(self, request: ExamGenerationRequest) -> Dict[str, Any]:
        """Generate exam using OpenAI GPT"""
        try:
            prompt = self._create_prompt(request)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            return self._parse_response(response.choices[0].message.content)
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return {"error": f"OpenAI API error: {str(e)}"}
        except Exception as e:
            logger.error(f"OpenAI client error: {e}")
            return {"error": f"Generation failed: {str(e)}"}
    
    def is_configured(self) -> bool:
        """Check if OpenAI API key is configured"""
        return bool(settings.openai_api_key)
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get OpenAI client information"""
        return {
            "name": "OpenAI",
            "model": self.model,
            "max_tokens": self.max_tokens,
            "supports": ["multiple_choice", "true_false", "short_answer", "essay"],
            "languages": ["en", "vi", "fr", "es", "de"],
            "cost_per_1k_tokens": 0.0005  # Example pricing
        }
    
    async def health_check(self) -> bool:
        """Verify OpenAI API connectivity"""
        try:
            await self.client.models.retrieve(self.model)
            return True
        except Exception:
            return False
```

### **3. Gemini Client Implementation**

```python
# app/ai/clients/gemini_client.py
from app.core.config import create_gemini_instance, settings

class GeminiClient(BaseAIClient):
    """Google Gemini client for exam generation"""
    
    def __init__(self):
        """Initialize Gemini client with lazy loading"""
        self._llm = None
        self.model = "gemini-2.0-flash-exp"
    
    @property
    def llm(self):
        """Lazy-load Gemini instance when needed"""
        if self._llm is None:
            self._llm = create_gemini_instance()
            if self._llm is None:
                raise Exception("Cannot create Gemini instance - API key not configured")
        return self._llm
    
    async def generate_exam(self, request: ExamGenerationRequest) -> Dict[str, Any]:
        """Generate exam using Google Gemini"""
        try:
            prompt = self._create_prompt(request)
            
            # Use async invoke for non-blocking operation
            response = await self.llm.ainvoke(prompt)
            
            return self._parse_response(response.content)
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return {"error": f"Gemini generation failed: {str(e)}"}
    
    def is_configured(self) -> bool:
        """Check if Gemini API key is configured"""
        return bool(settings.gemini_api_key)
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get Gemini client information"""
        return {
            "name": "Google Gemini",
            "model": self.model,
            "max_tokens": 8000,
            "supports": ["multiple_choice", "true_false", "essay", "coding"],
            "languages": ["en", "vi", "ja", "ko", "zh"],
            "cost_per_1k_tokens": 0.0003  # Example pricing
        }
    
    async def health_check(self) -> bool:
        """Verify Gemini API connectivity"""
        try:
            test_response = await self.llm.ainvoke("Hello, are you working?")
            return bool(test_response and test_response.content)
        except Exception:
            return False
```

### **4. AI Client Factory**

```python
# app/ai/services/client_factory.py
class AIClientFactory:
    """Factory for creating and managing AI clients"""
    
    _clients = {
        AIClientType.OPENAI: OpenAIClient,
        AIClientType.GEMINI: GeminiClient,
        AIClientType.MOCK: MockClient
    }
    
    @classmethod
    def create_client(cls, client_type: AIClientType) -> BaseAIClient:
        """Create AI client instance with validation"""
        if client_type not in cls._clients:
            raise ValueError(f"Unsupported AI client: {client_type}")
        
        client_class = cls._clients[client_type]
        client = client_class()
        
        if not client.is_configured():
            raise ValueError(f"Client {client_type} is not properly configured")
        
        logger.info(f"Created AI client: {client_type}")
        return client
    
    @classmethod
    async def get_available_clients(cls) -> List[Dict[str, Any]]:
        """Get list of available and healthy AI clients"""
        available = []
        
        for client_type, client_class in cls._clients.items():
            try:
                client = client_class()
                
                if client.is_configured():
                    # Check health status
                    is_healthy = await client.health_check()
                    
                    client_info = client.get_client_info()
                    client_info.update({
                        "type": client_type.value,
                        "is_healthy": is_healthy,
                        "status": "available" if is_healthy else "configured_but_unhealthy"
                    })
                    
                    available.append(client_info)
                    
            except Exception as e:
                logger.warning(f"Client {client_type} check failed: {e}")
                available.append({
                    "type": client_type.value,
                    "name": client_type.value.title(),
                    "is_healthy": False,
                    "status": "configuration_error",
                    "error": str(e)
                })
        
        return available
    
    @classmethod
    def get_default_client_type(cls) -> AIClientType:
        """Get default client type from configuration"""
        default = settings.default_ai_client.lower()
        
        try:
            return AIClientType(default)
        except ValueError:
            logger.warning(f"Invalid default client '{default}', using Gemini")
            return AIClientType.GEMINI
```

### **5. Main AI Service**

```python
# app/ai/services/ai_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.document_service import DocumentService

class AIService:
    """Main AI service for orchestrating exam generation"""
    
    def __init__(self, db: AsyncSession):
        """Initialize AI service with dependencies"""
        self.db = db
        self.document_service = DocumentService(db)
        self.logger = logging.getLogger(__name__)
    
    async def generate_exam_from_file(
        self,
        file_id: str,
        user_id: str,
        client_type: AIClientType,
        exam_config: ExamConfig
    ) -> ExamGenerationResult:
        """Generate exam from uploaded file using specified AI client"""
        
        try:
            # 1. Retrieve file content
            self.logger.info(f"Generating exam from file {file_id} using {client_type}")
            
            content_result = await self.document_service.get_file_content(file_id, user_id)
            if not content_result["success"]:
                return ExamGenerationResult(
                    success=False,
                    error=content_result["error"],
                    file_id=file_id
                )
            
            # 2. Validate content length
            content = content_result["content"]
            if len(content.strip()) < 100:
                return ExamGenerationResult(
                    success=False,
                    error="Insufficient content for exam generation (minimum 100 characters)",
                    file_id=file_id
                )
            
            # 3. Create AI client
            try:
                ai_client = AIClientFactory.create_client(client_type)
            except ValueError as e:
                return ExamGenerationResult(
                    success=False,
                    error=str(e),
                    file_id=file_id
                )
            
            # 4. Prepare generation request
            generation_request = ExamGenerationRequest(
                content=content,
                exam_title=exam_config.exam_title,
                question_count=exam_config.question_count,
                difficulty=exam_config.difficulty,
                question_types=exam_config.question_types
            )
            
            # 5. Generate exam
            generation_result = await ai_client.generate_exam(generation_request)
            
            # 6. Validate and format result
            if "error" in generation_result:
                return ExamGenerationResult(
                    success=False,
                    error=generation_result["error"],
                    file_id=file_id,
                    client_used=client_type.value
                )
            
            # 7. Return successful result
            return ExamGenerationResult(
                success=True,
                exam_data=generation_result,
                file_id=file_id,
                client_used=client_type.value,
                content_length=len(content),
                generation_time=time.time() - start_time
            )
            
        except Exception as e:
            self.logger.error(f"AI service error for file {file_id}: {e}")
            return ExamGenerationResult(
                success=False,
                error=f"Internal error: {str(e)}",
                file_id=file_id
            )
    
    async def get_available_clients(self) -> List[Dict[str, Any]]:
        """Get available AI clients for user selection"""
        return await AIClientFactory.get_available_clients()
    
    async def test_client_connectivity(self, client_type: AIClientType) -> Dict[str, Any]:
        """Test specific client connectivity"""
        try:
            client = AIClientFactory.create_client(client_type)
            is_healthy = await client.health_check()
            
            return {
                "client_type": client_type.value,
                "is_configured": client.is_configured(),
                "is_healthy": is_healthy,
                "client_info": client.get_client_info()
            }
            
        except Exception as e:
            return {
                "client_type": client_type.value,
                "is_configured": False,
                "is_healthy": False,
                "error": str(e)
            }
```

---

## 📊 **DATA SCHEMAS**

### **Request Schemas:**

```python
# app/ai/schemas/requests.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class ExamGenerationRequest(BaseModel):
    """Request for AI exam generation"""
    content: str = Field(..., min_length=100, description="Source content for exam generation")
    exam_title: str = Field(..., min_length=1, max_length=200)
    question_count: int = Field(default=10, ge=1, le=50)
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    question_types: List[QuestionType] = [QuestionType.MULTIPLE_CHOICE]
    language: str = Field(default="en", description="Target language for questions")
    subject_hint: Optional[str] = Field(None, description="Subject area hint for better context")

class ExamFromFileRequest(BaseModel):
    """API request for generating exam from uploaded file"""
    exam_title: str = Field(..., min_length=1, max_length=200)
    question_count: int = Field(default=10, ge=1, le=50)
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    ai_client: AIClientType = AIClientType.GEMINI
    question_types: List[QuestionType] = [QuestionType.MULTIPLE_CHOICE]
    language: str = Field(default="en")
    subject_hint: Optional[str] = None

class ExamConfig(BaseModel):
    """Configuration for exam generation"""
    exam_title: str
    question_count: int = 10
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    question_types: List[QuestionType] = [QuestionType.MULTIPLE_CHOICE]
    language: str = "en"
    subject_hint: Optional[str] = None
```

### **Response Schemas:**

```python
# app/ai/schemas/responses.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class QuestionOption(BaseModel):
    """Single option for multiple choice questions"""
    option_id: str  # A, B, C, D
    text: str
    is_correct: bool = False

class GeneratedQuestion(BaseModel):
    """Single generated question"""
    question_id: str
    question_text: str
    question_type: QuestionType
    options: Optional[List[QuestionOption]] = None  # For multiple choice
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: DifficultyLevel
    points: int = 1

class ExamGenerationResult(BaseModel):
    """Result of exam generation process"""
    success: bool
    exam_data: Optional[Dict[str, Any]] = None
    file_id: str
    client_used: Optional[str] = None
    content_length: Optional[int] = None
    generation_time: Optional[float] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ClientInfo(BaseModel):
    """Information about an AI client"""
    type: str
    name: str
    model: str
    max_tokens: int
    supports: List[str]
    languages: List[str]
    is_healthy: bool
    status: str
    cost_per_1k_tokens: Optional[float] = None
    error: Optional[str] = None

class AIClientsResponse(BaseModel):
    """Response for available AI clients"""
    available_clients: List[ClientInfo]
    default_client: str
    total_clients: int
```

---

## ⚙️ **CONFIGURATION**

### **Environment Variables:**

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000

# Google Gemini Configuration (existing)
GEMINI_API_KEY=your-gemini-key-here

# AI General Settings
DEFAULT_AI_CLIENT=gemini
AI_REQUEST_TIMEOUT=60
AI_MAX_RETRIES=3
AI_RETRY_DELAY=2

# Feature Flags
ENABLE_OPENAI_CLIENT=true
ENABLE_GEMINI_CLIENT=true
ENABLE_MOCK_CLIENT=true
```

### **Settings Class Updates:**

```python
# app/core/config.py
class Settings:
    # ... existing settings ...
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    openai_max_tokens: int = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
    
    # AI General Settings
    default_ai_client: str = os.getenv('DEFAULT_AI_CLIENT', 'gemini')
    ai_request_timeout: int = int(os.getenv('AI_REQUEST_TIMEOUT', '60'))
    ai_max_retries: int = int(os.getenv('AI_MAX_RETRIES', '3'))
    ai_retry_delay: int = int(os.getenv('AI_RETRY_DELAY', '2'))
    
    # Feature Flags
    enable_openai_client: bool = os.getenv('ENABLE_OPENAI_CLIENT', 'true').lower() == 'true'
    enable_gemini_client: bool = os.getenv('ENABLE_GEMINI_CLIENT', 'true').lower() == 'true'
    enable_mock_client: bool = os.getenv('ENABLE_MOCK_CLIENT', 'true').lower() == 'true'
```

---

## 🔄 **INTEGRATION POINTS**

### **1. Document Service Integration**

```python
# Existing DocumentService provides:
async def get_file_content(self, file_id: str, user_id: str) -> Dict[str, Any]
async def get_processing_status(self, file_id: str, user_id: str) -> Dict[str, Any]

# AI Service uses DocumentService to:
# 1. Retrieve processed file content
# 2. Validate content availability
# 3. Get content metadata
```

### **2. Exam Service Integration**

```python
# Updated ExamService integration:
class ExamService:
    def __init__(self, db_session: AsyncSession):
        self.ai_service = AIService(db_session)  # New dependency
    
    async def generate_exam_from_text(self, file_content: str, ...):
        # Delegate to AI service for generation
        # Maintain existing interface for backward compatibility
```

### **3. API Layer Integration**

```python
# New endpoints in app/api/upload.py:
@router.get("/ai/clients")
@router.post("/{file_id}/generate-exam")

# Updated endpoints in app/api/exam.py:
@router.post("/generate")  # Updated to use new AI service
```

---

## 🚀 **DEPLOYMENT CONSIDERATIONS**

### **Production Configuration:**
- Separate API keys for different environments
- Rate limiting for AI API calls
- Monitoring and alerting for AI service health
- Cost tracking and budgeting
- Fallback mechanisms for service failures

### **Performance Optimization:**
- Connection pooling for AI clients
- Request caching for repeated content
- Async processing for large documents
- Queue system for batch processing

### **Security:**
- API key rotation and secure storage
- Request validation and sanitization
- Rate limiting per user
- Audit logging for AI requests

---

*Last updated: 2025-09-12*
*Version: 1.0*
