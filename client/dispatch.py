# -*- encoding:utf8 -*
'''
module: client.dispatch
@author: helber
'''
import logging
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from tastypie.models import create_api_key
from django.db import models as dbmodels
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.conf import settings
from tv.models import Channel
import models

dbmodels.signals.post_save.connect(create_api_key, sender=User)


@receiver(post_save, sender=models.CompanyLogo)
def CompanyLogo_post_save(sender, instance, created, **kwargs):
    log = logging.getLogger('client')
    log.debug('Modificando logo')


@receiver(post_save, sender=models.SetTopBox)
def SetTopBox_post_save(sender, instance, created, **kwargs):
    log = logging.getLogger('client')
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
    log = logging.getLogger('client')
    log.debug('Deleting:%s', instance)
    users = User.objects.filter(username='%s%s' % (
        settings.STB_USER_PREFIX, instance.serial_number))
    log.debug('User to delete:%s', users)
    users.delete()


@receiver(post_save, sender=Channel)
def Channel_post_save(sender, instance, created, **kwargs):
    if models.SetTopBox.options.auto_add_channel is not True:
        return
    log = logging.getLogger('client')
    if created is True:
        log.debug('New Channel auto-create SetTopBox-Channel')
        for stb in models.SetTopBox.objects.all():
            reference, created = models.SetTopBoxChannel.objects.get_or_create(
                channel=instance, settopbox=stb)
            if created is True:
                log.debug('New SetTopBox-Channel:%s', reference)
