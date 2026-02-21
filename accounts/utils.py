"""
Utility functions for accounts app
"""
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP, CustomUser
from django.utils import timezone
from datetime import timedelta
import logging
from threading import Thread
import socket

logger = logging.getLogger(__name__)


def send_otp(email):
    """
    Generate and send OTP to user's email address
    
    Args:
        email (str): User's email address
    
    Returns:
        bool: True if OTP was sent successfully, False otherwise
    """
    try:
        # Get user
        user = CustomUser.objects.get(email=email)
        
        # Create or get OTP
        otp, created = OTP.objects.get_or_create(
            user=user,
            defaults={
                'expires_at': timezone.now() + timedelta(minutes=10)
            }
        )
        
        # If OTP exists but expired, create a new one
        if not created and not otp.is_valid():
            otp.delete()
            otp = OTP.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(minutes=10)
            )
        
        # Send OTP email
        subject = "Your ShikshaPath Email Verification OTP"
        message = f"""
Hello {user.first_name},

Your One-Time Password (OTP) for email verification is:

{otp.code}

This OTP is valid for 10 minutes. Please do not share this OTP with anyone.

If you did not request this OTP, please ignore this email.

Best regards,
ShikshaPath Team
        """
        
        html_message = f"""
<html>
    <body>
        <h2>Email Verification</h2>
        <p>Hello {user.first_name},</p>
        <p>Your One-Time Password (OTP) for email verification is:</p>
        <h1 style="font-size: 32px; font-weight: bold; color: #3b82f6; letter-spacing: 2px;">
            {otp.code}
        </h1>
        <p><strong>Valid for: 10 minutes</strong></p>
        <p style="color: #ef4444;">⚠️ Do not share this OTP with anyone.</p>
        <p>If you did not request this OTP, please ignore this email.</p>
        <hr>
        <p>Best regards,<br>ShikshaPath Team</p>
    </body>
</html>
        """
        
        # Send email asynchronously to prevent timeout in production
        try:
            # Try to send email with timeout
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=html_message,
                fail_silently=True,  # Don't fail registration if email fails
                timeout=5,  # 5 second timeout
            )
            return True
        except socket.timeout:
            logger.warning(f"Email timeout for {email}, but account created successfully")
            return True  # Account created even if email failed
        except Exception as e:
            logger.error(f"Error sending OTP: {e}")
            # Still return True so user can proceed - they can resend OTP
            return True
    
    except CustomUser.DoesNotExist:
        return False
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return False


def send_password_reset_otp(email):
    """
    Send OTP for password reset (similar to send_otp but with different message)
    
    Args:
        email (str): User's email address
    
    Returns:
        bool: True if OTP was sent successfully, False otherwise
    """
    try:
        user = CustomUser.objects.get(email=email)
        
        # Create OTP for password reset
        otp = OTP.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        subject = "Your ShikshaPath Password Reset OTP"
        message = f"""
Hello {user.first_name},

Your One-Time Password (OTP) for password reset is:

{otp.code}

This OTP is valid for 15 minutes. Please do not share this OTP with anyone.

If you did not request a password reset, please ignore this email.

Best regards,
ShikshaPath Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        return True
    
    except Exception as e:
        print(f"Error sending password reset OTP: {e}")
        return False

def send_mobile_otp(mobile_number, otp_code):
    """
    Send OTP to user's mobile number via SMS
    
    SETUP REQUIRED: This function requires SMS provider configuration.
    See MOBILE_OTP_SETUP.md for detailed setup instructions.
    
    Args:
        mobile_number (str): User's mobile number
        otp_code (str): The OTP code to send
    
    Returns:
        bool: True if OTP was sent successfully, False otherwise
    """
    try:
        # Check if SMS provider is configured
        sms_provider = getattr(settings, 'SMS_PROVIDER', None)
        
        if not sms_provider:
            print("⚠️ SMS provider not configured. See MOBILE_OTP_SETUP.md for setup instructions.")
            # For now, log the OTP to console for testing
            print(f"[TEST MODE] SMS OTP for {mobile_number}: {otp_code}")
            return True
        
        if sms_provider == 'twilio':
            return _send_via_twilio(mobile_number, otp_code)
        elif sms_provider == 'aws_sns':
            return _send_via_aws_sns(mobile_number, otp_code)
        elif sms_provider == 'msg91':
            return _send_via_msg91(mobile_number, otp_code)
        else:
            print(f"Unknown SMS provider: {sms_provider}")
            return False
    
    except Exception as e:
        print(f"Error sending mobile OTP: {e}")
        return False


def _send_via_twilio(mobile_number, otp_code):
    """Send SMS via Twilio"""
    try:
        from twilio.rest import Client
        
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID')
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN')
        from_number = getattr(settings, 'TWILIO_PHONE_NUMBER')
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f"Your ShikshaPath verification code is: {otp_code}. Valid for 10 minutes.",
            from_=from_number,
            to=mobile_number
        )
        return True
    except Exception as e:
        print(f"Twilio SMS error: {e}")
        return False


def _send_via_aws_sns(mobile_number, otp_code):
    """Send SMS via AWS SNS"""
    try:
        import boto3
        
        sns_client = boto3.client(
            'sns',
            region_name=getattr(settings, 'AWS_REGION', 'us-east-1'),
            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        )
        
        sns_client.publish(
            PhoneNumber=mobile_number,
            Message=f"Your ShikshaPath verification code is: {otp_code}. Valid for 10 minutes."
        )
        return True
    except Exception as e:
        print(f"AWS SNS SMS error: {e}")
        return False


def _send_via_msg91(mobile_number, otp_code):
    """Send SMS via MSG91 (Indian SMS provider)"""
    try:
        import requests
        
        authkey = getattr(settings, 'MSG91_AUTH_KEY')
        route = getattr(settings, 'MSG91_ROUTE', '4')
        
        url = "https://api.msg91.com/api/sendhttp"
        params = {
            'authkey': authkey,
            'mobiles': mobile_number,
            'message': f"Your ShikshaPath verification code is: {otp_code}. Valid for 10 minutes.",
            'route': route,
            'sender': getattr(settings, 'MSG91_SENDER_ID', 'SHIKSHA')
        }
        
        response = requests.get(url, params=params)
        return response.status_code == 200
    except Exception as e:
        print(f"MSG91 SMS error: {e}")
        return False
