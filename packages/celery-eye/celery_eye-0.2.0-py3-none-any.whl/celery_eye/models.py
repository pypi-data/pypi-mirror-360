from django.db import models
from django.utils.timezone import now

# Create your models here.

class CeleryWorkerMetadata(models.Model):
    """Stores metadata about each Celery worker"""
    worker_name = models.CharField(max_length=255, unique=True)  # e.g., worker-ip-172-31-12-45
    hostname = models.CharField(max_length=255, blank=True, null=True)
    log_file = models.CharField(max_length=512)  # Path to the log file
    started_at = models.DateTimeField(default=now)
    last_run_at = models.DateTimeField(null=True, blank=True)
    total_tasks = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.worker_name} ({self.started_at})"


class CeleryWorkerLog(models.Model):
    """Stores logs from Celery tasks"""
    worker = models.ForeignKey(CeleryWorkerMetadata, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20)  # SUCCESS, FAILED
    exception = models.TextField(blank=True, null=True)
    args = models.JSONField(blank=True, null=True)
    result = models.JSONField(blank=True, null=True)
    runtime = models.FloatField(help_text="Execution time in seconds")
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.worker.worker_name} - {self.task_name} - {self.status}"

    class Meta:
        ordering = ['-timestamp']