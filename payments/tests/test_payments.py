from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment
from payments.models import Payment, Payout
from decimal import Decimal
import json
from unittest.mock import patch, MagicMock

User = get_user_model()


class PaymentModelTestCase(TestCase):
    """Test Payment and Payout models"""
    
    def setUp(self):
        """Set up test data"""
        self.student = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
        
        self.instructor = User.objects.create_user(
            username='instructor@example.com',
            email='instructor@example.com',
            password='testpass123',
            role='instructor'
        )
        
        self.course = Course.objects.create(
            instructor=self.instructor,
            title='Test Course',
            description='A test course',
            price=Decimal('99.99'),
            platform_fee_percent=Decimal('10.00'),
            status='published'
        )
    
    def test_payment_creation(self):
        """Test creating a payment record"""
        payment = Payment.objects.create(
            student=self.student,
            instructor=self.instructor,
            course=self.course,
            amount=Decimal('99.99'),
            platform_fee=Decimal('10.00'),
            instructor_payout=Decimal('89.99'),
            status='created',
            razorpay_order_id='order_123'
        )
        
        self.assertEqual(payment.status, 'created')
        self.assertEqual(payment.amount, Decimal('99.99'))
        self.assertTrue(str(payment).startswith('Payment'))
    
    def test_payout_creation(self):
        """Test creating a payout record"""
        payout = Payout.objects.create(
            instructor=self.instructor,
            course=self.course,
            total_amount=Decimal('89.99'),
            status='pending',
            payment_method='bank_transfer'
        )
        
        self.assertEqual(payout.status, 'pending')
        self.assertEqual(payout.total_amount, Decimal('89.99'))
        self.assertFalse(payout.transferred)


