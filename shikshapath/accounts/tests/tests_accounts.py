from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import AuditLog

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test CustomUser model"""
    
    def test_user_creation_student(self):
        """Test creating a student user"""
        user = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
        
        self.assertEqual(user.role, 'student')
        self.assertFalse(user.is_suspended)
    
    def test_user_creation_instructor(self):
        """Test creating an instructor user"""
        user = User.objects.create_user(
            username='instructor@example.com',
            email='instructor@example.com',
            password='testpass123',
            role='instructor'
        )
        
        self.assertEqual(user.role, 'instructor')
    
    def test_user_suspend(self):
        """Test suspending a user"""
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        
        user.suspend()
        user.refresh_from_db()
        
        self.assertTrue(user.is_suspended)
        self.assertIsNotNone(user.suspended_at)
    
    def test_user_activate(self):
        """Test activating a suspended user"""
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        
        user.suspend()
        user.activate()
        user.refresh_from_db()
        
        self.assertFalse(user.is_suspended)
        self.assertIsNone(user.suspended_at)


class AuthenticationTestCase(TestCase):
    """Test authentication views"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        
        self.student = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
    
    def test_login_page_accessible(self):
        """Test that login page is accessible"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_register_page_accessible(self):
        """Test that register page is accessible"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_login(self):
        """Test user login"""
        success = self.client.login(username='student@example.com', password='testpass123')
        self.assertTrue(success)
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        success = self.client.login(username='student@example.com', password='wrongpassword')
        self.assertFalse(success)
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser@example.com',
            'email': 'newuser@example.com',
            'password1': 'newpass123!',
            'password2': 'newpass123!',
            'role': 'student'
        })
        
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_logout(self):
        """Test user logout"""
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.get(reverse('logout'))
        
        # Should be redirected
        self.assertEqual(response.status_code, 302)


class AuditLogTestCase(TestCase):
    """Test audit logging"""
    
    def test_audit_log_creation(self):
        """Test creating an audit log"""
        actor = User.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='testpass123',
            role='admin'
        )
        
        target = User.objects.create_user(
            username='user@example.com',
            email='user@example.com',
            password='testpass123'
        )
        
        log = AuditLog.objects.create(
            actor=actor,
            actor_email=actor.email,
            action='user_created',
            target_user=target,
            details={'created_by': 'admin'}
        )
        
        self.assertEqual(log.action, 'user_created')
        self.assertEqual(log.target_user, target)
        self.assertIsNotNone(log.timestamp)
