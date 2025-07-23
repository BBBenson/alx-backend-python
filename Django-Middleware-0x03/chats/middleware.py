from datetime import datetime, time
from django.http import HttpResponseForbidden


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}\n"

        with open('requests.log', 'a') as log_file:
            log_file.write(log_entry)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware that only allows access between 09:00 and 17:00.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.start_time = time(9, 0, 0)   # 09:00 AM
        self.end_time = time(17, 0, 0)    # 05:00 PM

    def __call__(self, request):
        current_time = datetime.now().time()
        if not (self.start_time <= current_time <= self.end_time):
            return HttpResponseForbidden(
                "<h1>Access forbidden: Outside allowed hours (09:00 - 17:00)</h1>"
            )
        response = self.get_response(request)
        return response


class RolepermissionMiddleware:
    """
    Middleware to enforce user role permissions.
    Only users with role 'admin' or 'moderator' are allowed.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Assuming user role is stored in `user.role`
            user_role = getattr(request.user, 'role', None)
            if user_role not in ('admin', 'moderator'):
                return HttpResponseForbidden(
                    "<h1>Access forbidden: Insufficient role permissions</h1>"
                )

        response = self.get_response(request)
        return response
