from functools import wraps
from django.http import JsonResponse


def api_login_required(view_func):
    """Custom login_required decorator for API views that returns JSON 401 instead of redirect."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Authentication required',
                'message': 'You must be logged in to access this API'
            }, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view