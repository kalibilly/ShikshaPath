from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.db import models
from accounts.models import AuditLog, CustomUser
from accounts.decorators import admin_required
from courses.models import Course, Enrollment
from payments.models import Payment, Payout
from django.utils import timezone
import csv
import json
from datetime import timedelta

# Create your views here.
@admin_required
def admin_dashboard(request):
    """Admin dashboard with key statistics."""
    # User starts
    total_users = CustomUser.objects.count()
    students = CustomUser.objects.filter(role='student').count()
    instructors = CustomUser.objects.filter(role='instructor').count()
    suspended_users = CustomUser.objects.filter(is_suspended=True).count()

    # Course stats
    total_courses = Course.objects.count()
    published_courses = Course.objects.filter(status='published').count()
    flagged_courses = Course.objects.filter(is_flagged=True).count()

    # Payment stats
    total_revenue = sum(p.amount for p in Payment.objects.filter(status='completed'))
    platform_fees = sum(p.platform_fee for p in Payment.objects.filter(status='completed'))
    pending_payouts = sum(p.amount for p in Payout.objects.filter(status='pending'))

    # Recent activity
    recent_users = CustomUser.objects.all().order_by('-created_at')[:5]
    recent_payments = Payment.objects.filter(status='completed').order_by('-created_at')[:5]
    recent_logs = AuditLog.objects.all().order_by('-timestamp')[:10]

    context = {
        'total_users': total_users,
        'students': students,
        'instructors': instructors,
        'suspended_users': suspended_users,
        'total_courses': total_courses,
        'published_courses': published_courses,
        'flagged_courses': flagged_courses,
        'total_revenue': total_revenue,
        'platform_fees': platform_fees,
        'pending_payouts': pending_payouts,
        'recent_users': recent_users,
        'recent_payments': recent_payments,
        'recent_logs': recent_logs,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def admin_users(request):
    """Admin user management."""
    users = CustomUser.objects.all().order_by('-created_at')
    role_filter = request.GET.get('role')
    search_query = request.GET.get('q')

    if role_filter:
        users = users.filter(role=role_filter)
    if search_query:
        users = users.filter(email__icontains=search_query) | users.filter(first_name__icontains=search_query)

    context = {
        'users': users,
        'role_filter': role_filter,
        'search_query': search_query
    }
    return render(request, 'admin_panel/users.html', context)


@admin_required
def admin_user_detail(request, user_id):
    """Admin user detail view."""
    user = get_object_or_404(CustomUser, id=user_id)
    courses = user.courses.all() if user.role == 'instructor' else None
    enrollments = user.enrollments.all() if user.role == 'student' else None
    payments = Payment.objects.filter(student=user) if user.role == 'student' else Payment.objects.filter(instructor=user)
    audit_logs = AuditLog.objects.filter(target_user=user).order_by('-timestamp')[:20]

    context = {
        'user': user,
        'courses': courses,
        'enrollments': enrollments,
        'payments': payments,
        'audit_logs': audit_logs,
    }
    return render(request, 'admin_panel/user_detail.html', context)


@admin_required
@require_POST
def admin_user_action(request, user_id):
    """Perform actions on a user: suspend, unsuspend, delete."""
    user = get_object_or_404(CustomUser, id=user_id)
    action = request.POST.get('action')
    reason = request.POST.get('reason', '')

    actor_email = request.user.email

    if action == 'suspend':
        user.suspend()
        AuditLog.objects.create(
            actor=request.user,
            actor_email=actor_email,
            action='user_suspended',
            target_user=user,
            details={'reason': reason},
        )
    elif action == 'activate':
        user.is_suspended = False
        user.save()
        AuditLog.objects.create(
            actor=request.user,
            actor_email=actor_email,
            action='user_activated',
            target_user=user,
        )
    elif action == 'delete':
        username = user.username
        user.delete()
        AuditLog.objects.create(
            actor=request.user,
            actor_email=actor_email,
            action='user_deleted',
            details={'username': username, 'reason': reason},
        )
        return JsonResponse({'status': 'success', 'redirect': '/admin-panel/users/'})

    return JsonResponse({'status': 'success'})


@admin_required
def admin_courses(request):
    """Admin course management."""
    courses = Course.objects.all().order_by('-created_at').select_related('instructor')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('q')

    if status_filter:
        courses = courses.filter(status=status_filter)
    if search_query:
        courses = courses.filter(title__icontains=search_query) | courses.filter(description__icontains=search_query)

    context = {
        'courses': courses,
        'status_filter': status_filter,
        'search_query': search_query
    }
    return render(request, 'admin_panel/courses.html', context)


@admin_required
def admin_course_detail(request, course_id):
    """Admin course detail view."""
    course = get_object_or_404(Course, id=course_id)
    videos = course.videos.all()
    enrollments = course.enrollments.all()
    payments = course.payments.filter(status='completed')

    context = {
        'course': course,
        'videos': videos,
        'enrollments': enrollments,
        'payments': payments,
        'enrollment_count': enrollments.count(),
        'revenue': sum(p.amount for p in payments),
    }
    return render(request, 'admin_panel/course_detail.html', context)


@admin_required
@require_POST
def admin_course_action(request, course_id):
    """Admin course actions: flag, suspend, etc."""
    course = get_object_or_404(Course, id=course_id)
    action = request.POST.get('action')
    reason = request.POST.get('reason', '')

    if action == 'flag':
        course.is_flagged = True
        course.flag_reason = reason
        course.save()
        AuditLog.objects.create(
            actor=request.user,
            actor_email=request.user.email,
            action='course_flagged',
            target_course=course,
            details={'reason': reason},
        )
    elif action == 'unflag':
        course.is_flagged = False
        course.flag_reason = None
        course.save()
        AuditLog.objects.create(
            actor=request.user,
            actor_email=request.user.email,
            action='course_unflagged',
            target_course=course,
        )
    elif action == 'suspend':
        course.is_suspended = True
        course.suspend_reason = reason
        course.save()
        AuditLog.objects.create(
            actor=request.user,
            actor_email=request.user.email,
            action='course_suspended',
            target_course=course,
            details={'reason': reason},
        )
    elif action == 'unsuspend':
        course.is_suspended = False
        course.suspend_reason = None
        course.save()
        AuditLog.objects.create(
            actor=request.user,
            actor_email=request.user.email,
            action='course_unsuspended',
            target_course=course,
        )

    return JsonResponse({'status': 'success'})


@admin_required
def admin_payments(request):
    """Admin payments analytics"""
    payments = Payment.objects.filter(status='completed').select_related('student', 'instructor', 'course')

    total_revenue = sum(p.amount for p in payments)
    total_platform_fees = sum(p.platform_fee for p in payments)
    total_instructor_payout = sum(p.instructor_payout for p in payments)

    # Top courses
    top_courses = Course.objects.annotate(
        revenue=models.Sum('payments__amount', filter=models.Q(payments__status='completed'))
    ).order_by('-revenue')[:5]

    # Top instructors
    top_instructors = CustomUser.objects.filter(role='instructor').annotate(
        revenue=models.Sum('payments__amount', filter=models.Q(payments__status='completed'))
    ).order_by('-revenue')[:5]

    # Recent payments
    recent_payments = payments.order_by('-created_at')[:10]

    context = {
        'total_revenue': round(total_revenue, 2),
        'total_platform_fees': round(total_platform_fees, 2),
        'total_instructor_payout': round(total_instructor_payout, 2),
        'top_courses': top_courses,
        'top_instructors': top_instructors,
        'recent_payments': recent_payments,
    }
    return render(request, 'admin_panel/payments.html', context)


@admin_required
def admin_payments_export(request):
    """Export payments data as CSV."""
    payments = Payment.objects.filter(status='completed').values(
        'id', 'student__email', 'instructor__email', 'course__title',
        'amount', 'platform_fee', 'instructor_payout', 'created_at'
    )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'

    writer = csv.DictWriter(response, fieldnames=[
        'id', 'student__email', 'instructor__email', 'course__title',
        'amount', 'platform_fee', 'instructor_payout', 'created_at'
    ])
    writer.writeheader()
    for payment in payments:
        writer.writerow(payment)

    return response


@admin_required
def admin_audit_log(request):
    """View audit logs"""
    logs = AuditLog.objects.all().order_by('-timestamp')
    
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    context = {
        'logs': logs,
        'action_filter': action_filter,
    }
    return render(request, 'admin_panel/audit_log.html', context)


@admin_required
def admin_audit_export(request):
    """Export audit logs as CSV or JSON"""
    logs = AuditLog.objects.all().order_by('-timestamp')
    export_format = request.GET.get('format', 'csv')
    
    if export_format == 'json':
        data = [{
            'id': log.id,
            'action': log.action,
            'actor_email': log.actor_email,
            'target_user_email': log.target_user.email if log.target_user else None,
            'target_course': log.target_course.title if log.target_course else None,
            'timestamp': log.timestamp.isoformat(),
            'details': log.details,
        } for log in logs]
        
        response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="audit_logs.json"'
        return response
    
    # CSV format
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
    
    writer = csv.DictWriter(response, fieldnames=[
        'id', 'action', 'actor_email', 'target_user_email', 'target_course', 'timestamp'
    ])
    writer.writeheader()
    for log in logs:
        writer.writerow({
            'id': log.id,
            'action': log.action,
            'actor_email': log.actor_email,
            'target_user_email': log.target_user.email if log.target_user else '',
            'target_course': log.target_course.title if log.target_course else '',
            'timestamp': log.timestamp,
        })
    
    return response
