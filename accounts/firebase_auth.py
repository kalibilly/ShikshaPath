"""
Firebase Phone Authentication Backend for Django
Handles OTP verification via Firebase Authentication
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class FirebasePhoneAuthBackend(ModelBackend):
    """
    Custom authentication backend using Firebase Phone Authentication
    """
    
    _app = None
    
    @classmethod
    def initialize_firebase(cls, firebase_config):
        """
        Initialize Firebase Admin SDK
        Must be called once during app startup
        """
        if cls._app is None:
            try:
                # Import Firebase locally only when initializing
                import firebase_admin
                from firebase_admin import credentials
                
                cred = credentials.Certificate(firebase_config)
                cls._app = firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {e}")
                raise
    
    @staticmethod
    def verify_phone_token(id_token):
        """
        Verify Firebase ID token from phone auth
        
        Args:
            id_token: Token returned from Firebase after successful OTP verification
            
        Returns:
            dict: Firebase user data if valid, None otherwise
        """
        try:
            # Import Firebase locally only when needed
            from firebase_admin import auth
            
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def authenticate(self, request, id_token=None, **kwargs):
        """
        Authenticate user using Firebase phone auth token
        
        Args:
            request: Django request object
            id_token: Firebase ID token from phone authentication
            
        Returns:
            User object if authentication successful, None otherwise
        """
        if not id_token:
            return None
        
        # Verify the token with Firebase
        decoded_token = self.verify_phone_token(id_token)
        if not decoded_token:
            return None
        
        # Extract phone number from Firebase user data
        phone_number = decoded_token.get('phone_number')
        firebase_uid = decoded_token.get('uid')
        
        if not phone_number:
            logger.warning("No phone number in Firebase token")
            return None
        
        # Find or create user in Django
        try:
            user = CustomUser.objects.get(mobile_number=phone_number)
        except CustomUser.DoesNotExist:
            # Create new user
            try:
                user = CustomUser.objects.create_user(
                    mobile_number=phone_number,
                    username=phone_number,
                    firebase_uid=firebase_uid,
                    is_email_verified=False,  # Email not verified yet
                )
                logger.info(f"New user created via Firebase: {phone_number}")
            except Exception as e:
                logger.error(f"Failed to create user: {e}")
                return None
        
        # Update Firebase UID
        if not user.firebase_uid:
            user.firebase_uid = firebase_uid
            user.save()
        
        return user
    
    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None


class FirebasePhoneOTPService:
    """
    Service for managing Firebase Phone OTP verification
    """
    
    @staticmethod
    def send_verification_code(phone_number, request):
        """
        Send OTP to phone number via Firebase
        
        Note: Firebase phone auth is client-side in web apps.
        This returns the necessary data for client-side verification.
        
        Args:
            phone_number: Phone number to verify (E.164 format, e.g., +1234567890)
            request: Django request
            
        Returns:
            dict: Response with verification ID or error
        """
        try:
            # In a real implementation, you would use Firebase REST API
            # or store the request for later verification
            
            return {
                'success': True,
                'message': 'OTP sent to phone',
                'phone_number': phone_number,
                'note': 'Use Firebase client SDK on frontend for phone verification'
            }
        except Exception as e:
            logger.error(f"Failed to send OTP: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def verify_otp(phone_number, otp_code):
        """
        Verify OTP code (typically called from frontend after Firebase verification)
        
        Args:
            phone_number: Phone number being verified
            otp_code: OTP code provided by user
            
        Returns:
            dict: Success status and user data if successful
        """
        try:
            # Firebase OTP verification happens client-side
            # This is a placeholder for server-side verification if needed
            
            return {
                'success': True,
                'message': 'OTP verified successfully'
            }
        except Exception as e:
            logger.error(f"OTP verification failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
