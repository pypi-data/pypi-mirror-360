import threading
import urllib.parse
import urllib.request
import os
# API endpoint
is_kubernetes = os.getenv('KUBERNETES_SERVICE_HOST') is not None
URL = (
    'http://watchlog-node-agent:3774'
    if is_kubernetes
    else 'http://localhost:3774'
)

class Watchlog:
    def __init__(self):
        self.url = URL

    def send_metric(self, method, metric, value=1):
        if not isinstance(value, (int, float, complex)):
            return
        
        def _send():
            try:
                params = urllib.parse.urlencode({
                    "method": method,
                    "metric": metric,
                    "value": value
                })
                full_url = f"{self.url}?{params}"
                req = urllib.request.Request(full_url)
                urllib.request.urlopen(req, timeout=1)
            except Exception:
                # خطاها را ساکت قورت بده، بدون print یا لاگ
                pass

        # استفاده از Thread برای غیرمسدودسازی کامل
        threading.Thread(target=_send, daemon=True).start()

    def increment(self, metric, value=1):
        self.send_metric('increment', metric, value)

    def decrement(self, metric, value=1):
        self.send_metric('decrement', metric, value)

    def gauge(self, metric, value):
        self.send_metric('gauge', metric, value)

    def percentage(self, metric, value):
        if 0 <= value <= 100:
            self.send_metric('percentage', metric, value)

    def systembyte(self, metric, value):
        self.send_metric('systembyte', metric, value)
