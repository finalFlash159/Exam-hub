# Exam Hub - AI-Powered Exam Generator

An intelligent exam generation application that creates multiple-choice questions from documents using Google Gemini AI.

## Screenshots

### Main Interface
![Main Interface](images/main_page.png)

### AI Generation Process
![Generation Step 1](images/genai1.png)
![Generation Step 2](images/genai2.png)
![Generation Step 3](images/genai3.png)

## Features

- Upload PDF and DOCX documents
- Automatic question generation using Google Gemini AI
- Multiple-choice questions with explanations
- Timed exam system with instant scoring
- Modern responsive web interface
- FastAPI backend with async support
- LangChain integration for AI operations

## Technology Stack

**Backend:**
- FastAPI (Python web framework)
- LangChain (LLM integration)
- Google Gemini AI
- Pydantic (data validation)

**Frontend:**
- React.js
- Material-UI components
- Context API for state management

**Deployment:**
- Railway (backend hosting)
- Vercel (frontend hosting)

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Google Gemini API key

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/Exam-hub.git
cd Exam-hub
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Create .env file with your API key
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 3. Frontend Setup
```bash
cd exam-app
npm install
```

### 4. Start Development
```bash
# From project root
./start-dev.sh
```

## Development URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:5001
- API Documentation: http://localhost:5001/docs

## Production URLs

- Frontend: https://exam-app-gules.vercel.app
- Backend API: https://exam-hub-production.up.railway.app

## API Endpoints

### Core Endpoints
- `POST /api/upload` - Upload document files
- `POST /api/generate-exam` - Generate questions from uploaded document
- `POST /api/save-exam` - Save generated exam to system

### System Endpoints
- `GET /health` - Health check
- `GET /api/test-connection` - Test Gemini API connectivity
- `GET /docs` - Interactive API documentation

## Project Structure

```
Exam-hub/
├── backend/
│   ├── app.py                 # Main FastAPI application
│   ├── api/                   # API endpoints (modular)
│   │   ├── upload.py          # File upload handling
│   │   ├── exam.py            # Exam generation & saving
│   │   └── health.py          # Health checks
│   ├── core/                  # Core functionality
│   │   ├── config.py          # Configuration management
│   │   └── logging_config.py  # Logging setup
│   ├── models/                # Pydantic models
│   ├── llm_generator.py       # AI question generation
│   └── document_processor.py  # File processing
├── exam-app/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── contexts/          # State management
│   │   └── data/              # Question data storage
│   └── public/                # Static assets
└── start-dev.sh               # Development startup script
```

## Usage Flow

1. Upload a PDF or DOCX document
2. Configure exam settings (title, question count)
3. AI generates multiple-choice questions automatically
4. Review and save exam to system or download JSON
5. Take exam with timer and get instant results

## Environment Variables

### Backend (.env)
```
GEMINI_API_KEY=your_gemini_api_key_here
ENV=development  # Optional, for local development only
```

### Frontend
Development automatically uses localhost:5001
Production uses Railway backend URL by default

## Deployment

Both frontend and backend deploy automatically when pushing to the main branch:

```bash
git add .
git commit -m "your commit message"
git push origin main
```

- Railway auto-deploys backend from GitHub
- Vercel auto-deploys frontend from GitHub

## Testing

### Backend
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend
```bash
cd exam-app
npm test
```

## Troubleshooting

### Common Issues

**Backend fails to start:**
- Verify Python 3.11+ is installed
- Check GEMINI_API_KEY is set in .env file
- Ensure virtual environment is activated

**Frontend build errors:**
- Verify Node.js 18+ is installed
- Try: `rm -rf node_modules package-lock.json && npm install`

**API connection errors:**
- Verify Gemini API key is valid
- Check network connectivity
- Visit `/api/test-connection` endpoint

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

Built with FastAPI, React, and Google Gemini AI
