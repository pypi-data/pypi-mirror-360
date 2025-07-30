from django.http import HttpResponse, Http404
import os

# Create your views here.
def download_log(request):
    """ View to download the log file """
    log_file = request.GET.get('log_file')

    if not log_file or not os.path.isfile(log_file):
        raise Http404("Log file not found")

    with open(log_file, 'rb') as f:
        response = HttpResponse(f.read(), content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(log_file)}'
        return response