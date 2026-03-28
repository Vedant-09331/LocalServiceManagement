from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

def role_required(allowed_roles=[]):
    """
    Decorator for views that checks whether a user has a particular role,
    redirecting to the home page or throwing a PermissionDenied error if necessary.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('core:login')
            if request.user.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                # User does not have the required role
                raise PermissionDenied("You do not have permission to view this page.")
        return _wrapped_view
    return decorator

def vendor_required(view_func):
    """Decorator ensuring only vendors can access the view."""
    return role_required(['vendor'])(view_func)

def customer_required(view_func):
    """Decorator ensuring only normal users can access the view."""
    return role_required(['user'])(view_func)

def admin_required(view_func):
    """Decorator ensuring only admins can access the view."""
    return role_required(['admin'])(view_func)
