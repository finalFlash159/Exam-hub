# 📚 ALEMBIC COMMANDS REFERENCE

## 🎯 ALEMBIC LÀ GÌ?
- **Database migration tool** cho SQLAlchemy
- **Track changes** của database schema qua Git
- **Collaborate** với team một cách professional
- **Deploy** database changes tự động

---

## 🔧 ALEMBIC SETUP

### 1. Install Dependencies
```bash
pip install alembic>=1.12.0
pip install "python-jose[cryptography]>=3.3.0"
pip install "passlib[bcrypt]>=1.7.4"
```

### 2. Initialize Alembic
```bash
# Tạo folder alembic/ và file config
alembic init alembic
```

### 3. Configure `alembic.ini`
```ini
# Thay dòng:
sqlalchemy.url = driver://user:pass@localhost/dbname

# Bằng:
sqlalchemy.url = sqlite:///./exam_hub.db
```

### 4. Configure `alembic/env.py`
```python
# Thay dòng 21:
target_metadata = None

# Bằng:
from app.models.base import Base
from app.models.exam import Exam, Question, ExamAttempt  
from app.models.user import User

target_metadata = Base.metadata
```

---

## 🚀 ALEMBIC COMMANDS CHÍNH

### 📝 1. TẠO MIGRATION FILE
```bash
# Tạo migration từ model changes
alembic revision --autogenerate -m "Mô tả thay đổi"

# Ví dụ:
alembic revision --autogenerate -m "Add users table"
alembic revision --autogenerate -m "Add email index to users"
alembic revision --autogenerate -m "Add posts table"
alembic revision --autogenerate -m "Remove old field from users"
```

### ⬆️ 2. APPLY MIGRATIONS (Chạy lệnh tạo table)
```bash
# Apply tất cả migrations chưa chạy
alembic upgrade head

# Apply từng migration một
alembic upgrade +1

# Apply đến revision cụ thể
alembic upgrade 79d948d5a30f
```

### ⬇️ 3. ROLLBACK MIGRATIONS
```bash
# Rollback 1 migration
alembic downgrade -1

# Rollback 2 migrations
alembic downgrade -2

# Rollback về revision cụ thể  
alembic downgrade 79d948d5a30f

# Rollback tất cả (DROP all tables) - NGUY HIỂM!
alembic downgrade base
```

### 🔍 4. CHECK STATUS
```bash
# Xem current revision
alembic current

# Xem lịch sử migrations
alembic history

# Xem lịch sử chi tiết
alembic history --verbose

# Xem pending migrations  
alembic show head

# Xem SQL sẽ được execute (không chạy thật)
alembic upgrade head --sql
```

---

## 🎯 WORKFLOW THỰC TẾ

### 🔄 KHI THÊM/SỬA MODEL

**Bước 1:** Sửa model (ví dụ: thêm field)
```python
# app/models/user.py
class User(BaseModel):
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str] = mapped_column(String(20))  # ← THÊM MỚI
```

**Bước 2:** Tạo migration
```bash
alembic revision --autogenerate -m "Add phone field to users"
```

**Bước 3:** Review migration file
```bash
# Xem file được tạo
ls alembic/versions/
cat alembic/versions/abc123_add_phone_field_to_users.py
```

**Bước 4:** Apply migration
```bash
alembic upgrade head
```

**Bước 5:** Commit to Git
```bash
git add alembic/versions/abc123_add_phone_field_to_users.py
git commit -m "Add phone field to users table"
git push
```

---

## 👥 WORKFLOW TRONG TEAM

### 👤 Developer A thêm feature:
```bash
# 1. Sửa model trong app/models/
# 2. Tạo migration
alembic revision --autogenerate -m "Add feature X"

# 3. Test locally
alembic upgrade head

# 4. Commit & push
git add .
git commit -m "Add feature X with database migration"
git push origin main
```

### 👤 Developer B pull về:
```bash
# Pull latest code
git pull origin main

# Sync database automatically
alembic upgrade head

# Ready to work!
```

### 🚀 Production deployment:
```bash
# On server
git pull origin main
alembic upgrade head    # Apply database changes
python app.py           # Start server
```

---

## 🆘 EMERGENCY COMMANDS

### Reset Database hoàn toàn:
```bash
# ⚠️ NGUY HIỂM - Xóa tất cả data
rm exam_hub.db                    # Xóa database file
alembic upgrade head              # Tạo lại từ migrations
```

### Fix lỗi migration conflict:
```bash
# Nếu có conflict migration
alembic merge -m "Merge conflicting migrations"
alembic upgrade head
```

### Xem SQL không execute:
```bash
# Debug SQL commands
alembic upgrade head --sql > migration.sql
cat migration.sql
```

---

## 📋 QUICK REFERENCE

### 🔄 Thường dùng hàng ngày:
```bash
alembic revision --autogenerate -m "Mô tả"  # Tạo migration
alembic upgrade head                        # Apply migrations
alembic current                            # Check status
alembic history                            # Xem lịch sử
```

### 🔍 Debug & troubleshoot:
```bash
alembic history --verbose          # Chi tiết migrations
alembic show head                  # Latest migration info  
alembic upgrade head --sql         # Xem SQL sẽ chạy
alembic downgrade -1               # Rollback 1 step
```

### ⚠️ Nguy hiểm (cẩn thận):
```bash
alembic downgrade base             # Xóa tất cả tables
rm exam_hub.db                     # Xóa database file
```

---

## 🎯 BEST PRACTICES

### ✅ DOs:
- **Luôn review** migration file trước khi apply
- **Test locally** trước khi commit
- **Descriptive messages** cho migration names
- **Backup database** trước khi deploy production
- **Team sync** trước khi merge migration conflicts

### ❌ DON'Ts:
- **Đừng edit** migration files đã committed
- **Đừng rollback** trên production khi có data
- **Đừng xóa** migration files
- **Đừng skip** migrations khi deploy
- **Đừng commit** database files (.db)

---

## 🔗 USEFUL COMMANDS KHÁC

### Project setup:
```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup database
alembic upgrade head
```

### Development workflow:
```bash
# Start development server
python app.py

# Test APIs
curl http://localhost:5001/health

# Check database
sqlite3 exam_hub.db ".tables"
```

---

## 📞 GẤP - CẦN HELP

### Nếu gặp lỗi migration:
1. **Check current status:** `alembic current`
2. **Check history:** `alembic history`
3. **Try rollback:** `alembic downgrade -1`
4. **Reset if needed:** `rm exam_hub.db && alembic upgrade head`

### Contact team lead nếu:
- Migration conflicts không resolve được
- Data bị mất trên production
- Database corruption
- Cần rollback production

---

*📝 File này được tạo để reference nhanh. Update khi có changes mới!* 