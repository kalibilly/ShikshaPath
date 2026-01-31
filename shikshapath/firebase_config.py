# Firebase Configuration
# Add your Firebase project credentials here

FIREBASE_CONFIG = {
    # Get these from Firebase Console > Project Settings > Service Account
    'type': 'service_account',
    'project_id': 'YOUR_PROJECT_ID',
    'private_key_id': 'YOUR_PRIVATE_KEY_ID',
    'private_key': 'YOUR_PRIVATE_KEY',
    'client_email': 'YOUR_CLIENT_EMAIL',
    'client_id': 'YOUR_CLIENT_ID',
    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
    'token_uri': 'https://oauth2.googleapis.com/token',
    'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
    'client_x509_cert_url': 'YOUR_CERT_URL',
}

# Web API Key (Get from Firebase Console > Project Settings > Web API Key)
FIREBASE_API_KEY = 'YOUR_WEB_API_KEY'

# App ID (Get from Firebase Console > Project Settings)
FIREBASE_APP_ID = 'YOUR_APP_ID'

# Note: Never commit actual credentials to version control.
# Use environment variables in production:
# import os
# FIREBASE_CONFIG = {
#     'project_id': os.getenv('FIREBASE_PROJECT_ID'),
#     'private_key': os.getenv('FIREBASE_PRIVATE_KEY'),
#     # ... etc
# }
