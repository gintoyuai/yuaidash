# dashboard/middleware.py
from .models import Traffic

class TrafficMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/admin/'):  # avoid logging admin visits
            Traffic.objects.create(
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                path=request.path
            )
        return self.get_response(request)
