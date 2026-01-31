from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from accounts.decorators import instructor_required
from courses.models import Course, Enrollment
from .models import Payment, Payout
from .forms import PayoutForm
from decimal import Decimal
import razorpay
import json
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


@login_required
def make_payment(request, course_id):
    """Initiate payment for course enrollment - creates Razorpay order"""
    course = get_object_or_404(Course, id=course_id)
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists():
        return redirect('courses:course_detail', course_id=course.id)
    
    if request.method == 'POST':
        try:
            # Create Razorpay Order
            amount_in_paise = int(course.price * 100)  # Razorpay expects amount in paise
            
            order_data = {
                'amount': amount_in_paise,
                'currency': 'INR',
                'receipt': f'course_{course.id}_student_{request.user.id}',
                'notes': {
                    'course_id': course.id,
                    'student_id': request.user.id,
                    'course_title': course.title,
                }
            }
            
            razorpay_order = razorpay_client.order.create(data=order_data)
            
            # Create Payment record in pending status
            platform_fee = Decimal(str(amount_in_paise / 100)) * Decimal(str(course.platform_fee_percentage / 100))
            instructor_payout = Decimal(str(amount_in_paise / 100)) - platform_fee
            
            payment = Payment.objects.create(
                student=request.user,
                instructor=course.instructor,
                course=course,
                amount=Decimal(str(amount_in_paise / 100)),
                platform_fee=platform_fee,
                instructor_payout=instructor_payout,
                status='created',
                razorpay_order_id=razorpay_order['id'],
                transaction_id=f"{razorpay_order['id']}_{request.user.id}"
            )
            
            context = {
                'course': course,
                'payment': payment,
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
                'amount': int(amount_in_paise),
                'currency': 'INR',
                'student_email': request.user.email,
                'student_name': f"{request.user.first_name} {request.user.last_name}",
            }
            return render(request, 'payments/payment_form.html', context)
        except Exception as e:
            logger.error(f"Error creating Razorpay order: {str(e)}")
            return render(request, 'payments/payment_form.html', 
                        {'error': 'Failed to initiate payment. Please try again.', 'course': course})
    
    context = {'course': course}
    return render(request, 'payments/payment_form.html', context)


@login_required
@require_POST
def confirm_payment(request):
    """Confirm payment after successful Razorpay transaction"""
    try:
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        course_id = request.POST.get('course_id')
        
        course = get_object_or_404(Course, id=course_id)
        
        # Verify signature
        signature_data = f'{razorpay_order_id}|{razorpay_payment_id}'
        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            signature_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if expected_signature != razorpay_signature:
            logger.error(f"Signature mismatch for payment {razorpay_payment_id}")
            return JsonResponse({'status': 'failed', 'error': 'Payment verification failed'}, status=400)
        
        # Get payment record
        payment = get_object_or_404(Payment, razorpay_order_id=razorpay_order_id)
        
        # Update payment status
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = 'captured'
        payment.completed_at = __import__('django.utils.timezone', fromlist=['now']).now()
        payment.save()
        
        # Create enrollment
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={'is_active': True}
        )
        
        if created:
            logger.info(f"New enrollment created: {enrollment.id}")
        
        return JsonResponse({'status': 'success', 'course_id': course.id})
    
    except Exception as e:
        logger.error(f"Error in confirm_payment: {str(e)}")
        return JsonResponse({'status': 'error', 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook(request):
    """Handle Razorpay webhook events"""
    try:
        webhook_data = json.loads(request.body)
        event = webhook_data.get('event')
        payload = webhook_data.get('payload', {})
        
        if event == 'payment.authorized':
            payment_data = payload.get('payment', {})
            razorpay_payment_id = payment_data.get('id')
            razorpay_order_id = payment_data.get('order_id')
            
            # Update payment status
            payment = Payment.objects.filter(razorpay_order_id=razorpay_order_id).first()
            if payment:
                payment.razorpay_payment_id = razorpay_payment_id
                payment.status = 'authorized'
                payment.save()
                logger.info(f"Payment authorized: {razorpay_payment_id}")
        
        elif event == 'payment.failed':
            payment_data = payload.get('payment', {})
            razorpay_order_id = payment_data.get('order_id')
            
            payment = Payment.objects.filter(razorpay_order_id=razorpay_order_id).first()
            if payment:
                payment.status = 'failed'
                payment.save()
                logger.warning(f"Payment failed: {razorpay_order_id}")
        
        elif event == 'refund.created':
            refund_data = payload.get('refund', {})
            razorpay_payment_id = refund_data.get('payment_id')
            
            payment = Payment.objects.filter(razorpay_payment_id=razorpay_payment_id).first()
            if payment:
                payment.status = 'refunded'
                payment.save()
                logger.info(f"Payment refunded: {razorpay_payment_id}")
        
        return JsonResponse({'status': 'ok'})
    
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@instructor_required
def course_payments(request, course_id):
    """View payments for a course (instructor only)"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    payments = Payment.objects.filter(course=course, status__in=['captured', 'authorized']).order_by('-created_at')
    
    total_revenue = sum(p.amount for p in payments)
    total_platform_fee = sum(p.platform_fee for p in payments)
    total_instructor_payout = sum(p.instructor_payout for p in payments)
    
    context = {
        'course': course,
        'payments': payments,
        'total_revenue': total_revenue,
        'total_platform_fee': total_platform_fee,
        'total_instructor_payout': total_instructor_payout,
    }
    return render(request, 'payments/course_payments.html', context)


instructor_required
def payouts_history(request):
    """View payout history (instructor only)"""
    payouts = payouts.objects.filter(instructor=request.user).order_by('-created_at')

    context = {
        'payouts' : payouts,
        'pending_amount' : sum(p.total_amount for p in payouts if p.status == 'pending'),
    }
    return render(request, 'payments/payout_history.html', context)


@instructor_required
@require_POST
def create_payout(request, course_id):
    """Create payout request for a course (instructor only)"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    
    # Calculate pending payouts for this course
    payments = Payment.objects.filter(
        course=course,
        status__in=['captured', 'authorized'],
        instructor=request.user
    )
    
    # Calculate total that hasn't been paid out
    total_amount = sum(p.instructor_payout for p in payments)
    
    if total_amount <= 0:
        return JsonResponse({'error': 'No pending payments'}, status=400)
    
    form = PayoutForm(request.POST)
    if form.is_valid():
        payout = form.save(commit=False)
        payout.instructor = request.user
        payout.course = course
        payout.total_amount = total_amount
        payout.save()
        
        logger.info(f"Payout created: {payout.id}")
        return JsonResponse({'status': 'success', 'payout_id': payout.id})
    
    return JsonResponse({'error': 'Invalid form'}, status=400)
