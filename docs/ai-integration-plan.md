# 🤖 AI Integration Implementation Plan

## 📋 **TỔNG QUAN DỰ ÁN**

**Mục tiêu:** Tích hợp hệ thống AI đa nhà cung cấp để tạo đề thi từ tài liệu đã upload

**Timeline:** 2-3 tuần implementation + testing

**Architecture:** Clean Architecture với AI Client Pattern

---

## 🏗️ **KIẾN TRÚC AI MODULE**

### **Cấu trúc thư mục:**
```
backend/app/ai/
├── __init__.py
├── clients/                    # AI Service Clients
│   ├── __init__.py
│   ├── base.py                # BaseAIClient (Abstract)
│   ├── openai_client.py       # OpenAI GPT Client
│   ├── gemini_client.py       # Google Gemini Client
│   └── mock_client.py         # Mock Client (Testing)
├── services/                   # AI Business Logic
│   ├── __init__.py
│   ├── ai_service.py          # Main AI orchestrator
│   └── client_factory.py      # AI Client Factory
└── schemas/                    # AI Request/Response Models
    ├── __init__.py
    ├── requests.py            # AI request schemas
    └── responses.py           # AI response schemas
```

### **Design Patterns:**
- **Strategy Pattern:** Interchangeable AI clients
- **Factory Pattern:** AI client creation
- **Dependency Injection:** Service layer integration
- **Abstract Base Class:** Common AI interface

---

## 📊 **IMPLEMENTATION PHASES**

### **🔄 PHASE 1: AI Architecture Foundation (Week 1)**

#### **1.1 Base AI Client Interface**
```python
# app/ai/clients/base.py
class BaseAIClient(ABC):
    @abstractmethod
    async def generate_exam(self, request: ExamGenerationRequest) -> ExamGenerationResponse
    
    @abstractmethod
    def is_configured(self) -> bool
    
    @abstractmethod
    def get_client_info(self) -> ClientInfo
```

**Tasks:**
- [ ] Tạo `AIClientType` enum (OpenAI, Gemini, Mock)
- [ ] Define `ExamGenerationRequest` schema
- [ ] Define `ExamGenerationResponse` schema
- [ ] Implement abstract methods
- [ ] Add error handling interfaces

**Deliverables:**
- ✅ Base client interface
- ✅ AI request/response schemas
- ✅ Error handling framework

---

#### **1.2 Mock Client Implementation**
```python
# app/ai/clients/mock_client.py
class MockAIClient(BaseAIClient):
    async def generate_exam(self, request: ExamGenerationRequest):
        # Generate realistic mock questions
        # Support different difficulty levels
        # Return structured response
```

**Tasks:**
- [ ] Implement mock question generation
- [ ] Support multiple question types
- [ ] Add configurable difficulty levels
- [ ] Generate realistic exam metadata

**Deliverables:**
- ✅ Working mock client
- ✅ Test data generation
- ✅ Development-ready AI substitute

---

#### **1.3 AI Client Factory**
```python
# app/ai/services/client_factory.py
class AIClientFactory:
    @classmethod
    def create_client(cls, client_type: AIClientType) -> BaseAIClient
    
    @classmethod
    def get_available_clients(cls) -> List[ClientInfo]
```

**Tasks:**
- [ ] Implement client instantiation logic
- [ ] Add configuration validation
- [ ] Handle client availability checking
- [ ] Add error handling for missing configs

**Deliverables:**
- ✅ Client factory implementation
- ✅ Configuration validation
- ✅ Available clients discovery

---

### **🔄 PHASE 2: Real AI Clients (Week 2)**

#### **2.1 OpenAI Client**
```python
# app/ai/clients/openai_client.py
class OpenAIClient(BaseAIClient):
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model or "gpt-4o-mini"
```

**Tasks:**
- [ ] Setup OpenAI async client
- [ ] Implement exam generation prompts
- [ ] Add response parsing logic
- [ ] Handle API errors & retries
- [ ] Add token counting & cost tracking

**Configuration needed:**
```env
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
```

