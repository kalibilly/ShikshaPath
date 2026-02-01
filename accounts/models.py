from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import uuid
import secrets
import random


# Create your models here.

class CustomUser(AbstractUser):
    """
    Extended User model with role-based access control.
    Roles: student, instructor, admin
    """
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    )
    
    THEME_CHOICES = (
        ('dark', 'Dark Mode'),
        ('light', 'Light Mode'),
        ('gaming', 'Gaming Theme'),
        ('transparent', 'Transparent Glass'),
        ('pink', 'Pink Paradise'),
        ('purple', 'Purple Passion'),
        ('ocean', 'Ocean Blue'),
        ('forest', 'Forest Green'),
        ('sunset', 'Sunset'),
        ('midnight', 'Midnight Blue'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='dark', help_text='User preferred theme')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.FileField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True, unique=True, help_text='Mobile number for registration/verification')
    firebase_uid = models.CharField(max_length=255, blank=True, null=True, unique=True, help_text='Firebase unique identifier for phone auth')
    is_suspended = models.BooleanField(default=False)
    suspended_at = models.DateTimeField(blank=True, null=True)
    email_verified = models.BooleanField(default=False, help_text='Is user email verified?')
    phone_verified = models.BooleanField(default=False, help_text='Is mobile number verified?')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} ({self.role})"
    
    def suspend(self):
        """Suspend user account"""
        self.is_suspended = True
        self.suspended_at = timezone.now()
        self.save()

    def activate(self):
        """Activate suspended user account"""
        self.is_suspended = False
        self.suspended_at = None
        self.save()


class OTP(models.Model):
    """One-Time Password model for email verification"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='email_otp')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_verified and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"Email OTP for {self.user.email}"


class MobileOTP(models.Model):
    """One-Time Password model for mobile number verification"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='mobile_otp')
    mobile_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Mobile OTP'
        verbose_name_plural = 'Mobile OTPs'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_verified and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"Mobile OTP for {self.mobile_number}"


class PasswordResetOTP(models.Model):
    """One-Time Password model for password reset"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='password_reset_otp')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Password Reset OTP'
        verbose_name_plural = 'Password Reset OTPs'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_verified and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"Password Reset OTP for {self.user.email}"


class AuditLog(models.Model):
    """
    Audit log for tracking admin actions and system events.
    """
    ACTION_CHOICES = (
        ('user_created', 'User Created'),
        ('user_suspended', 'User Suspended'),
        ('user_activated', 'User Activated'),
        ('user_deleted', 'User Deleted'),
        ('course_created', 'Course Created'),
        ('course_updated', 'Course Updated'),
        ('course_suspended', 'Course Suspended'),
        ('course_unsuspended', 'Course Unsuspended'),
        ('course_flagged', 'Course Flagged'),
        ('course_unflagged', 'Course Unflagged'),
        ('course_deleted', 'Course Deleted'),
        ('payment_processed', 'Payment Processed'),
        ('payment_created', 'Payment Created'),
        ('payment_transferred', 'Payment Transferred'),
    )
    
    actor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='audit_logs_created')
    actor_email = models.CharField(max_length=255,)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='audit_logs_target')
    target_course = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)  # Supports IPv6
    

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['target_user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.action} by {self.actor_email} at {self.timestamp}"