from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from accounts.decorators import instructor_required
from .models import Course, Enrollment, CourseResource, CourseRating, CourseReferral
from .forms import CourseCreationForm, CourseResourceForm, CourseRatingForm
import uuid

# Create your views here.
def home(request):
    """Home page - list all published courses that are not private, or private courses the user is enrolled in."""
    from django.db.models import Q
    
    # Base filter for published, non-suspended courses
    base_filter = Q(status='published', is_suspended=False)
    
    if request.user.is_authenticated:
        # For authenticated users: public courses OR private courses they own/enrolled in
        courses = Course.objects.filter(
            base_filter & (
                Q(is_private=False) |  # All public courses
                Q(is_private=True, instructor=request.user) |  # Courses they own
                Q(is_private=True, enrollments__student=request.user, enrollments__is_active=True)  # Private courses they're enrolled in
            )
        ).prefetch_related('instructor').distinct()
    else:
        # For guests: only public courses
        courses = Course.objects.filter(base_filter, is_private=False).prefetch_related('instructor')
    
    context = {
        'courses': courses,
    }
    return render(request, 'courses/home.html', context)


@login_required
def my_courses(request):
    """View for students to see their enrolled courses."""
    enrollments = Enrollment.objects.filter(student=request.user, is_active=True).select_related('course')
    context = {
        'enrollments': enrollments,
    }
    return render(request, 'courses/my_courses.html', context)


def course_detail(request, course_id):
    """Course detail page."""
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user has access to this course
    if not course.is_accessible_by_user(request.user):
        return redirect('home')
    
    is_enrolled = False
    user_rating = None

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists()
        user_rating = course.ratings.filter(student=request.user).first()
    
    # Get average rating
    avg_rating = get_course_average_rating(course)
    all_ratings = course.ratings.all()
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'platform_fee': course.get_platform_fee(),
        'instructor_payout': course.get_instructor_payout(),
        'avg_rating': avg_rating,
        'ratings': all_ratings,
        'user_rating': user_rating,
        'rating_form': CourseRatingForm() if is_enrolled else None,
    }
    return render(request, 'courses/course_detail.html', context)


@instructor_required
def create_course(request):
    """View for instructors to create a new course."""
    if request.method == 'POST':
        form = CourseCreationForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('courses:course_detail', course_id=course.id)
    else:
        form = CourseCreationForm()

    context = {'form': form,}
    return render(request, 'courses/create_course.html', context)


@instructor_required
def edit_course(request, course_id):
    """Edit course (instructor only)."""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST':
        form = CourseCreationForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            course = form.save(commit=False)
            # Handle privacy toggle
            is_private = request.POST.get('is_private') == 'on'
            if is_private and not course.is_private:
                # Course is being made private for the first time
                from django.utils import timezone
                course.made_private_at = timezone.now()
            course.is_private = is_private
            course.save()
            return redirect('courses:course_detail', course_id=course.id)
    else:
        form = CourseCreationForm(instance=course)

    resources = course.resources.all()
    context = {'form': form, 'course': course, 'resources': resources}
    return render(request, 'courses/edit_course.html', context)


@login_required
@require_POST
def enroll_course(request, course_id):
    """Enroll student in the course."""
    course = get_object_or_404(Course, id=course_id,)

    # Redirect to payments if course has price
    if course.price > 0:
        return redirect('payments:make_payment', course_id=course.id)
    
    # Free course - direct enrollment
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user, 
        course=course,
        defaults={'is_active': True}
    )

    if created:
        return redirect('courses:course_detail', course_id=course.id)

    return JsonResponse({'error': 'Already enrolled.'}, status=400)


@instructor_required
@require_POST
def add_resource(request, course_id):
    """Add a resource to a course."""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    
    title = request.POST.get('title')
    description = request.POST.get('description', '')
    resource_type = request.POST.get('resource_type')
    order = request.POST.get('order', 0)
    file = request.FILES.get('file')
    
    if title and resource_type and file:
        CourseResource.objects.create(
            course=course,
            title=title,
            description=description,
            resource_type=resource_type,
            file=file,
            order=int(order) if order else 0
        )
    
    return redirect('courses:edit_course', course_id=course.id)


@instructor_required
@require_POST
def delete_resource(request, resource_id):
    """Delete a resource from a course."""
    resource = get_object_or_404(CourseResource, id=resource_id)
    course_id = resource.course.id
    
    # Ensure only the course instructor can delete
    if resource.course.instructor != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    resource.delete()
    return redirect('courses:edit_course', course_id=course_id)


def search_courses(request):
    """Search courses and instructors by title, instructor name, or keyword."""
    query = request.GET.get('q', '').strip()
    courses = []
    
    if query:
        from django.db.models import Q
        
        # Search public courses by title or instructor name
        courses = Course.objects.filter(
            Q(title__icontains=query) | Q(instructor__first_name__icontains=query) | 
            Q(instructor__last_name__icontains=query) | Q(instructor__email__icontains=query),
            status='published',
            is_suspended=False
        ).exclude(is_private=True).prefetch_related('instructor').distinct()
        
        # If user is authenticated, also include private courses they're enrolled in
        if request.user.is_authenticated:
            private_enrolled = Course.objects.filter(
                Q(title__icontains=query) | Q(instructor__first_name__icontains=query) | 
                Q(instructor__last_name__icontains=query) | Q(instructor__email__icontains=query),
                status='published',
                is_private=True,
                enrollments__student=request.user,
                enrollments__is_active=True,
                is_suspended=False
            ).prefetch_related('instructor').distinct()
            
            instructor_private = Course.objects.filter(
                Q(title__icontains=query) | Q(instructor__first_name__icontains=query) | 
                Q(instructor__last_name__icontains=query) | Q(instructor__email__icontains=query),
                status='published',
                is_private=True,
                instructor=request.user,
                is_suspended=False
            ).prefetch_related('instructor').distinct()
            
            courses = courses | private_enrolled | instructor_private
    
    context = {
        'courses': courses,
        'query': query,
    }
    return render(request, 'courses/search_results.html', context)


@login_required
@require_POST
def add_rating(request, course_id):
    """Add or update a course rating."""
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user is enrolled
    if not Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists():
        return JsonResponse({'error': 'Not enrolled in this course'}, status=403)
    
    form = CourseRatingForm(request.POST)
    if form.is_valid():
        rating = form.save(commit=False)
        rating.course = course
        rating.student = request.user
        rating.save()
        return JsonResponse({'success': True, 'message': 'Rating saved successfully'})
    
    return JsonResponse({'error': form.errors}, status=400)


def get_course_average_rating(course):
    """Get average rating for a course."""
    ratings = course.ratings.all()
    if not ratings:
        return None
    return sum(r.rating for r in ratings) / len(ratings)


@login_required
def generate_referral_link(request, course_id):
    """Generate a referral link for a course. Any authenticated user can share any course."""
    course = get_object_or_404(Course, id=course_id)
    
    # Allow ANY authenticated user to generate referral links for ANY course
    # This enables students and other users to share courses in their network
    
    # Generate unique referral code
    referral_code = f"{course.id}_{request.user.id}_{str(uuid.uuid4())[:8]}"
    
    referral = CourseReferral.objects.create(
        course=course,
        referrer=request.user,  # The user generating the link (could be student, instructor, or anyone)
        referred_student=request.user,  # Placeholder, will be updated when someone uses the link
        referral_code=referral_code
    )
    
    referral_url = request.build_absolute_uri(f'/courses/course/{course_id}/?ref={referral_code}')
    
    return JsonResponse({
        'success': True,
        'referral_code': referral_code,
        'referral_url': referral_url
    })

