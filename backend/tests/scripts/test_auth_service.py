import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import init_database, create_session_maker
from app.services.auth_service import AuthService
from app.schemas.auth_schemas import UserRegisterRequest, UserLoginRequest, ForgotPasswordRequest, ResetPasswordRequest

async def test_auth_flow():
    print("Testing auth service...")

    # setup database
    await init_database()

    session_maker = create_session_maker()

    async with session_maker() as session:
        auth_service = AuthService(session)

        # test register user
        print("\n Testing register user...")
        register_request = UserRegisterRequest(
            email="vominhthinhcute4526@gmail.com",
            password="password123",
            full_name="Thinh Vo",
        )

        try:
            user_response = await auth_service.register_user(register_request)
            print(f"User registered: {user_response}")
        except Exception as e:
            print(f"Error registering user: {e}")
            return 
        
        # test verify email (get token from user)
        print("\n Testing verify email...")
        user = await auth_service.user_repository.get_by_email(register_request.email)
        verification_token = user.email_verification_token
        if not verification_token:
            print("No verification token found")
            return
        
        # test verify email
        try:
            verified = await auth_service.verify_email(verification_token)
            print(f"Email verified: {verified}")
        except Exception as e:
            print(f"Error verifying email: {e}")
            return
            
        # test login user
        print("\n Testing login user...")
        login_request = UserLoginRequest(
            email="vominhthinhcute4526@gmail.com",
            password="password123",
            remember_me=False,
        )

        try:
            login_response = await auth_service.login_user(login_request)
            print(f"Login successful: {login_response}")    
        except Exception as e:
            print(f"Error logging in: {e}")
            return
        
        # test forgot password
        print("\n Testing forgot password...")
        forgot_password_request = ForgotPasswordRequest(
            email="vominhthinhcute4526@gmail.com",
        )
        try:
            forgot_password_response = await auth_service.forgot_password(forgot_password_request.email)
            print(f"Forgot password response: {forgot_password_response}")
        except Exception as e:
            print(f"Error sending forgot password email: {e}")
            return

        # test reset password
        print("\n Testing reset password...")
        try:
            user = await auth_service.user_repository.get_by_email(forgot_password_request.email)
            reset_token = user.password_reset_token
            
            if not reset_token:
                print("No reset token found")
                return
            
            reset_password_request = ResetPasswordRequest(
                token=reset_token,
                new_password="newpassword123",
            )

            reset_password_response = await auth_service.reset_password(
                reset_password_request.token,
                reset_password_request.new_password
            )
            
            if not reset_password_response:
                print("Failed to reset password")
                return
            
            print(f"Reset password response: {reset_password_response}")
        except Exception as e:
            print(f"Error resetting password: {e}")


        # test refresh access token
        print("\n Testing refresh access token...")
        refresh_token = login_response.refresh_token
        try:
            refresh_response = await auth_service.refresh_access_token(refresh_token)
            print(f"Refresh access token response: {refresh_response}")
        except Exception as e:
            print(f"Error refreshing access token: {e}")
            return
        
        # test logout user
        print("\n Testing logout user...")
        try:
            logout_response = await auth_service.logout_user(refresh_token)
            print(f"Logout response: {logout_response}")
        except Exception as e:
            print(f"Error logging out user: {e}")
            return

if __name__ == "__main__":
    asyncio.run(test_auth_flow())