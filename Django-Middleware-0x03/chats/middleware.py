from datetime import datetime, time
from django.http import HttpResponseForbidden
import logging

# Set up a logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    def __init__(self, get_response):
        self.get_response = get_response
        self.start_time = time(9, 0, 0)
        self.end_time = time(17, 0, 0)

    def __call__(self, request):
        current_time = datetime.now().time()
        if not (self.start_time <= current_time <= self.end_time):
            return HttpResponseForbidden("<h1>Access forbidden: Outside allowed hours (09:00 - 17:00)</h1>")
        return self.get_response(request)


class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_role = getattr(request.user, 'role', None)
            if user_role not in ('admin', 'moderator'):
                return HttpResponseForbidden("<h1>Access forbidden: Insufficient role permissions</h1>")
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """
    Middleware to detect offensive language in POST requests.
    """
    OFFENSIVE_WORDS = ['badword1', 'badword2', 'stupid', 'idiot']  # Extend this list as needed

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            for key, value in request.POST.items():
                if any(offensive in value.lower() for offensive in self.OFFENSIVE_WORDS):
                    logger.warning(f"Offensive language detected in field '{key}': {value}")
                    return HttpResponseForbidden("<h1>Access forbidden: Offensive language detected</h1>")
        return self.get_response(request)
