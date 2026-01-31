from django.urls import path
from django.contrib.auth.views import LogoutView
from django.shortcuts import render
from . import views
from .theme_views import switch_theme, get_themes_api

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Email OTP Verification
    path('send-otp/', views.send_otp_view, name='send_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('verify-email-profile/', views.verify_email_from_profile_view, name='verify_email_from_profile'),
    
    # Password Reset
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password-otp/', views.reset_password_otp_view, name='reset_password_otp'),
    path('set-new-password/', views.set_new_password_view, name='set_new_password'),
    
    # Account Recovery
    path('account-recovery/', views.account_recovery_view, name='account_recovery'),
    
    # Mobile OTP Verification
    path('send-mobile-otp/', views.send_mobile_otp_view, name='send_mobile_otp'),
    path('verify-mobile-otp/', views.verify_mobile_otp_view, name='verify_mobile_otp'),
    path('firebase-login/', views.firebase_login, name='firebase_login'),
    path('phone-login/', lambda r: render(r, 'accounts/phone_login.html'), name='phone_login'),

    
    # User Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # Theme Management
    path('theme/switch/<str:theme_name>/', switch_theme, name='switch_theme'),
    path('api/themes/', get_themes_api, name='get_themes_api'),
    
    # Dashboards
    path('instructor-dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
