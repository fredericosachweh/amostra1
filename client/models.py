# -*- encoding:utf-8 -*-

import logging

from django.db import models
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from tv.models import Channel

import dbsettings


class SetTopBoxOptions(dbsettings.Group):
    auto_create = dbsettings.BooleanValue(
        _(u'Auto criação de settopbox no login'), default=False)
    auto_add_channel = dbsettings.BooleanValue(
        _(u'Cria automaticamente o vinculo entre settopbox e canal'),
        default=False
        )
    use_mac_as_serial = dbsettings.BooleanValue(
        _(u'Caso não seja fornecido via post, utiliza o MAC como serial'),
        default=True
        )


class SetTopBox(models.Model):
    u'Class to authenticate and manipulate IPTV client - SetTopBox'

    serial_number = models.CharField(_(u'Número serial'), max_length=255,
        help_text=_(u'Número serial do SetTopBox'), unique=True)
    mac = models.CharField(_(u'Endereço MAC'), max_length=255,
        help_text=_(u'Endereço MAC do SetTopBox'), unique=True)
    options = SetTopBoxOptions(u'Opções do SetTopBox')

    class Meta:
        verbose_name = _(u'SetTopBox')
        verbose_name_plural = _(u'SetTopBoxes')

    def __unicode__(self):
        return u'serial=%s,mac=%s' % (self.serial_number, self.mac)

    def get_user(self):
        return User.objects.get(username=self.serial_number)


@receiver(post_save, sender=SetTopBox)
def SetTopBox_post_save(sender, instance, created, **kwargs):
    log = logging.getLogger('client')
    ## Verifica se cria canais
    if created is True:
        log.debug('New SetTopBox')
        try:
            user = User.objects.get(username=instance.serial_number)
            log.debug('User existis')
        except:
            log.debug('Creating new user')
            user = User.objects.create_user(instance.serial_number,
                '%s@middleware.iptvdomain' % (instance.serial_number),
                instance.serial_number)
            user.is_active = True
        if user.groups.filter(name='settopbox').count() == 0:
            group, created = Group.objects.get_or_create(name='settopbox')
            if created is True:
                log.debug('Creating group settopbox')
            log.debug('Put new SetTopBox on group')
            user.groups.add(group)
        ## Auto cria a relação de canais de estiver configurado para tal
        if SetTopBox.options.auto_add_channel is True:
            log.debug('Auto creating channel for SetTopBox')
            for channel in Channel.objects.all():
                nrel, created = SetTopBoxChannel.objects.get_or_create(
                    settopbox=instance, channel=channel)
                if created is True:
                    log.debug('Created:%s', nrel)


@receiver(post_delete, sender=SetTopBox)
def SetTopBox_post_delete(sender, instance, **kwargs):
    log = logging.getLogger('client')
    log.debug('Deleting:%s', instance)
    users = User.objects.filter(username=instance.serial_number)
    log.debug('User to delete:%s', users)
    users.delete()


class SetTopBoxParameter(models.Model):
    u'Class to store key -> values of SetTopBox'

    key = models.CharField(_(u'Chave'), max_length=250,
        help_text=_(u'Chave do parametro. Ex. MACADDR'), db_index=True)
    value = models.CharField(_(u'Valor'), max_length=250,
        help_text=_(u'Valor do parametro. Ex. 00:00:00:00:00'), db_index=True)
    settopbox = models.ForeignKey(SetTopBox, db_index=True)

    class Meta:
        verbose_name = _(u'Parametro')
        verbose_name_plural = _(u'Parametros')
        unique_together = (('key', 'value', 'settopbox'),)

    def __unicode__(self):
        return u'%s {%s=%s}' % (self.settopbox, self.key, self.value)


class SetTopBoxChannel(models.Model):
    u'Class to link access permission to stb on tv.channel'

    settopbox = models.ForeignKey(SetTopBox, db_index=True)
    channel = models.ForeignKey(Channel, db_index=True)

    class Meta:
        unique_together = (('settopbox', 'channel',),)

    def __unicode__(self):
        return u'Channel:%s+SetTopBox:%s' % (self.channel, self.settopbox)


@receiver(post_save, sender=Channel)
def Channel_post_save(sender, instance, created, **kwargs):
    if SetTopBox.options.auto_add_channel is not True:
        return
    log = logging.getLogger('client')
    if created is True:
        log.debug('New Channel auto-create SetTopBox-Channel')
        for stb in SetTopBox.objects.all():
            reference, created = SetTopBoxChannel.objects.get_or_create(
                channel=instance, settopbox=stb)
            if created is True:
                log.debug('New SetTopBox-Channel:%s', reference)


class SetTopBoxConfig(models.Model):
    u'Class to store key -> value, value_type of SetTopBox'

    key = models.CharField(_(u'Chave'), max_length=250,
        help_text=_(u'Chave do parametro. Ex. VOLUME_LEVEL'), db_index=True)
    value = models.CharField(_(u'Valor'), max_length=250,
        help_text=_(u'Valor do parametro. Ex. 0.5'), db_index=True)
    value_type = models.CharField(_(u'Tipo do parametro'), max_length=50)
    settopbox = models.ForeignKey(SetTopBox, db_index=True)

    class Meta:
        verbose_name = _(u'Configuração do SetTopBox')
        verbose_name_plural = _(u'Configurações do SetTopBox')
        unique_together = (('key', 'settopbox'),)

    def __unicode__(self):
        return u'%s {%s=%s}' % (self.settopbox, self.key, self.value)

