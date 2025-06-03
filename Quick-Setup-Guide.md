# 🚀 Hướng dẫn Setup Nhanh - Exam Hub

Bạn đã có tài khoản GitHub, Vercel, Railway, SonarCloud rồi. Bây giờ làm theo các bước sau:

## Bước 1: Lấy API Tokens (5 phút)

### 1.1 Vercel Token
1. Mở: https://vercel.com/account/tokens
2. Nhấn "Create Token"
3. Token Name: `exam-hub-deploy`
4. Expiration: No expiration
5. Scope: Full Account
6. ✅ **Copy token này** (sẽ cần dùng ngay)

### 1.2 Railway Token  
1. Mở: https://railway.app/account/tokens
2. Nhấn "New Token"
3. Token Name: `exam-hub-deploy`
4. ✅ **Copy token này**

### 1.3 SonarCloud Token
1. Mở: https://sonarcloud.io/account/security
2. Generate new token
3. Token Name: `exam-hub`
4. Type: User Token
5. ✅ **Copy token này**

### 1.4 Snyk Token (Optional - có thể bỏ qua)
1. Mở: https://app.snyk.io/account
2. Copy existing API token
3. ✅ **Copy token này**

## Bước 2: Thêm GitHub Secrets (3 phút)

1. Mở repository GitHub của bạn
2. Vào **Settings** > **Secrets and variables** > **Actions**
3. Nhấn **"New repository secret"** và thêm từng secret:

```
Secret Name: VERCEL_TOKEN
Secret Value: (token Vercel vừa copy)
```

```
Secret Name: RAILWAY_TOKEN  
Secret Value: (token Railway vừa copy)
```

```
Secret Name: SONAR_TOKEN
Secret Value: (token SonarCloud vừa copy)
```

```
Secret Name: GEMINI_API_KEY
Secret Value: (Google Gemini API key của bạn)
```

## Bước 3: Deploy Test (2 phút)

1. Commit và push code:
```bash
git add .
git commit -m "Add free deployment setup"
git push origin main
```

2. Vào GitHub repository > **Actions** tab để xem pipeline chạy

## Bước 4: Setup Projects trong Vercel & Railway

### Vercel Setup:
1. Mở https://vercel.com/dashboard
2. Import Git Repository
3. Chọn repository `Exam-hub`
4. Root Directory: `exam-app`
5. Framework Preset: Create React App
6. Deploy!

### Railway Setup:
1. Mở https://railway.app/dashboard  
2. New Project > Deploy from GitHub repo
3. Chọn repository `Exam-hub`
4. Thêm service: PostgreSQL
5. Cấu hình environment variables

## Bước 5: Lấy Project IDs

### Vercel Project ID:
1. Vào project trên Vercel dashboard
2. Settings > General
3. Copy Project ID & Org ID
4. Thêm vào GitHub secrets:
```
PROJECT_ID: (project id)
ORG_ID: (org id)
```

### Railway Service Name:
1. Vào project trên Railway
2. Copy service name (thường là `web`)
3. Cập nhật trong workflow file nếu cần

## 🎯 Kết quả:

Sau khi hoàn thành:
- ✅ Frontend sẽ deploy tự động tại: `https://exam-hub-[random].vercel.app`
- ✅ Backend sẽ deploy tại: `https://exam-hub-backend.railway.app`
- ✅ Database PostgreSQL tự động tạo trên Railway
- ✅ CI/CD pipeline chạy tự động khi push code

## 🔧 Troubleshooting:

**Nếu có lỗi:**
1. Kiểm tra GitHub Actions logs
2. Đảm bảo tất cả secrets đã được thêm đúng
3. Kiểm tra API keys còn valid không

**Cần hỗ trợ:**
- GitHub Issues của repository
- Railway docs: https://docs.railway.app
- Vercel docs: https://vercel.com/docs 