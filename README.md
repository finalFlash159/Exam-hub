# Exam Hub - AI-Powered Exam Generator

An intelligent exam generation application that creates multiple-choice questions from documents using Google Gemini AI.

## Screenshots

### Main Interface
![Main Interface](images/main_page.png)

### AI Generation Process
![Generation Step 1](images/genai1.png)
![Generation Step 2](images/genai2.png)
![Generation Step 3](images/genai3.png)

## 🚀 Live Demo

**Live Demo:** https://exam-app-gules.vercel.app/
**Backend API:** https://exam-hub-production-c8b2.up.railway.app

## Features

- Upload PDF and DOCX documents
- Automatic question generation using Google Gemini AI
- Multiple-choice questions with bilingual explanations
- Timed exam system with instant scoring
- Modern responsive web interface
- Modular FastAPI architecture
- Optimized startup with lazy loading

## Tech Stack

- **Frontend:** React.js + Material-UI + Context API
- **Backend:** FastAPI + LangChain + Google Gemini AI
- **Document Processing:** PyMuPDF, python-docx
- **Deployment:** Vercel (frontend) + Railway (backend)
- **Development:** Hot reload, structured logging

## 🛠️ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/Exam-hub.git
cd Exam-hub

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Environment configuration
cp ../.env.example .env
# Edit .env with your GEMINI_API_KEY

# 4. Frontend setup  
cd ../exam-app
npm install

# 5. Start development servers
cd ..
./start-dev.sh
```

### Development URLs
- Frontend: http://localhost:3000
- Backend: http://localhost:5001
- API Docs: http://localhost:5001/docs
- Health Check: http://localhost:5001/health

## API Endpoints

```
GET  /                   # API information
GET  /health            # Health check
POST /api/upload        # Upload document
POST /api/generate-exam # Generate questions
POST /api/save-exam     # Save exam to system
GET  /docs              # Interactive API documentation
GET  /redoc             # Alternative API documentation
```

## Usage Flow

1. **Upload Document**: Upload PDF or DOCX file
2. **Configure Exam**: Set title and question count (1-20)
3. **AI Generation**: Google Gemini processes content and creates questions
4. **Review & Save**: Review generated questions and save to system
5. **Take Exam**: Use timer-based exam interface with instant scoring

## Project Structure

```
backend/
├── app.py                  # Main FastAPI application
├── api/                    # Modular API endpoints
│   ├── exam.py            # Exam generation & saving
│   ├── upload.py          # File upload handling
│   └── health.py          # Health checks
├── core/                   # Core configuration
│   ├── config.py          # Settings & Gemini config
│   └── logging_config.py  # Structured logging
├── models/                 # Pydantic data models
├── llm_generator.py        # AI question generation
└── document_processor.py   # Document text extraction

exam-app/
├── src/
│   ├── components/         # React components
│   ├── contexts/          # State management
│   ├── hooks/             # Custom React hooks
│   ├── data/              # Static data & questions
│   └── constants/         # Application constants
└── public/                # Static assets
```

## Configuration

### Backend Environment (.env)
```env
# Required
GEMINI_API_KEY=your_google_gemini_api_key_here

# Optional (defaults provided)
ENV=development
PORT=5001
```

### Frontend Configuration
- **Development**: Automatically connects to localhost:5001
- **Production**: Connects to Railway deployment

## 🚀 Deployment

### Railway (Backend)
1. Connect GitHub repository to Railway
2. Set environment variable: `GEMINI_API_KEY`
3. Railway will auto-deploy from main branch

### Vercel (Frontend)
1. Connect GitHub repository to Vercel
2. Build settings are automatically configured
3. Deploys automatically on push to main

## Testing

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd exam-app
npm test
```

## Development Features

- **Lazy Loading**: Faster startup with background Gemini initialization
- **Structured Logging**: Enhanced logs with proper levels
- **Error Handling**: Graceful degradation when API key missing
- **Type Safety**: Full TypeScript/Python typing
- **Hot Reload**: Development servers with auto-restart

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Troubleshooting

### Common Issues

**Backend not starting**: Check if GEMINI_API_KEY is set in environment variables
**File upload fails**: Ensure `backend/uploads/` directory exists
**Questions not generating**: Verify document has sufficient text content (>100 characters)

### Getting Help

- Check [Issues](https://github.com/yourusername/Exam-hub/issues) for common problems
- Review API documentation at `/docs` endpoint
- Check application logs for detailed error messages
