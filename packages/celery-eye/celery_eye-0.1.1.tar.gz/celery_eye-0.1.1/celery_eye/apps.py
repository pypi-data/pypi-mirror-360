from django.apps import AppConfig

class CeleryEyeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'celery_eye'
    verbose_name = "Celery Eye"

    def ready(self):
        import celery_eye.signals  # Ensure signals are imported

    