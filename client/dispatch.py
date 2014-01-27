# -*- encoding:utf8 -*
'''
module: client.dispatch
@author: helber
'''
import sys
import logging
log = logging.getLogger('client')
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db import models as dbmodels
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from nbridge.models import Nbridge
from django.conf import settings
from tv.models import Channel
import models
from tastypie.models import create_api_key
import thread
import requests
server_key = settings.NBRIDGE_SERVER_KEY

if 'syncdb' not in sys.argv and 'migrate' not in sys.argv:
    dbmodels.signals.post_save.connect(create_api_key, sender=User)


@receiver(post_save, sender=models.CompanyLogo)
def CompanyLogo_post_save(sender, instance, created, **kwargs):
    log.debug('Modificando logo')


@receiver(post_save, sender=models.SetTopBox)
def SetTopBox_post_save(sender, instance, created, **kwargs):
    ## Verifica se cria canais
    if created is True:
        log.debug('New SetTopBox')
        try:
            user = User.objects.get(username='%s%s' % (
                settings.STB_USER_PREFIX, instance.serial_number))
            log.error('User existis')
        except:
            log.info('Creating new user')
            user = User.objects.create_user('%s%s' % (
                settings.STB_USER_PREFIX, instance.serial_number),
                '%s@middleware.iptvdomain' % (instance.serial_number),
                instance.serial_number)
            log.info('User:%s', user)
            user.is_active = True
        if user.groups.filter(name='settopbox').count() == 0:
            group, created = Group.objects.get_or_create(name='settopbox')
            if created is True:
                log.debug('Creating group settopbox')
            log.debug('Put new SetTopBox on group')
            user.groups.add(group)
        ## Auto cria a relação de canais de estiver configurado para tal
        if models.SetTopBox.options.auto_add_channel is True:
            log.debug('Auto creating channel for SetTopBox')
            rec = models.SetTopBox.options.auto_enable_recorder_access or False
            for channel in Channel.objects.all():
                nrel, created = models.SetTopBoxChannel.objects.get_or_create(
                    settopbox=instance, channel=channel, recorder=rec)
                if created is True:
                    log.debug('Created:%s', nrel)


@receiver(post_delete, sender=models.SetTopBox)
def SetTopBox_post_delete(sender, instance, **kwargs):
    log.debug('Deleting:%s', instance)
    users = User.objects.filter(username='%s%s' % (
        settings.STB_USER_PREFIX, instance.serial_number))
    log.debug('User to delete:%s', users)
    users.delete()


@receiver(post_save, sender=Channel)
def Channel_post_save(sender, instance, created, **kwargs):
    if models.SetTopBox.options.auto_add_channel is not True:
        return
    if created is True:
        log.debug('New Channel auto-create SetTopBox-Channel')
        for stb in models.SetTopBox.objects.all():
            rec = models.SetTopBox.options.auto_enable_recorder_access or False
            reference, created = models.SetTopBoxChannel.objects.get_or_create(
                channel=instance, settopbox=stb, recorder=rec)
            if created is True:
                log.debug('New SetTopBox-Channel:%s', reference)

def reload_channels(nbridge, settopbox, message=None, userchannel=True, channel=True):
    log.debug('Reload [%s] nbridge [%s]=%s', settopbox, nbridge, message)
    url = 'http://%s/ws/eval' % (nbridge.server.host)
    command = ''
    if userchannel:
        command += 'require(\"api/tv/userchannel\").fetch();'
    if all:
        command += 'require(\"api/tv/channel\").fetch();'
    if message:
        command += 'alert(\"%s.\");' % (message)
    log.debug('Comando=%s', command)
    try:
        response = requests.post(url, timeout=5, data={
            'server_key': server_key,
            'command': command,
            'mac': [settopbox.mac]})
        log.debug('Resposta=[%s]%s', response.status_code, response.text)
    except Exception as e:
        log.error('ERROR:%s', e)

## curl cmd
# MAC='mac[]=FF:21:30:70:64:33&mac[]=FF:01:67:77:21:80&mac[]=FF:32:32:26:11:21&mac[]=FF:32:32:26:11:20'
# CMD="command=require(\"api/tv/channel\").fetch();require(\"api/tv/userchannel\").fetch();alert(\"Atualizado.\");"
# DATA="server_key=36410c96-c157-4b2a-ac19-1a2b7365ca11&$CMD&$MAC"
# curl -X POST --data "$DATA" http://127.0.0.1/ws/eval

# resp = requests.post('http://127.0.0.1/ws/eval', data={'server_key':'36410c96-c157-4b2a-ac19-1a2b7365ca11', 'command':'require(\"api/tv/channel\").fetch();require(\"api/tv/userchannel\").fetch();alert(\"Atualizado.\");', 'mac':['FF:21:30:70:64:33', 'FF:01:67:77:21:80', 'FF:32:32:26:11:21', 'FF:32:32:26:11:20']})
@receiver(post_save, sender=models.SetTopBoxChannel)
def SetTopBoxChannel_post_save(sender, instance, created, **kwargs):
    if created:
        log.debug('New stb channel created=%s', instance)
        message = 'Canal adicionado=%s' % (instance.channel.name)
        nbs = Nbridge.objects.filter(status=True)
        for s in nbs:
            thread.start_new_thread(reload_channels, (s, instance.settopbox),
                {'channel': True, 'message': message} ) 
            #reload_channels(s, instance.settopbox, channel=True,
            #    message='Canal adicionado=%s' % (instance.channel.name))

@receiver(post_delete, sender=models.SetTopBoxChannel)
def SetTopBoxChannel_post_delete(sender, instance, **kwargs):
    nbs = Nbridge.objects.filter(status=True)
    message = 'Canal removido=%s' % (instance.channel.name)
    for s in nbs:
        thread.start_new_thread(reload_channels, (s, instance.settopbox),
            {'channel': True, 'message': message} ) 
        #reload_channels(s, instance.settopbox, channel=True,
        #        message='Canal removido=%s' % (instance.channel.name))


