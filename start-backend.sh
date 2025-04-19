#!/bin/bash

echo "Starting Exam Hub backend server..."

# Kiểm tra môi trường ảo
if [ ! -d "venv" ]; then
    echo "Tạo môi trường ảo..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r backend/requirements.txt
else
    source venv/bin/activate
fi

# Chạy ứng dụng Flask với port khác (5001)
cd backend
python -c "
import os
from app import app
from document_processor import DocumentProcessor
from llm_generator import ExamGenerator

if __name__ == '__main__':
    print('Khởi động server trên cổng 5001...')
    app.run(debug=True, host='0.0.0.0', port=5001)
"
