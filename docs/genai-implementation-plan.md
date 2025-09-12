# 🤖 GenAI Module Implementation Plan

## 📋 **PROJECT OVERVIEW**

**Objective:** Implement GenAI module với domain-driven architecture để tạo đề thi từ tài liệu uploaded  
**Timeline:** 3 tuần implementation + testing  
**Architecture:** GenAI Module Pattern với Clean Architecture principles  

---

## 🏗️ **GENAI MODULE STRUCTURE**

### **Target Architecture:**
```
backend/app/genai/
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

## 📊 **IMPLEMENTATION PHASES**

### **🔄 PHASE 1: GenAI Foundation (Week 1)**

#### **Day 1: Module Structure Setup**

**Tasks:**
- [ ] Create GenAI module directory structure
- [ ] Setup base interfaces and enums
- [ ] Create module initialization files
- [ ] Setup logging and basic configuration

**Commands:**
```bash
cd backend
mkdir -p app/genai/{clients,generators,services,schemas,prompts,utils}
touch app/genai/__init__.py
touch app/genai/clients/__init__.py
touch app/genai/generators/__init__.py
touch app/genai/services/__init__.py
touch app/genai/schemas/__init__.py
touch app/genai/prompts/__init__.py
touch app/genai/utils/__init__.py
```

**Deliverables:**
- ✅ Complete directory structure
- ✅ Base module initialization
- ✅ Import structure ready

---

#### **Day 2: Base Client Interface & Schemas**

**Implementation:**
```python
# app/genai/clients/base.py
from abc import ABC, abstractmethod
from enum import Enum

class AIProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    MOCK = "mock"

