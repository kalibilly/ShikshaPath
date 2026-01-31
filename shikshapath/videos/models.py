from django.db import models
from courses.models import Course
from django.utils import timezone


class Video(models.Model):
    """
    Video model representing course videos.
    """
    STATUS_CHOICES = (
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed,', 'Failed'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField(upload_to='videos/')
    thumbnail = models.FileField(upload_to='video_thumbnails/', blank=True, null=True)
    duration = models.IntegerField(default=0)  # in seconds
    order = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    s3_video_key = models.CharField(max_length=500, blank=True, null=True)  # S3 object key
    s3_thumbnail_key = models.CharField(max_length=500, blank=True, null=True)  # S3 object key
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['course', 'order']),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"
    

class VideoProgress(models.Model):
    """
    Track student progress on videos.
    """
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='progress')
    student = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='video_progress')
    watched_duration = models.IntegerField(default=0)  # in seconds
    is_completed = models.BooleanField(default=False)
    completion_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    last_watched_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('video', 'student')
        ordering = ['-last_watched_at']
    
    def __str__(self):
        return f"{self.student.email} - {self.video.title}"
    
    def update_completion(self):
        """Update completion percentage"""
        if self.video.duration > 0:
            self.completion_percent = (self.watched_duration / self.video.duration) * 100
            if self.completion_percent >= 90:
                self.is_completed = True
            self.save()


class TranscodingJob(models.Model):
    """
    Track video transcoding jobs for background processing.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='transcoding_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    source_file = models.CharField(max_length=500)
    output_file = models.CharField(max_length=500, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Job {self.id} - {self.video.title}"
