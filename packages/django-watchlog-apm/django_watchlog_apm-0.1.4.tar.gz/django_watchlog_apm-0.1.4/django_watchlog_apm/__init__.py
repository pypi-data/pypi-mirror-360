# django_watchlog_apm/__init__.py
from .middleware import WatchlogAPMMiddleware
from .sender import start as start_sending
