"""
Accounts app - User authentication and profile management
"""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        # Initialize Firebase (if credentials are configured)
        from django.conf import settings
        try:
            from firebase_config import FIREBASE_CONFIG
            
            # Check if Firebase is actually configured (not placeholder values)
            if FIREBASE_CONFIG.get('project_id') != 'YOUR_PROJECT_ID':
                from accounts.firebase_auth import FirebasePhoneAuthBackend
                FirebasePhoneAuthBackend.initialize_firebase(FIREBASE_CONFIG)
                if settings.DEBUG:
                    print("✓ Firebase initialized successfully")
            else:
                if settings.DEBUG:
                    print("⚠ Firebase not configured (using placeholder credentials)")
        except ImportError:
            if settings.DEBUG:
                print("⚠ Firebase config not found")
        except Exception as e:
            if settings.DEBUG:
                print(f"⚠ Firebase initialization skipped: {str(e)}")
            
    verbose_name = 'Accounts'
