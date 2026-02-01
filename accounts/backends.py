from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
import firebase_admin
from firebase_admin import auth as firebase_auth

User = get_user_model()

class FirebaseAuthBackend(BaseBackend):
    def authenticate(self, request, token=None):
        try:
            # Verify Firebase ID token from frontend
            decoded_token = firebase_auth.verify_id_token(token)
            uid = decoded_token['uid']
            phone = decoded_token['phone_number']
            
            # Get/create Django user
            user, created = User.objects.get_or_create(
                username=phone,
                defaults={'email': f'{phone}@shikshapath.local'}
            )
            if created:
                user.set_password('firebase-phone-user')  # Unusable password
            user.is_active = True
            user.save()
            return user
        except Exception:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
