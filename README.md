# Exam Hub

A flexible and customizable exam application platform for various subjects and tools. Build, manage, and deliver interactive examinations with support for multiple question types, subject-specific testing, and extensible modules for different educational needs.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Creating Custom Exams](#creating-custom-exams)
  - [JSON File Structure](#json-file-structure)
  - [Question Format](#question-format)
  - [Adding Your Exam to the Application](#adding-your-exam-to-the-application)
- [Document-to-Exam Conversion](#document-to-exam-conversion)
  - [Supported Document Types](#supported-document-types)
  - [Backend Setup](#backend-setup)
  - [Using the Exam Generator](#using-the-exam-generator)
- [Customization Options](#customization-options)
- [Contributing](#contributing)
- [License](#license)

## Overview

Exam Hub is a React-based application designed to deliver customizable practice tests and exams across various subjects, technologies, and tools. Whether you need to create a programming language quiz, a certification practice exam, or an educational assessment, Exam Hub provides a flexible framework to build and deploy your tests.

## Features

- **Customizable Exam Creation**: Define your own exams with custom questions and answers
- **Multiple Question Types**: Support for multiple-choice questions with detailed explanations
- **Interactive UI**: User-friendly interface with progress tracking and timer
- **Flexible Architecture**: Easy to extend with new question types and exam formats
- **Results Analysis**: Detailed results with correct/incorrect answers and explanations
- **Multilingual Support**: Support for multiple languages in question explanations
- **AI-Powered Exam Generation**: Create exams from PDF or DOCX documents automatically

## Getting Started

### Prerequisites

- Node.js (14.x or higher)
- npm (6.x or higher) or yarn
- Python (3.8 or higher) for the backend document processing

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/exam-hub.git
cd exam-hub
```

2. Install frontend dependencies:
```bash
cd exam-app
npm install
```

3. Install backend dependencies:
```bash
cd ../backend
pip install -r requirements.txt
```

4. Set up the environment variables:
```bash
cp .env.example .env
# Edit the .env file and add your Gemini API key
```

### Running the Application

1. Start the backend server:
```bash
cd backend
python app.py
```

2. In a separate terminal, start the frontend:
```bash
cd exam-app
npm start
```

The application will be available at [http://localhost:3000](http://localhost:3000).

## Creating Custom Exams

You can create custom exams by defining question sets in JSON files. Follow these guidelines to create compatible exam files.

### JSON File Structure

Create a JSON file with an array of question objects. Place your file in the `/src/data/questions/` directory.

### Question Format

Each question object should have the following structure:

```json
{
  "id": 1,
  "question": "What is your question text?",
  "options": [
    { "label": "A", "text": "First option" },
    { "label": "B", "text": "Second option" },
    { "label": "C", "text": "Third option" },
    { "label": "D", "text": "Fourth option" }
  ],
  "answer": "B",
  "explanation": {
    "en": "Explanation in English",
    "vi": "Explanation in Vietnamese (optional)"
  }
}
```

#### Fields Explained:

- **id**: Unique identifier for the question (number)
- **question**: The question text (string)
- **options**: Array of answer options, each with:
  - **label**: Option identifier (typically A, B, C, D)
  - **text**: Option text
- **answer**: Correct option label (must match one of the option labels)
- **explanation**: Object containing explanations in different languages
  - At minimum, include "en" for English

### Example Question

```json
{
  "id": 1,
  "question": "Which programming language is known for its use in data science?",
  "options": [
    { "label": "A", "text": "Java" },
    { "label": "B", "text": "C++" },
    { "label": "C", "text": "Python" },
    { "label": "D", "text": "JavaScript" }
  ],
  "answer": "C",
  "explanation": {
    "en": "Python has become the leading language for data science due to its rich ecosystem of libraries like NumPy, pandas, and scikit-learn.",
    "vi": "Python đã trở thành ngôn ngữ hàng đầu cho khoa học dữ liệu nhờ hệ sinh thái phong phú của các thư viện như NumPy, pandas và scikit-learn."
  }
}
```

### Full Example File

Create a file like `my-exam.json` with this structure:

```json
[
  {
    "id": 1,
    "question": "Question 1 text",
    "options": [
      { "label": "A", "text": "Option A" },
      { "label": "B", "text": "Option B" },
      { "label": "C", "text": "Option C" },
      { "label": "D", "text": "Option D" }
    ],
    "answer": "A",
    "explanation": {
      "en": "Explanation for question 1"
    }
  },
  {
    "id": 2,
    "question": "Question 2 text",
    "options": [
      { "label": "A", "text": "Option A" },
      { "label": "B", "text": "Option B" },
      { "label": "C", "text": "Option C" },
      { "label": "D", "text": "Option D" }
    ],
    "answer": "B",
    "explanation": {
      "en": "Explanation for question 2",
      "vi": "Vietnamese explanation for question 2"
    }
  }
]
```

### Adding Your Exam to the Application

1. Place your JSON file in the `/src/data/questions/` directory
2. Import your file in `/src/data/index.js`:

```javascript
import myExamQuestions from './questions/my-exam.json';
```

3. Add your exam to the `examData` object:

```javascript
export const examData = {
  // ...existing exams
  "my-exam": {
    title: "My Custom Exam Title",
    questions: myExamQuestions
  }
};
```

## Document-to-Exam Conversion

Exam Hub includes a powerful feature to generate exams automatically from PDF and DOCX documents using Google's Gemini AI.

### Supported Document Types

- **PDF** (.pdf files)
- **Microsoft Word** (.docx files)

### Backend Setup

To use the document processing features:

1. Get a Gemini API key from Google AI Studio (https://makersuite.google.com/)
2. Add your API key to the `.env` file:
```
GEMINI_API_KEY=your-api-key-here
```
3. Ensure the Python backend is running (`python app.py`)

### Using the Exam Generator

1. Navigate to the "Create Exam" page
2. Upload your document (PDF or DOCX)
3. Configure your exam settings:
   - Set the title for your exam
   - Choose the number of questions to generate
4. Click "Generate Exam Questions"
5. Review the generated questions
6. Save the exam to add it to your collection

The AI will analyze your document and generate relevant multiple-choice questions based on the content. The quality of the generated questions depends on the clarity and structure of your document.

## Customization Options

You can customize various aspects of the exam:

- **Time Limit**: Modify the `TOTAL_TIME` constant in `/src/components/ExamApp.jsx`
- **Passing Score**: Adjust the `PASSING_SCORE` constant
- **UI Themes**: Modify the Material UI theme in the application
- **Languages**: Add additional language support in the explanation objects

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
