import time
import os
import psutil
from .collector import record

class WatchlogAPMMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.process = psutil.Process(os.getpid())

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        duration = (time.perf_counter() - start) * 1000

        mem = self.process.memory_info()

        # 📌 گرفتن مسیر route از resolver_match (نه فقط path فیزیکی)
        try:
            route_path = request.resolver_match.route
        except AttributeError:
            route_path = getattr(request, 'path', 'unknown')

        record({
            "type": "request",
            "service": os.getenv("WATCHLOG_APM_SERVICE") or os.getenv("APP_NAME", "django-app"),
            "path": route_path,
            "method": getattr(request, 'method', 'UNKNOWN'),
            "statusCode": getattr(response, 'status_code', 0),
            "duration": round(duration, 2),
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "memory": {
                "rss": mem.rss,
                "heapUsed": mem.vms,
                "heapTotal": mem.vms
            }
        })

        return response
