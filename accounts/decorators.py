from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from functools import wraps


def role_required(roles=[]):
    """
    Decorator to check if user has required role(s).
    Usage: @role_required('admin') or @role_required(['admin', 'instructor'])
    """
    if isinstance(roles, str):
        roles = [roles]

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator for admin-only views"""
    return role_required('admin')(view_func)


def instructor_required(view_func):
    """Decorator for instructor-only views"""
    return role_required('instructor')(view_func)


def student_required(view_func):
    """Decorator for student-only views"""
    return role_required('student')(view_func)

