import logging
import requests
import time

from celery import task
from decimal import Decimal as D

from django.conf import settings
from .models import SetTopBox, SetTopBoxChannel
from log.models import TaskLog
from nbridge.models import Nbridge
server_key = settings.NBRIDGE_SERVER_KEY

log = logging.getLogger('celery')


def split_pks(pks):
    limit = settings.QUERY_LIMIT
    return [pks[i:i + limit] for i in range(0, len(pks), limit)]


@task(name='reload-channels')
def reload_channels(settopboxes_pks, message, task_id, channel=False):
    splitted_pks = split_pks(settopboxes_pks)
    nstbs = len(settopboxes_pks)
    log.debug('Reload queue to %s STBs', nstbs)
    task_log = TaskLog.objects.get(pk=task_id)
    i = 0
    for n, pks in enumerate(splitted_pks):
        settopboxes = SetTopBox.objects.filter(pk__in=pks)
        for settopbox in settopboxes:
            i += 1
            log.debug('Reload:%s', settopbox)
            settopbox.reload_channels(message=message, channel=False)
            task_log.progress = D(i) / nstbs * 100
            task_log.save()
        if nstbs > settings.QUERY_LIMIT:
            time.sleep(settings.TASK_INTERVAL)
    task_log.is_finished = True
    task_log.progress = 100
    task_log.save()
    log.debug('Reload queue Finished:%s', task_log)


@task(name='reload-frontend-stbs')
def reload_frontend_stbs(settopboxes_pks, task_id):
    splitted_pks = split_pks(settopboxes_pks)
    nstbs = len(settopboxes_pks)
    log.debug('Reload frontend to %s STBs', nstbs)
    task_log = TaskLog.objects.get(pk=task_id)
    i = 0
    for n, pks in enumerate(splitted_pks):
        settopboxes = SetTopBox.objects.filter(pk__in=pks)
        for settopbox in settopboxes:
            i += 1
            settopbox.reload_frontend_stb()
            task_log.progress = D(i) / nstbs * 100
            task_log.save()
        if nstbs > settings.QUERY_LIMIT:
            time.sleep(settings.TASK_INTERVAL)
    task_log.is_finished = True
    task_log.progress = 100
    task_log.save()
    log.debug('Reload frontend queue Finished:%s', task_log)


@task(name='reboot-stbs')
def reboot_stbs(settopboxes_pks, task_id):
    splitted_pks = split_pks(settopboxes_pks)
    nstbs = len(settopboxes_pks)
    log.debug('Reboot %s STBs', nstbs)
    task_log = TaskLog.objects.get(pk=task_id)
    i = 0
    for n, pks in enumerate(splitted_pks):
        settopboxes = SetTopBox.objects.filter(pk__in=pks)
        nbs = Nbridge.objects.filter(status=True)
        log.debug('NBS=%s', nbs)
        for nbridge in nbs:
            log.debug('Enviando para nb=%s', nbridge)
            url = 'http://%s:%s/reboot/' % (
                nbridge.server.host, nbridge.nbridge_port
            )
            log.debug('URL=%s', url)
            macs = []
            # mac[]=FF:21:30:70:64:33&mac[]=FF:01:67:77:21:80&mac[]=FF:32:32:26:11:21
            for settopbox in settopboxes:
                i += 1
                macs.append(settopbox.mac)
                task_log.progress = D(i) / nstbs * 100
                task_log.save()
            data = {
                'server_key': server_key,
                'mac[]': [macs]
            }
            log.debug('Reboot=%s, macs[]=%s', url, macs)
            log.debug('DATA=%s', data)
            try:
                response = requests.post(url, timeout=10, data=data)
                log.debug(
                    'Resposta=[%s]%s', response.status_code, response.text
                )
            except Exception as e:
                log.error('ERROR:%s', e)
            finally:
                log.info('Finalizado o request')
            time.sleep(settings.TASK_INTERVAL)
            if nstbs > settings.QUERY_LIMIT:
                time.sleep(settings.TASK_INTERVAL)
    task_log.is_finished = True
    task_log.progress = 100
    task_log.save()
    log.debug('Reboot stbs queue Finished:%s', task_log)


@task(name='accept-recorder')
def accept_recorder(settopboxes_pks, message, task_id, channel=False):
    task_log = TaskLog.objects.get(pk=task_id)
    nstbs = len(settopboxes_pks)
    log.debug('Accept recorder to %s STBs', nstbs)
    settopboxes = SetTopBoxChannel.objects.filter(
        settopbox__id__in=settopboxes_pks, recorder=False)
    for i, settopbox in enumerate(settopboxes):
        settopbox.recorder=True
        settopbox.save()
        task_log.progress = D(i) / len(nstbs) * 100
        task_log.save()
    task_log.is_finished = True
    task_log.save()
    log.debug('Accept recorder queue Finished:%s', task_log)


@task(name='refuse-recorder')
def refuse_recorder(settopboxes_pks, message, task_id, channel=False):
    task_log = TaskLog.objects.get(pk=task_id)
    nstbs = len(settopboxes_pks)
    log.debug('Refuse recorder to %s STBs', nstbs)
    settopboxes = SetTopBoxChannel.objects.filter(
        settopbox__id__in=settopboxes_pks, recorder=True)
    for i, settopbox in enumerate(settopboxes):
        settopbox.recorder = False
        settopbox.save()
        task_log.progress = D(i) / len(nstbs) * 100
        task_log.save()
    task_log.is_finished = True
    task_log.save()
    log.debug('Refuse recorder queue Finished:%s', task_log)