**Deliverables:**
- ✅ Working OpenAI integration
- ✅ Robust error handling
- ✅ Cost tracking features

---

#### **2.2 Gemini Client**
```python
# app/ai/clients/gemini_client.py
class GeminiClient(BaseAIClient):
    def __init__(self):
        self._llm = None
    
    @property
    def llm(self):
        if self._llm is None:
            self._llm = create_gemini_instance()
        return self._llm
```

**Tasks:**
- [ ] Refactor existing Gemini code
- [ ] Move from utils/ to ai/clients/
- [ ] Implement new interface
- [ ] Add async support
- [ ] Improve prompt engineering

**Migration:**
- Move `app/utils/ai_generator.py` → `app/ai/clients/gemini_client.py`
- Update all imports
- Refactor to new interface

**Deliverables:**
- ✅ Migrated Gemini client
- ✅ Improved prompt engineering
- ✅ Better error handling

---

### **🔄 PHASE 3: AI Service Integration (Week 2-3)**

#### **3.1 Main AI Service**
```python
# app/ai/services/ai_service.py
class AIService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.document_service = DocumentService(db)
    
    async def generate_exam_from_file(
        self,
        file_id: str,
        user_id: str,
        client_type: AIClientType,
        exam_config: ExamConfig
    ) -> ExamGenerationResult
```

**Features:**
- File content retrieval integration
- AI client selection & instantiation
- Exam generation orchestration
- Result validation & formatting
- Error handling & logging

**Tasks:**
- [ ] Implement file-to-exam pipeline
- [ ] Add AI client selection logic
- [ ] Integrate with DocumentService
- [ ] Add comprehensive logging
- [ ] Implement result validation

**Deliverables:**
- ✅ Complete AI service
- ✅ File-to-exam pipeline
- ✅ Multi-client support

---

#### **3.2 API Endpoints**
```python
# New endpoints in app/api/upload.py
@router.get("/ai/clients")
async def get_available_ai_clients()

@router.post("/{file_id}/generate-exam")
async def generate_exam_from_file(
    file_id: str,
    request: ExamFromFileRequest,
    current_user: User = CurrentUser
)
```

**Request Schema:**
```python
class ExamFromFileRequest(BaseModel):
    exam_title: str
    question_count: int = 10
    difficulty: str = "medium"  # easy, medium, hard
    ai_client: AIClientType = AIClientType.GEMINI
    question_types: List[str] = ["multiple_choice"]
```

**Tasks:**
- [ ] Add AI client discovery endpoint
- [ ] Implement exam generation endpoint
- [ ] Add request validation
- [ ] Handle async processing
- [ ] Add comprehensive error responses

**Deliverables:**
- ✅ AI client API endpoints
- ✅ File-to-exam API
- ✅ Comprehensive documentation

---

### **🔄 PHASE 4: Integration & Testing (Week 3)**

#### **4.1 Service Layer Updates**
**Update ExamService:**
```python
# app/services/exam_service.py
class ExamService:
    def __init__(self, db_session: AsyncSession):
        # Remove direct AI generator dependency
        # Use AIService through dependency injection
        self.ai_service = AIService(db_session)
```

**Tasks:**
- [ ] Remove utils/ai_generator imports
- [ ] Update to use new AI service
- [ ] Maintain backward compatibility
- [ ] Update all existing endpoints

**Deliverables:**
- ✅ Updated service layer
- ✅ Clean architecture compliance
- ✅ No breaking changes

---

#### **4.2 Configuration Management**
```python
# app/core/config.py
class Settings:
    # OpenAI Configuration
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    openai_max_tokens: int = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
    
    # AI General Settings
    default_ai_client: str = os.getenv('DEFAULT_AI_CLIENT', 'gemini')
    ai_request_timeout: int = int(os.getenv('AI_REQUEST_TIMEOUT', '60'))
```

**Tasks:**
- [ ] Add OpenAI configuration
- [ ] Add AI general settings
- [ ] Update environment examples
- [ ] Add configuration validation

