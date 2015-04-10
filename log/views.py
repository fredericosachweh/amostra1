import datetime
import json

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone


@login_required
def current_task_log(request):
    TaskLog = apps.get_model('log', 'TaskLog')
    logs = TaskLog.objects.filter(is_finished=False)
    current_list = list()
    if logs:
        for log in logs:
            current_task = { 
                'name': log.get_name_display(),
                'create_at': datetime.datetime.strftime(
                timezone.localtime(log.create_at), '%d/%m/%Y %H:%I:%S'),
                'progress': "{}%".format(log.progress)
            }
            current_list.append(current_task)
                
    return HttpResponse(
        json.dumps(current_list), content_type="application/json")