from django.db import models
from accounts.models import CustomUser
from django.core.validators import MinValueValidator


class Course(models.Model):
    """
    Course model representing an online course.
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.1)])
    thumbnail = models.FileField(upload_to='course_thumbnails/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    is_private = models.BooleanField(default=False, help_text="If private, only enrolled students can access")
    made_private_at = models.DateTimeField(null=True, blank=True, help_text="When course was last made private")
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(null=True, blank=True)
    is_suspended = models.BooleanField(default=False)
    suspended_reason = models.TextField(null=True, blank=True)
    platform_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instructor', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['is_private']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_platform_fee(self):
        """Calculate platform fee for this course."""
        return (self.platform_fee_percentage / 100) * self.price
    
    def get_instructor_payout(self):
        """Calculate instructor payout."""
        return self.price - self.get_platform_fee()
    
    def enrollment_count(self):
        """Get number of enrollments."""
        return self.enrollments.filter(is_active=True).count()
    
    def is_accessible_by_user(self, user):
        """Check if a user can access this course."""
        # If course is public, anyone can see it
        if not self.is_private:
            return True
        
        # If private, only instructor and enrolled students can access
        if user.is_authenticated:
            if user == self.instructor:
                return True
            # Check if user is enrolled
            if self.enrollments.filter(student=user, is_active=True).exists():
                return True
        
        return False
    

class Enrollment(models.Model):
    """
    Enrollment model representing a user's enrollment in a course.
    """
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.email} - {self.course.title}"


class CourseResource(models.Model):
    """
    Course Resource model for videos, PDFs, notes, etc.
    """
    RESOURCE_TYPE_CHOICES = (
        ('video', 'Video'),
        ('pdf', 'PDF Document'),
        ('notes', 'Class Notes'),
        ('assignment', 'Assignment'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    file = models.FileField(upload_to='course_resources/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CourseRating(models.Model):
    """
    Rating and review model for courses.
    """
    RATING_CHOICES = (
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ratings')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='course_ratings')
    rating = models.IntegerField(choices=RATING_CHOICES)
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('course', 'student')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.student.email} ({self.rating}/5)"


class CourseReferral(models.Model):
    """
    Referral system for courses - track who referred whom.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='referrals')
    referrer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referrals_given')
    referred_student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referrals_received')
    referral_code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    is_converted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Referral: {self.course.title} ({self.referrer.email} -> {self.referred_student.email})"
