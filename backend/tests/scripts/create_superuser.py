# Tạo file: backend/create_superuser.py
"""
CLI Script to create a superuser (admin) account
Usage: python create_superuser.py <email> <password> <full_name>
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import get_db_session
from app.models.user import User, UserRole
from app.utils.security import get_password_hash
from sqlalchemy import select

async def create_superuser(email: str, password: str, full_name: str):
    """Create superuser with admin role"""
    
    async for session in get_db_session():
        try:
            print(f"🚀 Creating superuser: {email}")
            
            # Check if user exists
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"❌ User {email} already exists!")
                return False
            
            # Hash password
            hashed_password = get_password_hash(password)
            
            # Create admin user
            user = User(
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                role=UserRole.ADMIN,  # 👑 ADMIN ROLE
                is_active=True,
                email_verified=True,  # ✅ Auto verified
                email_verification_token=None  # No need for verification
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print("✅ SUPERUSER CREATED SUCCESSFULLY!")
            print(f"📧 Email: {user.email}")
            print(f"👤 Name: {user.full_name}")
            print(f"👑 Role: {user.role.value}")
            print(f"✅ Verified: {user.email_verified}")
            print(f"🆔 ID: {user.id}")
            print("\n🎉 Ready to login with admin privileges!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating superuser: {e}")
            await session.rollback()
            return False

def main():
    """Main CLI function"""
    if len(sys.argv) != 4:
        print("❌ Usage: python create_superuser.py <email> <password> <full_name>")
        print("\n📝 Example:")
        print('python create_superuser.py admin@example.com admin123 "Admin User"')
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    full_name = sys.argv[3]
    
    # Validate inputs
    if len(password) < 8:
        print("❌ Password must be at least 8 characters!")
        sys.exit(1)
    
    if "@" not in email:
        print("❌ Invalid email format!")
        sys.exit(1)
    
    # Create superuser
    success = asyncio.run(create_superuser(email, password, full_name))
    
    if success:
        print("\n🔐 LOGIN CREDENTIALS:")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print("\n📖 Next steps:")
        print("1. Go to http://localhost:8000/docs")
        print("2. Use POST /auth/login")
        print("3. Copy access_token and click Authorize")
        print("4. Test admin endpoints! 🚀")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()