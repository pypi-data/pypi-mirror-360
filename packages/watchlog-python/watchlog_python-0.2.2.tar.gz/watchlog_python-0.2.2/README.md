# watchlog-python

A lightweight, non-blocking Python client for sending custom metrics to the [Watchlog](https://watchlog.io/) monitoring platform.

## 🚀 Installation

Install the package using pip:

```bash
pip install watchlog-python
```

## 📦 Usage

### 1. Import the Watchlog class

```python
from watchlog import Watchlog
```

### 2. Create an instance of Watchlog

```python
watchlog_instance = Watchlog()
```

### 3. Send metrics using simple method calls

```python
# Increment a counter
watchlog_instance.increment('page_views', 10)

# Decrement a counter
watchlog_instance.decrement('items_in_cart', 2)

# Set a gauge value
watchlog_instance.gauge('current_temperature', 22.5)

# Set a percentage value (0 to 100)
watchlog_instance.percentage('completion_rate', 85)

# Log system byte metric (e.g., memory usage in bytes)
watchlog_instance.systembyte('memory_usage', 1024)
```

All operations are performed **asynchronously and silently**, ensuring zero interruption to your main application.

## 🌐 Example Usage in a Django View

```python
# views.py
from django.http import HttpResponse
from watchlog import Watchlog

watchlog_instance = Watchlog()

def some_view(request):
    watchlog_instance.increment('view_hits')
    return HttpResponse("This is a view that increments a metric.")
```

## ✅ Features

- ⚡️ Non-blocking & thread-based HTTP request
- 🛡️ No logging, printing, or exception leaks
- 🔐 Safe and isolated from your main application flow
- 🧩 Easy to integrate with any Python web framework

## 📄 License

MIT License