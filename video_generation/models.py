from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Course
import uuid

User = get_user_model()


class VideoGenerationTask(models.Model):
    """Track 3D video generation jobs using Manim"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    ANIMATION_STYLE_CHOICES = (
        ('mathematical', 'Mathematical'),
        ('business', 'Business'),
        ('technical', 'Technical'),
        ('educational', 'Educational'),
    )
    
    task_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='video_generations')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_generations')
    
    # Content input
    source_content = models.TextField(help_text="The text/notes to convert to animation")
    animation_style = models.CharField(
        max_length=20,
        choices=ANIMATION_STYLE_CHOICES,
        default='educational'
    )
    
    # Configuration
    duration = models.IntegerField(default=60, help_text="Duration in seconds")
    quality = models.CharField(
        max_length=10,
        choices=[('low', 'Low (480p)'), ('medium', 'Medium (720p)'), ('high', 'High (1080p)')],
        default='medium'
    )
    title = models.CharField(max_length=255, blank=True)
    
    # Output
    generated_video = models.FileField(upload_to='generated_videos/', null=True, blank=True)
    thumbnail = models.FileField(upload_to='video_thumbnails/', null=True, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    progress_percentage = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['instructor', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.animation_style} ({self.status})"
    
    def get_duration_display(self):
        """Format duration as MM:SS"""
        mins, secs = divmod(self.duration, 60)
        return f"{mins}:{secs:02d}"

