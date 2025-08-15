import logging
from typing import Dict, Any, Optional
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Brevo email service for transactional emails"""
    
    def __init__(self):
        """Initialize Brevo API client"""
        # Configure Brevo API
        self.configuration = sib_api_v3_sdk.Configuration()
        self.configuration.api_key['api-key'] = settings.brevo_api_key
        
        # Create API instance
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(self.configuration)
        )
        
        logger.info("EmailService initialized with Brevo API")
    
    async def send_verification_email(
        self, 
        email: str, 
        verification_token: str, 
        user_name: str = None
    ) -> bool:
        """Send email verification email"""
        try:
            # Create verification link
            verification_link = self._create_verification_link(verification_token)
            
            # Prepare context
            user_display_name = user_name or email.split('@')[0]
            
            # Create email content
            subject = f"🔐 Verify your {settings.from_name} account"
            html_content = self._create_verification_html(
                user_name=user_display_name,
                verification_link=verification_link
            )
            text_content = self._create_verification_text(
                user_name=user_display_name,
                verification_link=verification_link
            )
            
            # Send email
            return self._send_transactional_email(
                to_email=email,
                to_name=user_display_name,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {e}")
            return False
    
    async def send_password_reset_email(
        self, 
        email: str, 
        reset_token: str, 
        user_name: str = None
    ) -> bool:
        """Send password reset email"""
        try:
            # Create reset link
            reset_link = self._create_reset_link(reset_token)
            
            # Prepare context
            user_display_name = user_name or email.split('@')[0]
            
            # Create email content
            subject = f"🔐 Reset your {settings.from_name} password"
            html_content = self._create_reset_html(
                user_name=user_display_name,
                reset_link=reset_link
            )
            text_content = self._create_reset_text(
                user_name=user_display_name,
                reset_link=reset_link
            )
            
            # Send email
            return self._send_transactional_email(
                to_email=email,
                to_name=user_display_name,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")
            return False
    
    def _create_verification_link(self, token: str) -> str:
        """Create email verification link"""
        return f"{settings.frontend_url}/verify-email?token={token}"
    
    def _create_reset_link(self, token: str) -> str:
        """Create password reset link"""
        return f"{settings.frontend_url}/reset-password?token={token}"
    
    def _send_transactional_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None,
        to_name: str = None
    ) -> bool:
        """Send email using Brevo API - VERIFIED WORKING PATTERN"""
        try:
            # Create email object (exact pattern from successful test)
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                sender={
                    "email": settings.from_email,
                    "name": settings.from_name
                },
                to=[{
                    "email": to_email,
                    "name": to_name or to_email.split('@')[0]
                }],
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            # Send email
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            
            logger.info(f"Email sent successfully to {to_email}. Message ID: {api_response.message_id}")
            return True
            
        except ApiException as e:
            logger.error(f"Brevo API error when sending email to {to_email}: Status {e.status}, Reason: {e.reason}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when sending email to {to_email}: {e}")
            return False
    
    def _create_verification_html(self, user_name: str, verification_link: str) -> str:
        """Create verification email HTML content"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Verification - {settings.from_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 30px 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 15px 30px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; background-color: #f1f1f1; border-radius: 0 0 8px 8px; }}
                .link {{ background-color: #e9ecef; padding: 10px; border-radius: 3px; font-family: monospace; word-break: break-all; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 Welcome to {settings.from_name}!</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    <p>Thank you for signing up for <strong>{settings.from_name}</strong>! To complete your registration and start using our platform, please verify your email address.</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_link}" class="button">✅ Verify Email Address</a>
                    </div>
                    
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p class="link">{verification_link}</p>
                    
                    <p><strong>🔒 Security Notice:</strong></p>
                    <ul>
                        <li>This verification link will expire in 24 hours</li>
                        <li>If you didn't create an account, you can safely ignore this email</li>
                        <li>Your account won't be activated until you click the verification link</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>Best regards,<br><strong>The {settings.from_name} Team</strong></p>
                    <p>Need help? Contact us at <a href="mailto:{settings.from_email}">{settings.from_email}</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_verification_text(self, user_name: str, verification_link: str) -> str:
        """Create verification email text content"""
        return f"""
        🎓 Welcome to {settings.from_name}!

        Hi {user_name},

        Thank you for signing up for {settings.from_name}! To complete your registration, please verify your email address.

        Verification link: {verification_link}

        🔒 Security Notice:
        - This verification link will expire in 24 hours
        - If you didn't create an account, you can safely ignore this email

        Best regards,
        The {settings.from_name} Team

        Need help? Contact us at {settings.from_email}
        """
    
    def _create_reset_html(self, user_name: str, reset_link: str) -> str:
        """Create password reset email HTML content"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset - {settings.from_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 30px 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 15px 30px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; background-color: #f1f1f1; border-radius: 0 0 8px 8px; }}
                .link {{ background-color: #e9ecef; padding: 10px; border-radius: 3px; font-family: monospace; word-break: break-all; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    <p>We received a request to reset your password for your <strong>{settings.from_name}</strong> account.</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">🔑 Reset My Password</a>
                    </div>
                    
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p class="link">{reset_link}</p>
                    
                    <div class="warning">
                        <p><strong>⚠️ Security Notice:</strong></p>
                        <ul>
                            <li>This reset link will expire in 24 hours</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                            <li>Your password won't change until you click the link above</li>
                            <li>Only the most recent reset link will work</li>
                        </ul>
                    </div>
                    
                    <p>For security reasons, if you continue to receive these emails without requesting them, please contact our support team immediately.</p>
                </div>
                <div class="footer">
                    <p>Best regards,<br><strong>The {settings.from_name} Security Team</strong></p>
                    <p>🚨 Security concern? Contact us at <a href="mailto:{settings.from_email}">{settings.from_email}</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_reset_text(self, user_name: str, reset_link: str) -> str:
        """Create password reset email text content"""
        return f"""
        🔐 Password Reset Request

        Hi {user_name},

        We received a request to reset your password for your {settings.from_name} account.

        Reset link: {reset_link}

        ⚠️ Security Notice:
        - This reset link will expire in 24 hours
        - If you didn't request this reset, please ignore this email
        - Your password won't change until you click the link above

        For security reasons, if you continue to receive these emails without requesting them, please contact our support team immediately.

        Best regards,
        The {settings.from_name} Security Team

        🚨 Security concern? Contact us at {settings.from_email}
        """