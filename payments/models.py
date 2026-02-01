from django.db import models
from accounts.models import CustomUser
from courses.models import Course
from decimal import Decimal

# Create your models here.
class Payment(models.Model):
    """
    Payment record for course enrollment using Razorpay.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('created', 'Created'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    student = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='payments')
    instructor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='received_payments')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    instructor_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', '-created_at']),
            models.Index(fields=['instructor', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Payment {self.id} - {self.student} for {self.course}"
    

class Payout(models.Model):
    """
    Payout record for instructor earnings.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payouts')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='payouts')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, default='bank_transfer')  # bank_transfer, paypal, etc.
    bank_account = models.CharField(max_length=255, blank=True, null=True)
    transferred = models.BooleanField(default=False)
    razorpay_transfer_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instructor', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Payout {self.id} - {self.instructor} - {self.total_amount}"