class PaymentViewTestCase(TestCase):
    """Test payment views and payment flow"""
    
    def setUp(self):
        """Set up test client and users"""
        self.client = Client()
        
        self.student = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
        
        self.instructor = User.objects.create_user(
            username='instructor@example.com',
            email='instructor@example.com',
            password='testpass123',
            role='instructor'
        )
        
        self.course = Course.objects.create(
            instructor=self.instructor,
            title='Premium Course',
            description='A premium course for learning',
            price=Decimal('299.99'),
            platform_fee_percent=Decimal('10.00'),
            status='published'
        )
    
    def test_make_payment_not_logged_in(self):
        """Test that payment page requires login"""
        response = self.client.get(reverse('payments:make_payment', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_make_payment_logged_in(self):
        """Test payment initiation page for logged in user"""
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.get(reverse('payments:make_payment', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Complete Payment', response.content)
    
    def test_make_payment_already_enrolled(self):
        """Test that enrolled students are redirected"""
        # Enroll student first
        Enrollment.objects.create(
            student=self.student,
            course=self.course,
            is_active=True
        )
        
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.get(reverse('payments:make_payment', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    @patch('razorpay.Client.order.create')
    def test_initiate_razorpay_order(self, mock_create):
        """Test Razorpay order creation"""
        mock_create.return_value = {
            'id': 'order_test123',
            'amount': 29999,
            'currency': 'INR'
        }
        
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.post(reverse('payments:make_payment', args=[self.course.id]))
        
        # Check that order was created
        self.assertEqual(Payment.objects.count(), 1)
        payment = Payment.objects.first()
        self.assertEqual(payment.razorpay_order_id, 'order_test123')
        self.assertEqual(payment.status, 'created')
    
    def test_confirm_payment_valid_signature(self):
        """Test payment confirmation with valid signature"""
        import hmac
        import hashlib
        
        # Create a test payment
        payment = Payment.objects.create(
            student=self.student,
            instructor=self.instructor,
            course=self.course,
            amount=Decimal('299.99'),
            platform_fee=Decimal('30.00'),
            instructor_payout=Decimal('269.99'),
            status='created',
            razorpay_order_id='order_test123'
        )
        
        # Generate valid signature
        signature_data = f'order_test123|payment_test123'
        from django.conf import settings
        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            signature_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        self.client.login(username='student@example.com', password='testpass123')
        
        response = self.client.post(reverse('payments:confirm_payment'), {
            'razorpay_order_id': 'order_test123',
            'razorpay_payment_id': 'payment_test123',
            'razorpay_signature': expected_signature,
            'course_id': self.course.id
        })
        
        # Check response
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        
        # Check payment was updated
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'captured')
        self.assertEqual(payment.razorpay_payment_id, 'payment_test123')
    
    def test_confirm_payment_invalid_signature(self):
        """Test payment confirmation with invalid signature"""
        # Create a test payment
        payment = Payment.objects.create(
            student=self.student,
            instructor=self.instructor,
            course=self.course,
            amount=Decimal('299.99'),
            platform_fee=Decimal('30.00'),
            instructor_payout=Decimal('269.99'),
            status='created',
            razorpay_order_id='order_test123'
        )
        
        self.client.login(username='student@example.com', password='testpass123')
        
        response = self.client.post(reverse('payments:confirm_payment'), {
            'razorpay_order_id': 'order_test123',
            'razorpay_payment_id': 'payment_test123',
            'razorpay_signature': 'invalid_signature',
            'course_id': self.course.id
        })
        
        # Check response
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'failed')
        
        # Check payment was NOT updated
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'created')
    
    def test_enrollment_created_on_payment(self):
        """Test that enrollment is created after successful payment"""
        import hmac
        import hashlib
        
        payment = Payment.objects.create(
            student=self.student,
            instructor=self.instructor,
            course=self.course,
            amount=Decimal('299.99'),
            platform_fee=Decimal('30.00'),
            instructor_payout=Decimal('269.99'),
            status='created',
            razorpay_order_id='order_test456'
        )
        
        # Generate valid signature
        signature_data = f'order_test456|payment_test456'
        from django.conf import settings
        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            signature_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        self.client.login(username='student@example.com', password='testpass123')
        
        response = self.client.post(reverse('payments:confirm_payment'), {
            'razorpay_order_id': 'order_test456',
            'razorpay_payment_id': 'payment_test456',
            'razorpay_signature': expected_signature,
            'course_id': self.course.id
        })
        
        # Check enrollment was created
        enrollment = Enrollment.objects.filter(student=self.student, course=self.course).first()
        self.assertIsNotNone(enrollment)
        self.assertTrue(enrollment.is_active)


class InstructorPayoutTestCase(TestCase):
    """Test instructor payout functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.instructor = User.objects.create_user(
            username='instructor@example.com',
            email='instructor@example.com',
            password='testpass123',
            role='instructor'
        )
        
        self.student1 = User.objects.create_user(
            username='student1@example.com',
            email='student1@example.com',
            password='testpass123',
            role='student'
        )
        
        self.student2 = User.objects.create_user(
            username='student2@example.com',
            email='student2@example.com',
            password='testpass123',
            role='student'
        )
        
        self.course = Course.objects.create(
            instructor=self.instructor,
            title='Instructor Course',
            description='Course by instructor',
            price=Decimal('199.99'),
            platform_fee_percent=Decimal('10.00'),
            status='published'
        )
        
        # Create multiple payments
        Payment.objects.create(
            student=self.student1,
            instructor=self.instructor,
            course=self.course,
            amount=Decimal('199.99'),
            platform_fee=Decimal('20.00'),
            instructor_payout=Decimal('179.99'),
            status='captured',
            razorpay_payment_id='pay_001'
        )
        
        Payment.objects.create(
            student=self.student2,
            instructor=self.instructor,
            course=self.course,
            amount=Decimal('199.99'),
            platform_fee=Decimal('20.00'),
            instructor_payout=Decimal('179.99'),
            status='captured',
            razorpay_payment_id='pay_002'
        )
    
    def test_payout_view_requires_instructor(self):
        """Test that non-instructors cannot access payout views"""
        self.client.login(username='student1@example.com', password='testpass123')
        response = self.client.get(reverse('payments:payouts_history'))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_instructor_payouts_history(self):
        """Test instructor can view payout history"""
        self.client.login(username='instructor@example.com', password='testpass123')
        response = self.client.get(reverse('payments:payouts_history'))
        self.assertEqual(response.status_code, 200)
    
    def test_course_payments_view(self):
        """Test instructor can view payments for their course"""
        self.client.login(username='instructor@example.com', password='testpass123')
        response = self.client.get(reverse('payments:course_payments', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Complete Payment', response.content)
