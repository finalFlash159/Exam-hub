# Exam Hub

Smart exam application with AI-powered automatic exam generation from PDF/DOCX documents.

![Main Page](images/main_page.png)

## 🚀 Live Demo

**🌐 Frontend:** https://exam-app-gules.vercel.app/  
**🔧 Backend API:** https://exam-hub-production.up.railway.app  

*Try the live application now! Upload your PDF/DOCX documents and generate AI-powered exams instantly.*

## Key Features

- **Online Multiple Choice Exams**: User-friendly interface with timer and progress tracking
- **AI-Powered Exam Generation**: Create questions automatically from PDF/DOCX documents
- **Results Management**: View detailed correct/incorrect answers with explanations
- **Multi-language Support**: Vietnamese and English
- **Flexible Customization**: Easy to add new exams

![GenAI Feature 1](images/genai1.png)
![GenAI Feature 2](images/genai2.png)
![GenAI Feature 3](images/genai3.png)

## Quick Setup

### System Requirements
- Node.js 18+
- Python 3.9+
- Google Gemini API Key

### Step 1: Clone repository
```bash
git clone https://github.com/finalFlash159/Exam-hub.git
cd Exam-hub
```

### Step 2: Frontend Setup
```bash
cd exam-app
npm install
npm start
```
Frontend will run at http://localhost:3000

### Step 3: Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Backend will run at http://localhost:5001

### Step 4: Configure API Key
Create `.env` file in `backend` folder:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

## How to Use

### Take Available Exams
1. Open http://localhost:3000
2. Select an exam
3. Start taking the exam
4. View results and explanations

### Generate Exam from Documents
1. Go to "Create Exam" page
2. Upload PDF or DOCX file
3. Fill in exam information
4. Click "Generate Exam"
5. New exam will be added to the system

### Add Manual Exams
1. Create JSON file in `exam-app/src/data/questions/`
2. Question format:
```json
{
  "id": 1,
  "question": "Your question here?",
  "options": [
    {"label": "A", "text": "Option A"},
    {"label": "B", "text": "Option B"},
    {"label": "C", "text": "Option C"},
    {"label": "D", "text": "Option D"}
  ],
  "answer": "B",
  "explanation": {
    "en": "Explanation in English",
    "vi": "Giải thích bằng tiếng Việt"
  }
}
```
3. Update `exam-app/src/data/index.js` file

## Project Structure

```
Exam-hub/
├── exam-app/           # Frontend React
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── data/       # Exam data
│   │   └── styles/     # CSS styles
│   └── public/
├── backend/            # Backend Python Flask
│   ├── app.py         # Main application
│   ├── document_processor.py
│   ├── llm_generator.py
│   └── requirements.txt
└── uploads/           # Document upload folder
```

## Deployment

Project supports automatic CI/CD with GitHub Actions:
- Frontend: Deploy to Vercel
- Backend: Deploy to Railway
- Database: PostgreSQL on Railway

See `Quick-Setup-Guide.md` for details

## Technologies Used

**Frontend:**
- React 18
- Material-UI
- React Router

**Backend:**
- Python Flask
- Google Gemini AI
- PyPDF2, python-docx

**Deployment:**
- Vercel (Frontend)
- Railway (Backend + Database)
- GitHub Actions (CI/CD)

## License

MIT License - see [LICENSE](LICENSE) file
