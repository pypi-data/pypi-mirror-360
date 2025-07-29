# django_watchlog_apm/sender.py
import http.client
import json
import threading
import time
from urllib.parse import urlparse
from .collector import flush
import os

is_kubernetes = os.getenv('KUBERNETES_SERVICE_HOST') is not None
AGENT_URL = (
    'http://watchlog-node-agent:3774/apm'
    if is_kubernetes
    else 'http://localhost:3774/apm'
)

def _send(data):
    try:
        if not data:
            return

        parsed = urlparse(AGENT_URL)
        body = json.dumps(
            {
                "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "platformName": "django",
                "metrics": data,
            }
        )

        conn = http.client.HTTPConnection(parsed.hostname, parsed.port or 80, timeout=3)
        conn.request(
            "POST",
            parsed.path or "/",
            body,
            {"Content-Type": "application/json", "Content-Length": str(len(body))},
        )
        conn.getresponse()
        conn.close()
    except Exception:
        pass  # مقاوم در برابر خطا


def start(interval=10):
    def loop():
        while True:
            try:
                data = flush()
                _send(data)
            except:
                pass
            time.sleep(max(10, interval))

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
