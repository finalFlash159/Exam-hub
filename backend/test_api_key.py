import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

def test_api_key():
    """Kiểm tra API key và kết nối với Google Generative AI."""
    
    # Lấy API key từ biến môi trường
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Kiểm tra xem API key có tồn tại không
    if not api_key:
        print("\033[91mLỖI: API key không được tìm thấy.\033[0m")
        print("Vui lòng thêm API key vào file .env trong thư mục backend:")
        print("GEMINI_API_KEY=your_api_key_here")
        return False
    
    # Nếu API key chỉ là placeholder
    if api_key == "your_actual_api_key_here":
        print("\033[91mLỖI: API key chưa được cập nhật.\033[0m")
        print("Vui lòng cập nhật API key thực tế trong file .env")
        return False
    
    # Cấu hình API
    print("Đang cấu hình API Gemini...")
    genai.configure(api_key=api_key)
    
    try:
        # Liệt kê models có sẵn
        print("Đang kiểm tra models có sẵn...")
        models = genai.list_models()
        model_names = [model.name for model in models]
        print("\033[92mCác models có sẵn:\033[0m")
        for name in model_names:
            print(f"- {name}")
        
        # Kiểm tra xem Gemini Pro có sẵn không
        if any("gemini-pro" in name for name in model_names):
            print("\033[92mSUCCESS: API key hợp lệ và model Gemini Pro có sẵn!\033[0m")
            return True
        else:
            print("\033[91mLỖI: Model Gemini Pro không có sẵn với API key này.\033[0m")
            return False
    
    except Exception as e:
        print(f"\033[91mLỖI kết nối API: {str(e)}\033[0m")
        return False

if __name__ == "__main__":
    print("===== KIỂM TRA GOOGLE GENERATIVE AI API KEY =====")
    success = test_api_key()
    if success:
        print("\033[92mTất cả đã sẵn sàng! Bạn có thể khởi động server backend.\033[0m")
        sys.exit(0)
    else:
        print("\033[91mKiểm tra thất bại. Vui lòng khắc phục các lỗi trước khi tiếp tục.\033[0m")
        sys.exit(1)
