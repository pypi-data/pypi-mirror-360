from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from celery_eye.models import CeleryWorkerLog, CeleryWorkerMetadata





@admin.register(CeleryWorkerLog)
class CeleryWorkerLogAdmin(admin.ModelAdmin):
    list_display = ('worker', 'task_name', 'status', 'runtime', 'timestamp')
    search_fields = ('worker__worker_name', 'task_name', 'status')
    list_filter = ('status', 'timestamp', 'worker')
    ordering = ('-timestamp',)
    readonly_fields = ('worker', 'task_name', 'status', 'exception', 'args', 'result', 'runtime', 'timestamp')



# Helper function to read the log content
def read_log_file(log_file):
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading log file: {str(e)}"
    
@admin.register(CeleryWorkerMetadata)
class CeleryWorkerMetadataAdmin(admin.ModelAdmin):
    list_display = ('worker_name', 'hostname', 'started_at', 'last_run_at', 'total_tasks', 'log_file_link')
    readonly_fields = ('worker_name','hostname', 'started_at', 'last_run_at', 'total_tasks', 'log_file', 'view_log_file', 'log_file_link')

    def view_log_file(self, obj):
        """ Display the log content in the admin panel """
        if obj.log_file:
            content = read_log_file(obj.log_file)
            
            # Display the content in a preformatted block
            return format_html(
                '<div style="white-space: pre; background: #f5f5f5; padding: 10px; border: 1px solid #ccc; '
                'max-height: 500px; overflow: auto;">{}</div>',
                mark_safe(content)
            )
        return "No log file available"

    view_log_file.short_description = "Log File Content"

    def log_file_link(self, obj):
        """ Add a link to download the log file """
        if obj.log_file:
            return format_html(
                '<a href="/download-log/?log_file={}" target="_blank">Download Log</a>',
                obj.log_file
            )
        return "No log file"

    log_file_link.short_description = "Download Log"
