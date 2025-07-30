# Celery Eye

**Celery Eye** is a Django app that logs and displays **Celery task execution** details in the Django **Admin panel**. It enables developers and operators to monitor task history, status, and performance directly from the web UI.

---

## 🚀 Features

- Logs all executed Celery tasks in real-time
- View task name, status, start time, end time, and more
- Admin interface to search, filter, and debug tasks
- Lightweight and easy to integrate
- Works with Redis and Celery 5+

---

## 📦 Installation

```bash
pip install celery-eye
```

---

## 🛠️ Prerequisites

Before installing `celery-eye`, ensure your Django project is already configured with **Celery** and **Redis**.

---

## 🔧 Project Setup

### 1. Configure `celery.py`

Create a `celery.py` file in your main Django project folder (same level as `settings.py`):

```python
# myproject/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### 2. Update `__init__.py` to initialize Celery

```python
# myproject/__init__.py
from .celery import app as celery_app

__all__ = ['celery_app']
```

---

## ⚙️ `settings.py` Configuration

Add the following Celery and Redis configuration in your `settings.py`:

```python
import os

# Celery Configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "UTC")  # or your desired timezone
CELERY_LOG_DIR = BASE_DIR / "logs"  # or any path like "/var/logs/celery_eye/ or your path mount in your docker volumes"

```

Make sure you have **Redis running** locally or remotely.

---

## 🧩 Django Integration

### 1. Add `celery_eye` to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    ...
    'celery_eye',
]
```

### 2. Run migrations

```bash
python manage.py migrate
```

### 3. Create a superuser (if you haven't)

```bash
python manage.py createsuperuser
```

### 4. Start your services

Make sure your services are running:

```bash
# Run Redis
redis-server

# Run Celery Worker (in your Django root directory)
celery -A myproject worker --loglevel=info

# Run Django server
python manage.py runserver
```

You should now be able to:

- See Celery task execution logs in the Django Admin
- Filter/search by status, task name, and timestamps

---

## 🧪 Example Task

```python
# any_app/tasks.py
from celery import shared_task

@shared_task
def test_task(x, y):
    return x + y
```

Trigger in a Django shell:

```bash
python manage.py shell
```

```python
from any_app.tasks import test_task
test_task.delay(5, 7)
```

---

## 🐳 Optional: Redis with Docker

You can spin up Redis with Docker:

```bash
docker run -d -p 6379:6379 redis
```

---

## 🤝 Contributing

Pull requests, issues, and feature suggestions are welcome!

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for more details.
