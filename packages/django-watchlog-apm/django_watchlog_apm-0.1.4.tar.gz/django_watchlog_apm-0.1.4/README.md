# APM for Django – Watchlog Integration

🎯 Lightweight and production-safe Application Performance Monitoring (APM) middleware for Django apps, made for [Watchlog](https://watchlog.io).

Tracks route execution time, memory, status codes, and errors — and sends them periodically to your Watchlog agent in aggregated form.

---

## 🚀 Features

- 🔧 Automatic tracking of all HTTP requests
- 📊 Aggregation of metrics by route and method
- ⚠️ Optional error tracking via error handler
- 🧠 Smart batching to avoid redundant sends
- 🌐 Sends metrics over HTTP to Watchlog agent
- 🏷️ Automatically detects route pattern like `users/<int:id>/`
- 💡 Safe-by-default (never crashes your app)

---

## 📦 Installation

```bash
pip install django_watchlog_apm
```

---

## ⚙️ Usage

In your Django `settings.py`, add the middleware **after routing is resolved**, e.g.:

```python
MIDDLEWARE = [
    ...
    'django_watchlog_apm.middleware.WatchlogAPMMiddleware',
]
```

If you want to also track uncaught exceptions, add:

```python
MIDDLEWARE = [
    ...
    'django_watchlog_apm.error_handler.capture_exception',
    'django_watchlog_apm.middleware.WatchlogAPMMiddleware',
]
```

---

## 🛠️ Service Identification

You can define your service name in the `.env` or environment variables:

```env
WATCHLOG_APM_SERVICE=payments-service
```

If not defined, it falls back to:

```env
APP_NAME=django-app
```

If neither is set, the default `django-app` is used.

---

## 📤 What gets sent?

Example payload every 10 seconds:

```json
{
  "collected_at": "2025-05-18T12:00:00Z",
  "platformName": "django",
  "metrics": [
    {
      "type": "aggregated_request",
      "service": "payments-service",
      "path": "users/<int:id>/",
      "method": "GET",
      "request_count": 2,
      "error_count": 0,
      "avg_duration": 12.3,
      "max_duration": 20.4,
      "avg_memory": {
        "rss": 18432000,
        "heapUsed": 23789568,
        "heapTotal": 23789568
      }
    }
  ]
}
```

---

## 🧪 Example view to test errors

In `urls.py`:

```python
from django.urls import path
from .views import hello, fail

urlpatterns = [
    path("hello/<int:id>/", hello),
    path("fail/", fail),
]
```

In `views.py`:

```python
from django.http import JsonResponse

def hello(request, id):
    return JsonResponse({"message": f"Hello {id}"})

def fail(request):
    1 / 0  # triggers 500 error
```

---

## 📁 Recommended `.gitignore`

```gitignore
/storage/logs/apm-buffer.json
/storage/framework/cache/watchlog-apm.lock
```

---

## ✅ Notes

- Route patterns are extracted using `request.resolver_match.route`
- Middleware must be placed **after** routing to access the route object
- Metrics are batched in a local file and flushed every 10 seconds
- Errors are captured if error handler middleware is enabled

---

## 📝 License

MIT © Mohammadreza  
Built for [Watchlog.io](https://watchlog.io)
