"""
Test file for UserRepository and RefreshTokenRepository
"""

# Python Standard Library
import asyncio
import sys
import os
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional

# Add Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession

# Database connection
from app.database.connection import init_database, get_db_session, check_database_connection, async_session_maker, create_session_maker

# Repository classes
from app.repositories.user_repository import UserRepository, RefreshTokenRepository


# Model classes
from app.models.user import User, UserRole
from app.models.auth import RefreshToken

# Security utilities
from app.utils.security import get_password_hash, verify_password

# Email service
from app.services.email_service import EmailService


async def setup_test():
    print("🔧 Setting up test environment...")
    
    # init database
    print("📊 Initializing database...")
    await init_database()

    # test connection
    print("🔌 Testing database connection...")
    try:
        result = await check_database_connection()
        if result:
            print("✅ Database connection: SUCCESS")
            return True
        else:
            print("❌ Database connection: FAILED")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

async def test_create_user():
    print("\nTesting create_user_with_verification...")
    
    email = "test@test.com"
    password = "test"
    full_name = "Test User"
    verification_token = secrets.token_urlsafe(32)
    hashed_password = get_password_hash(password)

    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Full Name: {full_name}")
    print(f"Verification Token: {verification_token}")
    print(f"Hashed Password: {hashed_password}")

    try:
        if async_session_maker is None:
            print("Creating session maker...")
            session_maker = create_session_maker()
        else:
            session_maker = async_session_maker()
        
        # create repository
        async with session_maker() as session:
            user_repository = UserRepository(session)
            user = await user_repository.create_user_with_verification(
                email, hashed_password, full_name, verification_token
            )
            
            print(f"User created: {user.email}, ID: {user.id}")
            return True

    except Exception as e:
        print(f"Error creating session maker: {e}")
        return False
    

async def test_get_by_email():
    print("\nTesting get_by_email...")
    try:
        if async_session_maker is None:
            print("Creating session maker...")
            session_maker = create_session_maker()
        else:
            session_maker = async_session_maker()
        
        # create repository
        async with session_maker() as session:
            user_repository = UserRepository(session)

            # test existing email
            print("Testing existing email...")
            user = await user_repository.get_by_email("test@test.com")
            if user:
                print(f"User found: {user.email}, ID: {user.id}")
            else:
                print("User not found")
            
            # test non-existing email
            print("Testing non-existing email...")
            user1 = await user_repository.get_by_email("nonexistent@test.com")
            if user1 is None:
                print("Correctly returned None for non-existing email")
            else:
                print("Incorrectly returned a user for non-existing email")
                return True
            
    except Exception as e:
        print(f"Error creating session maker: {e}")
        return False
    

async def test_verify_email():
    print("\nTesting verify_email...")
    try:
        if async_session_maker is None:
            print("Creating session maker...")
            session_maker = create_session_maker()
        else:
            session_maker = async_session_maker()
        
        # create repository
        async with session_maker() as session:
            user_repository = UserRepository(session)
            user = await user_repository.get_by_email("test@test.com")
            if user:
                print(f"User found: {user.email}, ID: {user.id}")
            else:
                print("User not found")

            verified_user = await user_repository.verify_email(user.email_verification_token)
            if verified_user:
                print(f"User verified: {verified_user.email}, ID: {verified_user.id}")
            else:
                print("User not verified")

            return True

    except Exception as e:
        print(f"Error creating session maker: {e}")
        return False

async def test_set_password_reset_token():
    print("\nTesting set_password_reset_token...")

    try: 
        session_maker = create_session_maker()
        async with session_maker() as session:
            user_repository = UserRepository(session)

            user = await user_repository.get_by_email("test@test.com")
            if not user:
                print("User not found")
                return False
            
            # set password reset token
            reset_token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

            # set reset token
            success = await user_repository.set_password_reset_token(
                user, reset_token, expires_at
            )

            if success:
                print(f"Password reset token set for user: {user.email}")
                print(f"Expires at: {expires_at}")
                return True
            else:
                print("Failed to set password reset token")
                return False
                            
    except Exception as e:
        print(f"test_set_password_reset_token: FAILED - {e}")
        return False
    
async def test_reset_password():
    print("\nTesting reset_password...")
    try:
        session_maker = create_session_maker()
        async with session_maker() as session:
            user_repository = UserRepository(session)
            
            user = await user_repository.get_by_email("test@test.com")
            if not user:
                print("User not found")
                return False
            
            if not user.password_reset_token:
                print("No password reset token found")
                return False
            
            # reset password
            new_password = "new_password"
            hashed_password = get_password_hash(new_password)
            success = await user_repository.reset_password(user.password_reset_token, hashed_password)
            
            if success:
                print(f"Password reset for user: {user.email}")
                return True
            else:
                print("Failed to reset password")
                return False
            
    except Exception as e:
        print(f"test_reset_password: FAILED - {e}")
        return False
    
# global variable for refresh token
test_refresh_token = None

