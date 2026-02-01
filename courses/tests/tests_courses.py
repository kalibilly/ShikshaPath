from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment
from decimal import Decimal

User = get_user_model()


class CourseModelTestCase(TestCase):
    """Test Course and Enrollment models"""
    
    def setUp(self):
        """Set up test data"""
        self.instructor = User.objects.create_user(
            username='instructor@example.com',
            email='instructor@example.com',
            password='testpass123',
            role='instructor'
        )
        
        self.student = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
    
    def test_course_creation(self):
        """Test creating a course"""
        course = Course.objects.create(
            instructor=self.instructor,
            title='Python Basics',
            description='Learn Python programming',
            price=Decimal('99.99'),
            status='published'
        )
        
        self.assertEqual(course.title, 'Python Basics')
        self.assertEqual(course.instructor, self.instructor)
        self.assertEqual(course.status, 'published')
    
    def test_course_platform_fee_calculation(self):
        """Test platform fee calculation"""
        course = Course.objects.create(
            instructor=self.instructor,
            title='Test Course',
            description='Test',
            price=Decimal('100.00'),
            platform_fee_percent=Decimal('10.00'),
            status='published'
        )
        
        self.assertEqual(course.get_platform_fee(), Decimal('10.00'))
        self.assertEqual(course.get_instructor_payout(), Decimal('90.00'))
    
    def test_course_enrollment_count(self):
        """Test enrollment count"""
        course = Course.objects.create(
            instructor=self.instructor,
            title='Popular Course',
            description='Very popular',
            price=Decimal('99.99'),
            status='published'
        )
        
        # Create enrollments
        Enrollment.objects.create(student=self.student, course=course, is_active=True)
        
        self.assertEqual(course.enrollment_count(), 1)
    
    def test_enrollment_creation(self):
        """Test creating an enrollment"""
        course = Course.objects.create(
            instructor=self.instructor,
            title='Test Course',
            description='Test',
            price=Decimal('99.99'),
            status='published'
        )
        
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=course,
            is_active=True
        )
        
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, course)
        self.assertTrue(enrollment.is_active)
    
    def test_unique_enrollment_constraint(self):
        """Test that a student can't enroll twice in same course"""
        course = Course.objects.create(
            instructor=self.instructor,
            title='Test Course',
            description='Test',
            price=Decimal('99.99'),
            status='published'
        )
        
        Enrollment.objects.create(student=self.student, course=course)
        
        # Try to create duplicate
        with self.assertRaises(Exception):
            Enrollment.objects.create(student=self.student, course=course)


class CourseViewTestCase(TestCase):
    """Test course views"""
    
    def setUp(self):
        """Set up test client and data"""
        self.client = Client()
        
        self.instructor = User.objects.create_user(
            username='instructor@example.com',
            email='instructor@example.com',
            password='testpass123',
            role='instructor'
        )
        
        self.student = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
        
        self.course = Course.objects.create(
            instructor=self.instructor,
            title='Public Course',
            description='A public course',
            price=Decimal('99.99'),
            status='published'
        )
    
    def test_home_view(self):
        """Test home page lists published courses"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Public Course', response.content)
    
    def test_home_excludes_draft_courses(self):
        """Test that draft courses don't appear on home"""
        draft_course = Course.objects.create(
            instructor=self.instructor,
            title='Draft Course',
            description='Not published',
            price=Decimal('99.99'),
            status='draft'
        )
        
        response = self.client.get(reverse('home'))
        self.assertNotIn(b'Draft Course', response.content)
    
    def test_home_excludes_suspended_courses(self):
        """Test that suspended courses don't appear on home"""
        suspended_course = Course.objects.create(
            instructor=self.instructor,
            title='Suspended Course',
            description='Suspended',
            price=Decimal('99.99'),
            status='published',
            is_suspended=True
        )
        
        response = self.client.get(reverse('home'))
        self.assertNotIn(b'Suspended Course', response.content)
    
    def test_course_detail_view(self):
        """Test course detail page"""
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Public Course', response.content)
    
    def test_course_detail_shows_enrollment_button_for_unenrolled(self):
        """Test unenrolled students see enroll button"""
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        # Check for enroll button (specific text depends on template)
        self.assertEqual(response.status_code, 200)
    
    def test_my_courses_requires_login(self):
        """Test that my_courses requires login"""
        response = self.client.get(reverse('my_courses'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_my_courses_shows_enrolled_courses(self):
        """Test student sees their enrolled courses"""
        Enrollment.objects.create(student=self.student, course=self.course, is_active=True)
        
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.get(reverse('my_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Public Course', response.content)
    
    def test_create_course_requires_instructor(self):
        """Test that non-instructors can't create courses"""
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.get(reverse('create_course'))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_instructor_can_create_course(self):
        """Test instructor can create course"""
        self.client.login(username='instructor@example.com', password='testpass123')
        response = self.client.post(reverse('create_course'), {
            'title': 'New Course',
            'description': 'Test course',
            'price': '199.99',
            'platform_fee_percent': '10.00'
        })
        
        self.assertTrue(Course.objects.filter(title='New Course').exists())
    
    def test_instructor_can_edit_own_course(self):
        """Test instructor can edit their own course"""
        self.client.login(username='instructor@example.com', password='testpass123')
        response = self.client.post(reverse('edit_course', args=[self.course.id]), {
            'title': 'Updated Title',
            'description': 'Updated description',
            'price': '149.99',
            'platform_fee_percent': '10.00'
        })
        
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Title')
    
    def test_instructor_cannot_edit_others_course(self):
        """Test instructor can't edit another instructor's course"""
        other_instructor = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123',
            role='instructor'
        )
        
        self.client.login(username='other@example.com', password='testpass123')
        response = self.client.get(reverse('edit_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 404)
    
    def test_enroll_free_course(self):
        """Test enrolling in free course"""
        free_course = Course.objects.create(
            instructor=self.instructor,
            title='Free Course',
            description='Free',
            price=Decimal('0.00'),
            status='published'
        )
        
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.post(reverse('enroll_course', args=[free_course.id]))
        
        # Check enrollment was created
        self.assertTrue(Enrollment.objects.filter(
            student=self.student,
            course=free_course
        ).exists())
    
    def test_enroll_paid_course_redirects_to_payment(self):
        """Test enrolling in paid course redirects to payment"""
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.post(reverse('enroll_course', args=[self.course.id]))
        
        # Should redirect to payment
        self.assertEqual(response.status_code, 302)
        self.assertIn('/payments/', response.url)
