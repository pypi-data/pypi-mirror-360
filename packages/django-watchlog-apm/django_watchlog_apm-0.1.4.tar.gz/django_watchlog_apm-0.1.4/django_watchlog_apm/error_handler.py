# django_watchlog_apm/error_handler.py
from .collector import record
import time


def capture_exception(get_response):
    def middleware(request):
        try:
            return get_response(request)
        except Exception as e:
            record(
                {
                    "type": "error",
                    "service": "django-app",
                    "path": request.path,
                    "method": request.method,
                    "message": str(e),
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
            )
            raise

    return middleware
