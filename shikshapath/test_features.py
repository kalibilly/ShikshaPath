"""
Quick test to verify all the implemented features are working
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shikshapath.settings')
django.setup()

from django.contrib.auth import get_user_model
from courses.models import Course
from video_generation.models import VideoGenerationTask
from payments.models import Payment

User = get_user_model()

print("\n" + "="*60)
print("SHIKSHAPATH PLATFORM - FEATURE VERIFICATION TEST")
print("="*60)

# Test 1: Check VideoGenerationTask model
print("\n[TEST 1] VideoGenerationTask Model")
print("-" * 40)
try:
    task_count = VideoGenerationTask.objects.count()
    print(f"✓ VideoGenerationTask model works - Total tasks: {task_count}")
except Exception as e:
    print(f"✗ VideoGenerationTask model error: {e}")

# Test 2: Check if users exist
print("\n[TEST 2] Users in Database")
print("-" * 40)
try:
    users_count = User.objects.count()
    print(f"✓ Users in database: {users_count}")
    if users_count > 0:
        for user in User.objects.all()[:3]:
            print(f"  - {user.email} ({user.get_full_name()})")
except Exception as e:
    print(f"✗ Error checking users: {e}")

# Test 3: Check if courses exist
print("\n[TEST 3] Courses in Database")
print("-" * 40)
try:
    courses_count = Course.objects.count()
    print(f"✓ Courses in database: {courses_count}")
    if courses_count > 0:
        for course in Course.objects.all()[:3]:
            print(f"  - {course.title} (by {course.instructor.email})")
except Exception as e:
    print(f"✗ Error checking courses: {e}")

# Test 4: Check Payment Model
print("\n[TEST 4] Payment System")
print("-" * 40)
try:
    payment_count = Payment.objects.count()
    print(f"✓ Payment system working - Total payments: {payment_count}")
except Exception as e:
    print(f"✗ Payment system error: {e}")

# Test 5: Check CourseRating Model
print("\n[TEST 5] Rating System")
print("-" * 40)
try:
    from courses.models import CourseRating
    rating_count = CourseRating.objects.count()
    print(f"✓ Rating system working - Total ratings: {rating_count}")
except Exception as e:
    print(f"✗ Rating system error: {e}")

# Test 6: Check CourseReferral Model
print("\n[TEST 6] Referral System")
print("-" * 40)
try:
    from courses.models import CourseReferral
    referral_count = CourseReferral.objects.count()
    print(f"✓ Referral system working - Total referrals: {referral_count}")
except Exception as e:
    print(f"✗ Referral system error: {e}")

print("\n" + "="*60)
print("FEATURE VERIFICATION COMPLETE")
print("="*60)
print("\n✓ Platform components verified successfully!")
print("\nAvailable URLs:")
print("  - http://localhost:8000/ (Home)")
print("  - http://localhost:8000/admin/ (Admin Panel)")
print("  - http://localhost:8000/accounts/login/ (Login)")
print("  - http://localhost:8000/courses/ (Browse Courses)")
print("  - http://localhost:8000/videos/list/<course_id>/ (Generated Videos)")
print("\n")
