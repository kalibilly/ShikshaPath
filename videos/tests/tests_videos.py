from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from courses.models import Course, Enrollment
from videos.models import Video, VideoProgress, TranscodingJob
from decimal import Decimal
import os

User = get_user_model()


class VideoModelTestCase(TestCase):
    """Test Video and related models"""
    
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
        
        self.course = Course.objects.create(
            instructor=self.instructor,
            title='Video Course',
            description='A course with videos',
            price=Decimal('99.99'),
            status='published'
        )
    
    def test_video_creation(self):
        """Test creating a video"""
        video = Video.objects.create(
            course=self.course,
            title='Introduction',
            description='Intro video',
            video_file='videos/intro.mp4',
            duration=300,
            order=1
        )
        
        self.assertEqual(video.title, 'Introduction')
        self.assertEqual(video.duration, 300)
        self.assertEqual(video.status, 'processing')  # Default status
    
    def test_video_progress_creation(self):
        """Test creating video progress record"""
        video = Video.objects.create(
            course=self.course,
            title='Lesson 1',
            video_file='videos/lesson1.mp4',
            duration=600
        )
        
        progress = VideoProgress.objects.create(
            video=video,
            student=self.student,
            watched_duration=300
        )
        
        self.assertEqual(progress.watched_duration, 300)
        self.assertFalse(progress.is_completed)
    
    def test_video_progress_completion_percent(self):
        """Test completion percentage calculation"""
        video = Video.objects.create(
            course=self.course,
            title='Full Video',
            video_file='videos/full.mp4',
            duration=1000
        )
        
        progress = VideoProgress.objects.create(
            video=video,
            student=self.student,
            watched_duration=500
        )
        progress.update_completion()
        
        self.assertEqual(progress.completion_percent, Decimal('50.00'))
    
    def test_video_marks_complete_at_90_percent(self):
        """Test that video marks complete at 90% watched"""
        video = Video.objects.create(
            course=self.course,
            title='Short Video',
            video_file='videos/short.mp4',
            duration=1000
        )
        
        progress = VideoProgress.objects.create(
            video=video,
            student=self.student,
            watched_duration=900
        )
        progress.update_completion()
        
        self.assertTrue(progress.is_completed)
        self.assertEqual(progress.completion_percent, Decimal('90.00'))
    
    def test_transcoding_job_creation(self):
        """Test creating a transcoding job"""
        video = Video.objects.create(
            course=self.course,
            title='Test Video',
            video_file='videos/test.mp4'
        )
        
        job = TranscodingJob.objects.create(
            video=video,
            source_file='videos/test.mp4'
        )
        
        self.assertEqual(job.status, 'pending')
        self.assertEqual(job.source_file, 'videos/test.mp4')
    
    def test_unique_progress_constraint(self):
        """Test that student can't have multiple progress records for same video"""
        video = Video.objects.create(
            course=self.course,
            title='Test Video',
            video_file='videos/test.mp4'
        )
        
        VideoProgress.objects.create(video=video, student=self.student)
        
        with self.assertRaises(Exception):
            VideoProgress.objects.create(video=video, student=self.student)


class VideoViewTestCase(TestCase):
    """Test video views"""
    
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
            title='Test Course',
            description='Test',
            price=Decimal('99.99'),
            status='published'
        )
        
        self.video = Video.objects.create(
            course=self.course,
            title='Test Video',
            description='A test video',
            video_file='videos/test.mp4',
            duration=600
        )
    
    def test_upload_video_requires_instructor(self):
        """Test that only instructors can upload videos"""
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.get(reverse('videos:upload_video', args=[self.course.id]))
        self.assertEqual(response.status_code, 403)
    
    def test_upload_video_requires_own_course(self):
        """Test that instructor can only upload to own courses"""
        other_instructor = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123',
            role='instructor'
        )
        
        self.client.login(username='other@example.com', password='testpass123')
        response = self.client.get(reverse('videos:upload_video', args=[self.course.id]))
        self.assertEqual(response.status_code, 404)
    
    def test_instructor_can_upload_video(self):
        """Test instructor can upload video to own course"""
        self.client.login(username='instructor@example.com', password='testpass123')
        response = self.client.get(reverse('videos:upload_video', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_watch_video_requires_enrollment_or_instructor(self):
        """Test that only enrolled students can watch video"""
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.get(reverse('videos:watch_video', args=[self.video.id]))
        # Should redirect to login since not enrolled
        self.assertEqual(response.status_code, 302)
    
    def test_enrolled_student_can_watch_video(self):
        """Test that enrolled students can watch video"""
        # Enroll student
        Enrollment.objects.create(student=self.student, course=self.course, is_active=True)
        
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.get(reverse('videos:watch_video', args=[self.video.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_instructor_can_watch_own_course_video(self):
        """Test that instructor can watch their own course videos"""
        self.client.login(username='instructor@example.com', password='testpass123')
        response = self.client.get(reverse('videos:watch_video', args=[self.video.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_stream_video_requires_enrollment(self):
        """Test that streaming requires enrollment"""
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.get(reverse('videos:stream_video', args=[self.video.id]))
        self.assertEqual(response.status_code, 403)
    
    def test_save_progress_updates_watched_duration(self):
        """Test saving video progress"""
        # Enroll student first
        Enrollment.objects.create(student=self.student, course=self.course, is_active=True)
        
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.post(reverse('videos:save_progress', args=[self.video.id]), {
            'watched_duration': '300'
        })
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        
        # Verify progress was saved
        progress = VideoProgress.objects.get(video=self.video, student=self.student)
        self.assertEqual(progress.watched_duration, 300)
    
    def test_save_progress_calculates_completion(self):
        """Test that saving progress calculates completion percent"""
        Enrollment.objects.create(student=self.student, course=self.course, is_active=True)
        
        self.client.login(username='student@example.com', password='testpass123')
        response = self.client.post(reverse('videos:save_progress', args=[self.video.id]), {
            'watched_duration': '540'  # 90% of 600 seconds
        })
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['is_completed'])
        self.assertEqual(float(data['completion_percent']), 90.0)