class BaseAIClient(ABC):
    @abstractmethod
    async def generate_content(self, prompt: str, **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        pass
```

**Tasks:**
- [ ] Implement `BaseAIClient` abstract class
- [ ] Create `AIProvider` enum
- [ ] Define core schemas in `schemas/requests.py` and `schemas/responses.py`
- [ ] Add error handling interfaces

**Deliverables:**
- ✅ Abstract client interface
- ✅ Core request/response schemas
- ✅ Error handling framework

---

#### **Day 3: Mock Client Implementation**

**Implementation:**
```python
# app/genai/clients/mock_client.py
class MockClient(BaseAIClient):
    async def generate_content(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # Generate realistic mock exam questions
        # Support different difficulty levels
        # Return structured JSON response
```

**Tasks:**
- [ ] Implement fully functional mock client
- [ ] Generate realistic test questions
- [ ] Support all question types (multiple choice, true/false, short answer)
- [ ] Add configurable difficulty levels
- [ ] Create comprehensive test data

**Deliverables:**
- ✅ Working mock client for development
- ✅ Realistic test data generation
- ✅ No external API dependencies

---

#### **Day 4: Client Factory & Content Analyzer**

**Implementation:**
```python
# app/genai/clients/factory.py
class AIClientFactory:
    @classmethod
    def create_client(cls, provider: AIProvider) -> BaseAIClient:
        # Client instantiation logic
        # Configuration validation
        # Health checking
    
    @classmethod
    async def get_available_clients(cls) -> List[Dict[str, Any]]:
        # Discover available clients
        # Check health status
        # Return capabilities

# app/genai/utils/content_analyzer.py
class ContentAnalyzer:
    @staticmethod
    def analyze_content(content: str) -> Dict[str, Any]:
        # Content metrics (word count, complexity)
        # Reading level estimation
        # Keyword extraction
        # Question generation recommendations
```

**Tasks:**
- [ ] Implement client factory with configuration validation
- [ ] Add client health checking and discovery
- [ ] Create content analyzer for preprocessing
- [ ] Add content metrics and recommendations
- [ ] Implement content chunking for large documents

**Deliverables:**
- ✅ Client factory implementation
- ✅ Content analysis utilities
- ✅ Health checking system

---

### **🔄 PHASE 2: AI Clients Implementation (Week 2)**

#### **Day 5-6: OpenAI Client**

**Implementation:**
```python
# app/genai/clients/openai_client.py
class OpenAIClient(BaseAIClient):
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.ai_request_timeout
        )
        self.model = settings.openai_model or "gpt-4o-mini"
    
    async def generate_content(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # Async OpenAI API integration
        # JSON mode support
        # Error handling and retries
        # Usage tracking
```

**Tasks:**
- [ ] Setup OpenAI async client with proper configuration
- [ ] Implement robust error handling and retry logic
- [ ] Add JSON mode support for structured responses
- [ ] Implement usage tracking and cost monitoring
- [ ] Add timeout and rate limiting handling
- [ ] Create comprehensive tests

**Configuration:**
```env
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
OPENAI_TIMEOUT=60
```

**Deliverables:**
- ✅ Production-ready OpenAI integration
- ✅ Robust error handling
- ✅ Cost and usage tracking

---

#### **Day 7-8: Gemini Client Migration**

**Migration Tasks:**
- [ ] Move existing code from `app/utils/ai_generator.py`
- [ ] Refactor to new `BaseAIClient` interface
- [ ] Improve existing Gemini implementation
- [ ] Add async support and better error handling
- [ ] Update all imports throughout codebase

**Implementation:**
```python
# app/genai/clients/gemini_client.py
class GeminiClient(BaseAIClient):
    def __init__(self):
        self._llm = None
    
    @property
    def llm(self):
        if self._llm is None:
            self._llm = create_gemini_instance()
        return self._llm
    
    async def generate_content(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # Migrate existing Gemini logic
        # Improve prompt engineering
        # Add better error handling
```

**Migration Steps:**
1. **Backup existing code**
2. **Create new Gemini client**
3. **Update service imports**
4. **Test compatibility**
5. **Remove old code**

**Deliverables:**
- ✅ Migrated Gemini client
- ✅ Improved implementation
- ✅ Backward compatibility maintained

---

#### **Day 9-10: Prompt Engineering & Templates**

**Implementation:**
```python
# app/genai/prompts/exam_prompts.py
class ExamPrompts:
    SYSTEM_PROMPT = """You are an expert exam creator..."""
    
    @staticmethod
    def generate_exam_prompt(content, exam_title, question_count, difficulty, question_types):
        # Sophisticated prompt engineering
        # Dynamic prompt generation based on parameters
        # Difficulty-specific guidelines
        # Question type instructions

# app/genai/prompts/question_prompts.py
class QuestionPrompts:
    MULTIPLE_CHOICE_PROMPT = """Create a multiple choice question..."""
    TRUE_FALSE_PROMPT = """Create a true/false question..."""
    SHORT_ANSWER_PROMPT = """Create a short answer question..."""
```

**Tasks:**
- [ ] Design comprehensive prompt templates
- [ ] Implement dynamic prompt generation
- [ ] Add difficulty-specific guidelines
- [ ] Create question type-specific prompts
- [ ] Add multilingual support
- [ ] Test prompt effectiveness

**Deliverables:**
- ✅ Professional prompt templates
- ✅ Dynamic prompt generation
- ✅ Multi-difficulty support

---

### **🔄 PHASE 3: Generation Logic & Integration (Week 3)**

#### **Day 11-12: Exam Generation Logic**

**Implementation:**
```python
# app/genai/generators/exam_generator.py
class ExamGenerator:
    def __init__(self):
        self.content_analyzer = ContentAnalyzer()
        self.prompts = ExamPrompts()
    
    async def generate_exam(self, request: ExamGenerationRequest, provider: AIProvider):
        # 1. Analyze content
        # 2. Adjust request based on analysis
        # 3. Create AI client
        # 4. Generate exam content
        # 5. Validate and format response

# app/genai/generators/question_generator.py
class QuestionGenerator:
    async def generate_question(self, content_chunk: str, question_type: str):
        # Generate individual questions
        # Support different question types
        # Quality validation
```

**Tasks:**
- [ ] Implement high-level exam generation orchestrator
- [ ] Add content analysis integration
- [ ] Create question generation logic
- [ ] Add response validation and formatting
- [ ] Implement quality checks
- [ ] Add comprehensive error handling

**Deliverables:**
- ✅ Complete generation pipeline
- ✅ Quality validation system
- ✅ Error recovery mechanisms

---

#### **Day 13-14: GenAI Service Integration**

**Implementation:**
```python
# app/genai/services/genai_service.py
class GenAIService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.document_service = DocumentService(db)
        self.exam_generator = ExamGenerator()
    
    async def generate_exam_from_file(
        self, file_id: str, user_id: str, exam_title: str,
        question_count: int, difficulty: str, provider: AIProvider
    ) -> Dict[str, Any]:
        # 1. Get file content from DocumentService
        # 2. Validate content sufficiency
        # 3. Create generation request
        # 4. Generate exam using ExamGenerator
        # 5. Format and return response
```

**Tasks:**
- [ ] Implement main GenAI service orchestrator
- [ ] Integrate with existing DocumentService
- [ ] Add file-to-exam pipeline
- [ ] Implement comprehensive error handling
- [ ] Add logging and monitoring
- [ ] Create service tests

**Deliverables:**
- ✅ Complete GenAI service
- ✅ Document service integration
- ✅ File-to-exam pipeline

---

#### **Day 15-16: API Integration**

**API Updates:**
```python
# app/api/upload.py (add new endpoints)
from app.genai.services.genai_service import GenAIService
from app.genai.clients.base import AIProvider

@router.get("/ai/providers")
async def get_available_ai_providers():
    """Get available AI providers"""
    genai_service = GenAIService(db)
    return await genai_service.get_available_providers()

@router.post("/{file_id}/generate-exam")
async def generate_exam_from_file(
    file_id: str,
    request: ExamFromFileRequest,
    current_user: User = CurrentUser,
    db: AsyncSession = Depends(get_db_session)
):
    """Generate exam from file using GenAI"""
    genai_service = GenAIService(db)
    return await genai_service.generate_exam_from_file(...)
```

**Service Updates:**
```python
# app/services/exam_service.py (update existing)
from app.genai.services.genai_service import GenAIService

class ExamService:
    def __init__(self, db_session: AsyncSession):
        self.genai_service = GenAIService(db_session)
        # ... other dependencies
    
    async def generate_exam_from_text(self, ...):
        # Delegate to GenAI service
        # Maintain backward compatibility
```

**Tasks:**
- [ ] Add new AI provider discovery endpoint
- [ ] Implement file-to-exam generation endpoint
- [ ] Update existing exam service to use GenAI
- [ ] Add request validation and error handling
- [ ] Update API documentation
- [ ] Test all endpoints

**Deliverables:**
- ✅ Complete API integration
- ✅ Backward compatibility
- ✅ Updated documentation

---

#### **Day 17-18: Configuration & Environment**

**Configuration Updates:**
```python
# app/core/config.py
class Settings:
    # ... existing settings ...
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    openai_max_tokens: int = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
    openai_timeout: int = int(os.getenv('OPENAI_TIMEOUT', '60'))
    
    # GenAI General Settings
    default_ai_provider: str = os.getenv('DEFAULT_AI_PROVIDER', 'gemini')
    ai_request_timeout: int = int(os.getenv('AI_REQUEST_TIMEOUT', '60'))
    ai_max_retries: int = int(os.getenv('AI_MAX_RETRIES', '3'))
    
    # Feature Flags
    enable_openai: bool = os.getenv('ENABLE_OPENAI', 'true').lower() == 'true'
    enable_gemini: bool = os.getenv('ENABLE_GEMINI', 'true').lower() == 'true'
    enable_mock_ai: bool = os.getenv('ENABLE_MOCK_AI', 'true').lower() == 'true'
```

**Environment Files:**
```env
# .env.example
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
OPENAI_TIMEOUT=60

# Google Gemini (existing)
GEMINI_API_KEY=your-gemini-key-here

# GenAI Settings
DEFAULT_AI_PROVIDER=gemini
AI_REQUEST_TIMEOUT=60
AI_MAX_RETRIES=3

# Feature Flags
ENABLE_OPENAI=true
ENABLE_GEMINI=true
ENABLE_MOCK_AI=true
```

**Tasks:**
- [ ] Add OpenAI configuration to settings
- [ ] Update environment variable documentation
- [ ] Add feature flags for AI providers
- [ ] Create development and production configs
- [ ] Update deployment configurations
- [ ] Add configuration validation

**Deliverables:**
- ✅ Complete configuration management
- ✅ Environment documentation
- ✅ Feature flag system

---

#### **Day 19-21: Testing & Documentation**

**Testing Strategy:**
```python
# tests/genai/
├── test_clients/
│   ├── test_openai_client.py
│   ├── test_gemini_client.py
│   ├── test_mock_client.py
│   └── test_factory.py
├── test_generators/
│   ├── test_exam_generator.py
│   └── test_question_generator.py
├── test_services/
│   └── test_genai_service.py
├── test_utils/
│   └── test_content_analyzer.py
└── integration/
    ├── test_api_integration.py
    └── test_end_to_end.py
```

**Documentation Updates:**
- [ ] Update API documentation with GenAI endpoints
- [ ] Create GenAI module documentation
- [ ] Add configuration guides
- [ ] Create troubleshooting guides
- [ ] Update deployment documentation

**Tasks:**
- [ ] Write comprehensive unit tests (90%+ coverage)
- [ ] Create integration tests
- [ ] Add end-to-end tests
- [ ] Performance testing
- [ ] Load testing for AI endpoints
- [ ] Update all documentation
- [ ] Create deployment guides

**Deliverables:**
- ✅ Complete test suite
- ✅ Updated documentation
- ✅ Deployment guides

---

## 🚀 **IMPLEMENTATION COMMANDS**

### **Phase 1 Setup (Day 1):**
```bash
cd backend

# Create GenAI module structure
mkdir -p app/genai/{clients,generators,services,schemas,prompts,utils}

# Create initialization files
touch app/genai/__init__.py
touch app/genai/clients/__init__.py
touch app/genai/generators/__init__.py
touch app/genai/services/__init__.py
touch app/genai/schemas/__init__.py
touch app/genai/prompts/__init__.py
touch app/genai/utils/__init__.py

# Create core files
touch app/genai/clients/base.py
touch app/genai/clients/factory.py
touch app/genai/clients/mock_client.py
touch app/genai/schemas/requests.py
touch app/genai/schemas/responses.py
touch app/genai/utils/content_analyzer.py
```

### **Development Commands:**
```bash
# Install additional dependencies
pip install openai>=1.0.0

# Run tests
pytest tests/genai/ -v

# Run with mock AI for development
export ENABLE_MOCK_AI=true
export DEFAULT_AI_PROVIDER=mock
uvicorn app.main:app --reload

# Run with real AI
export OPENAI_API_KEY=your-key
export ENABLE_OPENAI=true
export DEFAULT_AI_PROVIDER=openai
uvicorn app.main:app --reload
```

---

## 📋 **MIGRATION CHECKLIST**

### **Code Migration:**
- [ ] Move `app/utils/ai_generator.py` → `app/genai/clients/gemini_client.py`
- [ ] Update all imports from old location
- [ ] Refactor `ExamService` to use `GenAIService`
- [ ] Remove deprecated utility code
- [ ] Update `__init__.py` exports throughout

### **Configuration Migration:**
- [ ] Add OpenAI environment variables
- [ ] Update Docker configurations
- [ ] Add GenAI settings to config
- [ ] Update deployment scripts

### **Testing Migration:**
- [ ] Update existing AI tests
- [ ] Add new GenAI module tests
- [ ] Add integration tests
- [ ] Update test documentation

---

## 🎯 **SUCCESS CRITERIA**

### **Functional Requirements:**
✅ Users can select AI provider (OpenAI/Gemini/Mock)  
✅ Generate high-quality exams from uploaded files  
✅ Support multiple question types and difficulties  
✅ Robust error handling and graceful degradation  
✅ Content analysis and smart recommendations  

### **Technical Requirements:**
✅ Clean GenAI module architecture  
✅ Async/await throughout  
✅ 90%+ test coverage  
✅ Production-ready configuration  
✅ Comprehensive error handling  

### **Performance Requirements:**
✅ <30 seconds exam generation time  
✅ Support concurrent requests  
✅ Efficient content processing  
✅ Resource usage optimization  

---

## 🚨 **RISKS & MITIGATION**

### **Technical Risks:**
- **API Rate Limits:** Implement retry logic with exponential backoff
- **Large Content:** Add content chunking and processing optimization
- **AI Quality:** Add response validation and fallback mechanisms
- **Configuration:** Add comprehensive validation and clear error messages

### **Business Risks:**
- **AI Costs:** Add usage monitoring, budgets, and alerts
- **User Experience:** Add progress indicators and clear feedback
- **Quality Assurance:** Add content validation and human review workflows

---

## 📚 **RESOURCES & DEPENDENCIES**

### **New Dependencies:**
```txt
openai>=1.0.0          # OpenAI API client
tiktoken>=0.5.0        # Token counting for OpenAI
```

### **Documentation:**
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Google Gemini API](https://ai.google.dev/docs)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)

### **Environment Setup:**
```env
# Development
ENABLE_MOCK_AI=true
DEFAULT_AI_PROVIDER=mock

# Production
OPENAI_API_KEY=your-production-key
GEMINI_API_KEY=your-production-key
DEFAULT_AI_PROVIDER=gemini
ENABLE_OPENAI=true
ENABLE_GEMINI=true
ENABLE_MOCK_AI=false
```

---

## 🎉 **READY FOR IMPLEMENTATION**

### **Prerequisites Met:**
- ✅ Complete authentication system
- ✅ File upload and processing pipeline  
- ✅ Document content extraction working
- ✅ Database schema ready
- ✅ Clean architecture foundation
- ✅ Detailed GenAI module plan

### **Next Action:**
**Start GenAI Module Implementation - Week 1, Day 1**

```bash
# Execute Phase 1 setup:
cd backend
mkdir -p app/genai/{clients,generators,services,schemas,prompts,utils}
# Continue with base.py implementation...
```

---

*GenAI Implementation Plan - Ready to Execute! 🚀*
