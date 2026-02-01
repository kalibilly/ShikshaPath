from django.contrib import admin
from .models import Payment, Payout


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student__email', 'course__title', 'transaction_id')
    readonly_fields = ('created_at', 'completed_at', 'razorpay_order_id')


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'instructor', 'total_amount', 'status', 'transferred', 'created_at')
    list_filter = ('status', 'transferred', 'created_at')
    search_fields = ('instructor__email', 'stripe_transfer_id')
    readonly_fields = ('created_at', 'completed_at')
