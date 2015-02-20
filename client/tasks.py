import logging
import requests
import time

from celery import task
from decimal import Decimal as D
from .models import SetTopBox
from log.models import TaskLog
from nbridge.models import Nbridge
from django.conf import settings
server_key = settings.NBRIDGE_SERVER_KEY

log = logging.getLogger('client')

def split_pks(pks):
    limit = settings.QUERY_LIMIT
    return [pks[i:i+limit] for i in range(0,len(pks),limit)]

@task(name='reload-channels')
def reload_channels(settopboxes_pks, message, task_id, channel=False):
    splitted_pks = split_pks(settopboxes_pks) 
    task = TaskLog.objects.get(pk=task_id)
    for n, pks in enumerate(splitted_pks):
        settopboxes = SetTopBox.objects.filter(pk__in=settopboxes_pks)
        for settopbox in settopboxes:
            settopbox.reload_channels(message=message, channel=False)
        task.progress = D(n) / len(splitted_pks) * 100
        task.save()
        time.sleep(settings.TASK_INTERVAL)
    task.is_finished = True
    task.save()

@task(name='reboot-stbs')
def reboot_stbs(settopboxes_pks, task_id):
    splitted_pks = split_pks(settopboxes_pks) 
    task = TaskLog.objects.get(pk=task_id)
    for n, pks in enumerate(splitted_pks):
        print n
        settopboxes = SetTopBox.objects.filter(pk__in=pks)
        log.debug('Reboot')
        nbs = Nbridge.objects.filter(status=True)
        log.debug('NBS=%s', nbs)
        for nbridge in nbs:
            log.debug('Enviando para nb=%s', nbridge)
            url = 'http://%s/ws/reboot/' % (nbridge.server.host)
            log.debug('URL=%s', url)
            macs = []
            # mac[]=FF:21:30:70:64:33&mac[]=FF:01:67:77:21:80&mac[]=FF:32:32:26:11:21
            for settopbox in settopboxes:
                macs.append(settopbox.mac)
            data = {
                'server_key': server_key,
                'mac[]': [macs]
                }
            log.debug('Reboot=%s, macs[]=%s', url, macs)
            log.debug('DATA=%s', data)
            try:
                response = requests.post(url, timeout=10, data=data)
                log.debug('Resposta=[%s]%s', response.status_code, response.text)
            except Exception as e:
                log.error('ERROR:%s', e)
            finally:
                log.info('Finalizado o request')
            task.progress = D(n) / len(splitted_pks) * 100
            task.save()
            time.sleep(settings.TASK_INTERVAL)
    task.is_finished = True
    task.save()
