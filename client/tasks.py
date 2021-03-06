import logging
import requests
import time

from celery import task
from decimal import Decimal as D
from django.apps import apps
from django.conf import settings
server_key = settings.NBRIDGE_SERVER_KEY

log = logging.getLogger('celery')


def split_pks(pks):
    limit = settings.QUERY_LIMIT
    return [pks[i:i + limit] for i in range(0, len(pks), limit)]


@task(name='stbs-update-plans')
def stbs_update_plans(stbs_pks=[]):

    SetTopBox = apps.get_model('client', 'SetTopBox')
    Plan = apps.get_model('client', 'Plan')
    plans = Plan.objects.all()
    if stbs_pks:
        settopboxes = SetTopBox.objects.filter(id__in=stbs_pks)
    else:
        settopboxes = SetTopBox.objects.all()
    for plan in plans:
        stbs_plan = list()
        plan_channels_pk = plan.channels_pks()
        for stb in settopboxes:
            for p_channel in plan_channels_pk:
                if p_channel in stb.channels_pks():
                    stbs_plan.append(stb.pk)
                    settopboxes = settopboxes.exclude(pk=stb.pk)
        if stbs_plan:
            SetTopBox.objects.filter(pk__in=stbs_plan).update(plan=plan)
    if settopboxes:
        settopboxes.exclude(plan=None).update(plan=None)


@task(name='reload-channels')
def reload_channels(settopboxes_pks, message, task_id, channel=False):
    TaskLog = apps.get_model('log', 'TaskLog')
    SetTopBox = apps.get_model('client', 'SetTopBox')
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
    TaskLog = apps.get_model('log', 'TaskLog')
    SetTopBox = apps.get_model('client', 'SetTopBox')
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
    TaskLog = apps.get_model('log', 'TaskLog')
    SetTopBox = apps.get_model('client', 'SetTopBox')
    Nbridge = apps.get_model('nbridge', 'Nbridge')
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
    TaskLog = apps.get_model('log', 'TaskLog')
    SetTopBoxChannel = apps.get_model('client', 'SetTopBoxChannel')
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
    TaskLog = apps.get_model('log', 'TaskLog')
    SetTopBoxChannel = apps.get_model('client', 'SetTopBoxChannel')
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

