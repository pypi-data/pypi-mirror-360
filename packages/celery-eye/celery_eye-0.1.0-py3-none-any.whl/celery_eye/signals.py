import traceback
from celery.signals import task_postrun, task_prerun
from django.utils.timezone import now
from celery_eye.models import CeleryWorkerMetadata, CeleryWorkerLog
import socket
import os
import sys

LOG_DIR = './logs'  # Shared Docker volume
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure log directory exists


@task_prerun.connect
def log_task_prerun(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """
    Create a unique log file for each task execution before it runs.
    """
    try:
        hostname = socket.gethostname()

        # Use sender.name (task name) + task_id for log file naming
        if "watch_mongo_changes" in sender.name:
            task_name = args[1] 
        else:
            task_name = sender.name
        log_file = os.path.join(LOG_DIR, f"{task_name}-{task_id}.log")

        # Redirect stdout and stderr to the log file
        sys.stdout = open(log_file, "a")
        sys.stderr = open(log_file, "a")

        # Store metadata
        metadata, created = CeleryWorkerMetadata.objects.get_or_create(
            worker_name=f"{task_name}-{task_id}",  # Use task_name + task_id as unique worker name
            defaults={
                'hostname': hostname,
                'started_at': now(),
                'log_file': log_file
            }
        )

        print(f"[{now()}] Task {task_name} ({task_id}) will log to {log_file}")

    except Exception as e:
        print(f"Error setting up task log file: {e}")


@task_postrun.connect
def log_task_postrun(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **extra):
    """
    Log task execution details after it finishes.
    """
    try:
        task_name = sender.name
        worker_name = f"{task_name}-{task_id}"

        # Retrieve the matching worker
        worker = CeleryWorkerMetadata.objects.get(worker_name=worker_name)

        # Store log details
        exception = None
        if state == "FAILURE":
            exception = str(extra.get('exception', 'Unknown error'))
        worker_end_time = now()
        runtime = (worker_end_time - worker.started_at).total_seconds()

        CeleryWorkerLog.objects.create(
            worker=worker,
            task_name=task_name,
            status=state,
            exception=exception,
            args=args,
            result=str(retval) if retval is not None else retval,
            runtime=runtime,
            timestamp=worker_end_time
        )


        # Update worker metadata
        worker.total_tasks += 1
        worker.last_run_at = worker_end_time
        worker.save()
        
       

    except Exception as e:
        traceback.print_exc()
        print(f"Error logging Celery task: {e}")

    sys.stdout.close()
    sys.stderr.close()
