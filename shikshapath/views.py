from django.http import HttpResponse
from django.shortcuts import render

# Accounts 
from accounts.views import (RegisterView, CustomLoginView, CustomLogoutView, Profile_View, profile_edit_view,)

# Courses
from courses.views import (home, my_courses, course_detail, create_course, edit_course, enroll_course,)

# Videos
from videos.views import (upload_video, watch_video, stream_video, save_progress,)

# Payments
from payments.views import (make_payment, confirm_payment, payment_webhook, course_payments, payouts_history, create_payout,)

# Admin Panel
from admin_panel.views import (admin_dashboard, admin_users, admin_user_detail, admin_user_action, admin_courses, admin_course_detail, admin_course_action, admin_payments, admin_payments_export, admin_audit_log, admin_audit_export,)

def index(request):
    return render(request, 'courses/home.html')

# Public API exported by this module
__all__ = [
    # project index
    'index',

    # Accounts
    'RegisterView',
    'CustomLoginView',
    'CustomLogoutView',
    'Profile_View',
    'profile_edit_view',

    # Courses
    'home',
    'my_courses',
    'course_detail',
    'create_course',
    'edit_course',
    'enroll_course',

    # Videos
    'upload_video',
    'watch_video',
    'stream_video',
    'save_progress',

    # Payments
    'make_payment',
    'confirm_payment',
    'payment_webhook',
    'course_payments',
    'payouts_history',
    'create_payout',

    # Admin Panel
    'admin_dashboard',
    'admin_users',
    'admin_user_detail',
    'admin_user_action',
    'admin_courses',
    'admin_course_detail',
    'admin_course_action',
    'admin_payments',
    'admin_payments_export',
    'admin_audit_log',
    'admin_audit_export',
]

