from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def student_required(view_func):
    """
    Decorator that checks if the logged-in user is a student.
    Redirects administrators to the admin dashboard.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Superusers and staff shouldn't be trapped in student dashboard
        is_admin = request.user.is_staff or request.user.is_superuser
        if hasattr(request.user, 'profile') and request.user.profile.is_administrator:
            is_admin = True

        if is_admin:
            messages.info(request, "Administrators are directed to the Admin Dashboard.")
            return redirect('admin_dashboard')

        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    """
    Decorator that checks if the logged-in user is an administrator.
    Redirects students to their student dashboard.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        is_admin = request.user.is_staff or request.user.is_superuser
        if hasattr(request.user, 'profile') and request.user.profile.is_administrator:
            is_admin = True

        if not is_admin:
            messages.error(request, "Access denied. Administrator privileges are required to access this page.")
            return redirect('student_dashboard')

        return view_func(request, *args, **kwargs)
    return _wrapped_view
