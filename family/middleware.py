from django.shortcuts import redirect


class SimpleAuthMiddleware:
    """Simple middleware to protect /app/ routes with login requirement."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Protect /app/ routes - redirect to admin login if not authenticated
        if request.path.startswith('/app/') and not request.user.is_authenticated:
            return redirect(f'/admin/login/?next={request.path}')
        
        response = self.get_response(request)
        return response