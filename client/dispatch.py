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
from django.conf import settings
from tv.models import Channel
import models
from tastypie.models import create_api_key

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
        ## Auto create default options to STB
        # password
        if models.SetTopBox.default.password is not None:
            passwd_config = models.SetTopBoxConfig.objects.create(
                settopbox=instance, key='global.PASSWORD',
                value=models.SetTopBox.default.password, value_type='string')
            log.debug('Nova config password=%s', passwd_config)
        # recorder
        if models.SetTopBox.default.recorder is not None:
            rec = 'disabled'
            if models.SetTopBox.default.recorder is True:
                rec = 'enable'
            rec_config = models.SetTopBoxConfig.objects.create(
                settopbox=instance, key='app/tv.TVOD_PLUGIN',
                value=rec, value_type='string')
            log.debug('Nova config recorder=%s', rec_config)
        # parental
        if models.SetTopBox.default.parental is not None:
            parental_config = models.SetTopBoxConfig.objects.create(
                settopbox=instance, key='app/tv.PARENTAL_CONTROL',
                value=models.SetTopBox.default.parental, value_type='string')
            log.debug('Nova config parental=%s', parental_config)

# app/tv.PARENTAL_CONTROL = 0,10,12,14,16,18,-1
# global.PASSWORD = 1234
# app/tv.TVOD_PLUGIN = enable/disable
# app/tv.ASPECT_RATIO = auto,stretch,16_9,4_3


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

@receiver(post_save, sender=models.SetTopBoxChannel)
def SetTopBoxChannel_post_save(sender, instance, created, **kwargs):
    if created:
        log.debug('New stb channel created=%s', instance)
        message = 'Canal adicionado=%s' % (instance.channel.name)
        instance.settopbox.reload_channels(message=message, channel=True)

@receiver(post_delete, sender=models.SetTopBoxChannel)
def SetTopBoxChannel_post_delete(sender, instance, **kwargs):
    message = 'Canal removido=%s' % (instance.channel.name)
    instance.settopbox.reload_channels(message=message, channel=True)