async def test_create_refresh_token():
    print("\nTesting create_refresh_token...")
    global test_refresh_token
    
    try:
        session_maker = create_session_maker()
        async with session_maker() as session:
            # 1. Lấy user đã tạo
            user_repository = UserRepository(session)
            user = await user_repository.get_by_email("test@test.com")
            if not user:
                print("User not found for test")
                return False
            
            # 2. Tạo refresh token data
            refresh_token_repository = RefreshTokenRepository(session)
            token = secrets.token_urlsafe(64)  # Refresh token dài hơn
            expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # 7 ngày
            device_info = "iPhone 15 Pro"
            ip_address = "192.168.1.100"
            user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)"
            
            # 3. Tạo refresh token
            refresh_token = await refresh_token_repository.create_refresh_token(
                user_id=user.id,
                token=token,
                expires_at=expires_at,
                device_info=device_info,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # 4. Verify results
            if refresh_token:
                print(f"✅ Refresh token created: {refresh_token.token[:10]}...")
                print(f"✅ User ID: {refresh_token.user_id}")
                print(f"✅ Expires at: {refresh_token.expires_at}")
                print(f"✅ Device: {refresh_token.device_info}")
                test_refresh_token = refresh_token.token
                return True
            else:
                print("Failed to create refresh token")
                return False
                
    except Exception as e:
        print(f"Test_create_refresh_token: FAILED - {e}")
        return False

async def test_get_valid_token():
    print("\nTesting get_valid_token...")
    try:
        session_maker = create_session_maker()
        async with session_maker() as session:
            refresh_token_repository = RefreshTokenRepository(session)
            refresh_token = await refresh_token_repository.get_valid_token(test_refresh_token)
            
            if refresh_token:
                print(f"✅ Valid refresh token found: {refresh_token.token[:10]}...")
                print(f"✅ User ID: {refresh_token.user_id}")
                print(f"✅ Expires at: {refresh_token.expires_at}")
                print(f"✅ Device: {refresh_token.device_info}")
                return True
            else:
                print("No valid refresh token found")
                return False
                
    except Exception as e:
        print(f"Test_get_valid_token: FAILED - {e}")
        return False

async def test_revoke_token():
    print("\n🧪 Testing revoke_token...")
    global test_refresh_token
    
    if not test_refresh_token:
        print("❌ No refresh token to revoke")
        return False
    
    try:
        session_maker = create_session_maker()
        async with session_maker() as session:
            refresh_token_repository = RefreshTokenRepository(session)
            
            # 1. Revoke token
            success = await refresh_token_repository.revoke_token(test_refresh_token)
            
            if not success:
                print("❌ Failed to revoke token")
                return False
            
            # 2. Verify token is revoked
            revoked_token = await refresh_token_repository.get_valid_token(test_refresh_token)
            
            if revoked_token is None:
                print("✅ Token successfully revoked")
                return True
            else:
                print("❌ Token still valid after revoke")
                return False
                
    except Exception as e:
        print(f"❌ test_revoke_token: FAILED - {e}")
        return False    

async def test_revoke_all_user_tokens():
    print("\n🧪 Testing revoke_all_user_tokens...")
    
    try:
        session_maker = create_session_maker()
        async with session_maker() as session:
            user_repository = UserRepository(session)
            refresh_token_repository = RefreshTokenRepository(session)
            
            # 1. Lấy user
            user = await user_repository.get_by_email("test@test.com")
            if not user:
                print("❌ User not found")
                return False
            
            # 2. Tạo thêm vài refresh tokens để test
            token1 = secrets.token_urlsafe(64)
            token2 = secrets.token_urlsafe(64)
            expires_at = datetime.now(timezone.utc) + timedelta(days=7)
            
            await refresh_token_repository.create_refresh_token(
                user.id, token1, expires_at, "Device 1"
            )
            await refresh_token_repository.create_refresh_token(
                user.id, token2, expires_at, "Device 2"
            )
            
            # 3. Revoke all tokens
            revoked_count = await refresh_token_repository.revoke_all_user_tokens(user.id)
            
            print(f"✅ Revoked {revoked_count} tokens")
            
            # 4. Verify all tokens are revoked
            valid_token1 = await refresh_token_repository.get_valid_token(token1)
            valid_token2 = await refresh_token_repository.get_valid_token(token2)
            
            if valid_token1 is None and valid_token2 is None:
                print("✅ All tokens successfully revoked")
                return True
            else:
                print("❌ Some tokens still valid")
                return False
                
    except Exception as e:
        print(f"❌ test_revoke_all_user_tokens: FAILED - {e}")
        return False

async def main():
    print("Starting User Repository Tests...")
    
    # setup env
    success = await setup_test()
    if not success:
        print("Failed to setup test environment")
        return
    
    # test 
    await test_create_user()
    await test_get_by_email()
    await test_verify_email()
    await test_set_password_reset_token()
    await test_reset_password()
    await test_create_refresh_token()
    await test_get_valid_token()
    await test_revoke_token()
    await test_revoke_all_user_tokens()
    print("All tests completed successfully")

if __name__ == "__main__":
    asyncio.run(main())