import datetime
import json

from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.serializers.python import Serializer
from django.http import HttpResponse
from django.utils import timezone

from . import models


@login_required
def current_task_log(request):
    logs = models.TaskLog.objects.filter(is_finished=False)
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