**Deliverables:**
- ✅ Complete AI configuration
- ✅ Environment documentation
- ✅ Configuration validation

---

#### **4.3 Testing & Documentation**
**Test Coverage:**
- Unit tests for each AI client
- Integration tests for AI service
- End-to-end API tests
- Mock client validation

**Documentation Updates:**
- API documentation with examples
- AI client configuration guide
- Architecture documentation
- Deployment guide updates

**Tasks:**
- [ ] Write comprehensive tests
- [ ] Update API documentation
- [ ] Create configuration guides
- [ ] Add troubleshooting guides

**Deliverables:**
- ✅ Complete test suite
- ✅ Updated documentation
- ✅ Deployment guides

---

## 🚀 **DETAILED IMPLEMENTATION STEPS**

### **Step 1: Project Setup (Day 1)**
```bash
# Create AI module structure
mkdir -p backend/app/ai/{clients,services,schemas}
touch backend/app/ai/__init__.py
touch backend/app/ai/clients/__init__.py
touch backend/app/ai/services/__init__.py  
touch backend/app/ai/schemas/__init__.py
```

### **Step 2: Base Implementation (Day 1-2)**
1. Create `base.py` with abstract client
2. Define request/response schemas
3. Implement mock client
4. Create client factory
5. Add basic tests

### **Step 3: Real Clients (Day 3-7)**
1. Implement OpenAI client
2. Migrate Gemini client
3. Add configuration management
4. Test both clients
5. Add error handling

### **Step 4: Service Integration (Day 8-14)**
1. Create AI service
2. Add API endpoints  
3. Update existing services
4. Integration testing
5. Documentation updates

### **Step 5: Production Ready (Day 15-21)**
1. Performance optimization
2. Comprehensive testing
3. Security review
4. Documentation completion
5. Deployment preparation

---

## 📋 **MIGRATION CHECKLIST**

### **Code Migration:**
- [ ] Move `utils/ai_generator.py` → `ai/clients/gemini_client.py`
- [ ] Update all imports from old location
- [ ] Refactor ExamService to use AIService
- [ ] Remove deprecated code
- [ ] Update __init__.py exports

### **Configuration:**
- [ ] Add OpenAI environment variables
- [ ] Update deployment configurations
- [ ] Add AI client selection settings
- [ ] Update Docker configurations

### **Testing:**
- [ ] Update existing tests
- [ ] Add new AI client tests
- [ ] Add integration tests
- [ ] Update test documentation

---

## 🎯 **SUCCESS CRITERIA**

### **Functional Requirements:**
✅ Users can select AI provider (OpenAI/Gemini)  
✅ Generate exams from uploaded files  
✅ Support multiple question types  
✅ Configurable difficulty levels  
✅ Robust error handling  

### **Technical Requirements:**
✅ Clean architecture compliance  
✅ Async/await throughout  
✅ Comprehensive error handling  
✅ 90%+ test coverage  
✅ Production-ready configuration  

### **Performance Requirements:**
✅ <30s exam generation time  
✅ Support concurrent requests  
✅ Graceful degradation  
✅ Resource usage optimization  

---

## 🚨 **RISKS & MITIGATION**

### **Technical Risks:**
- **API Rate Limits:** Implement retry logic & backoff
- **Token Limits:** Add content chunking for large documents  
- **Network Issues:** Add timeout & retry mechanisms
- **Configuration Errors:** Add validation & clear error messages

### **Business Risks:**
- **AI Costs:** Add usage monitoring & limits
- **Quality Issues:** Add response validation & fallbacks
- **User Experience:** Add loading states & progress indicators

---

## 📚 **RESOURCES & REFERENCES**

### **Documentation:**
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Google Gemini API](https://ai.google.dev/docs)
- [FastAPI Async Patterns](https://fastapi.tiangolo.com/async/)
- [Clean Architecture Principles](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

### **Configuration Examples:**
```env
# .env file for development
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
GEMINI_API_KEY=...
DEFAULT_AI_CLIENT=gemini
```

---

*Last updated: 2025-09-12*
*Next review: After Phase 1 completion*
