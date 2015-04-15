# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import datetime
import json
import logging

from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse
from django.utils import timezone

from . import models

def create_cache_log(task_id, log_id):
    cache.set('task_log-{}'.format(log_id), task_id)


def monitoring_task_ok(task_log):
    log = logging.getLogger('celery')
    task_id = cache.get('task_log-{}'.format(task_log.id))
    print(task_id)
    if task_id:
        state = AsyncResult(task_id).state
        if not state in ['STARTED', 'PENDING']:
            task_log.is_finished = True
            task_log.save()
            log.error('Task {} travou com status {} e '
                      'foi finalizada manualmente.'.format(task_id, state))
            return False
        return True
    else:
        task_log.is_finished = True
        task_log.save()
        log.error('Task {} se perdeu no celery e não concluiu.'.format(task_log.id))
        return False


@login_required
def current_task_log(request):
    logs = models.TaskLog.objects.filter(is_finished=False).order_by('id')
    current_list = list()
    if logs:
        for log in logs:
            if monitoring_task_ok(log):
                current_task = {
                    'name': log.get_name_display(),
                    'create_at': datetime.datetime.strftime(
                    timezone.localtime(log.create_at), '%d/%m/%Y %H:%I:%S'),
                    'progress': "{}%".format(log.progress)
                }
                current_list.append(current_task)
                
    return HttpResponse(
        json.dumps(current_list), content_type="application/json")
