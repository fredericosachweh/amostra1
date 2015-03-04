# -*- encoding:utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
import thread
import requests
import datetime

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.conf import settings
from django import forms
from tv.models import Channel
from .fields import MACAddressField

import dbsettings
from nbridge.models import Nbridge
log = logging.getLogger('client')


class LogoToReplace(dbsettings.ImageValue):

    def get_db_prep_save(self, value):
        from PIL import Image
        import os
        log.debug('Modificando logo=%s', value)
        val = super(LogoToReplace, self).get_db_prep_save(value)
        log.debug('Depois do super logo=%s', val)
        if val is None:
            return ''
        # img/menu.png (450, 164)px
        # themes/modern/images/logo_menor2.png (100, 26)px
        if self.attribute_name == 'logo_main':
            fname = os.path.join(settings.MEDIA_ROOT, val)
            thumb = Image.open(fname)
            log.debug('Tamanho:%s', thumb.size)
            thumb.thumbnail((450, 164), Image.ANTIALIAS)
            dst = '%smenu.png' % (settings.MEDIA_ROOT)
            log.debug('Save to:%s', dst)
            thumb.save(dst)
        if self.attribute_name == 'logo_small_menu':
            fname = os.path.join(settings.MEDIA_ROOT, val)
            thumb = Image.open(fname)
            thumb.thumbnail((163, 67), Image.ANTIALIAS)
            dst = '%slogo_menor1.png' % (settings.MEDIA_ROOT)
            log.debug('Save to:%s', dst)
            thumb.save(dst)
        if self.attribute_name == 'logo_small':
            fname = os.path.join(settings.MEDIA_ROOT, val)
            thumb = Image.open(fname)
            thumb.thumbnail((163, 67), Image.ANTIALIAS)
            dst = '%slogo_menor2.png' % (settings.MEDIA_ROOT)
            log.debug('Save to:%s', dst)
            thumb.save(dst)
        if self.attribute_name == 'banner_epg':
            fname = os.path.join(settings.MEDIA_ROOT, val)
            thumb = Image.open(fname)
            thumb.thumbnail((450, 80), Image.ANTIALIAS)
            dst = '%sbanner_repg.png' % (settings.MEDIA_ROOT)
            log.debug('Save to:%s', dst)
            thumb.save(dst)
        log.debug('name=%s', self.attribute_name)
        return val


class CompanyLogo(dbsettings.Group):
    logo_main = LogoToReplace(
        _('Logo principal'), upload_to='',
        help_text='Formato PNG transparente 450 x 164 px', required=False
    )
    logo_small_menu = LogoToReplace(
        _('Logo pequeno Menu'), upload_to='',
        help_text='Formato PNG transparente 163 x 67 px', required=False
    )
    logo_small = LogoToReplace(
        _('Logo pequeno TV'), upload_to='',
        help_text='Formato PNG transparente 163 x 67 px', required=False
    )
    banner_epg = LogoToReplace(
        _('Banner na guia de programação'), upload_to='', required=False,
        help_text='Formato JPG 450 x 80 px'
    )

logo = CompanyLogo('Logo da interface')


class SetTopBoxOptions(dbsettings.Group):
    auto_create = dbsettings.BooleanValue(
        _('Auto criação de settopbox no login'), default=False)
    auto_add_channel = dbsettings.BooleanValue(
        _('Cria automaticamente o vinculo entre settopbox e canal'),
        default=False
        )
    auto_enable_recorder_access = dbsettings.BooleanValue(
        _('Automaticamente libera o acesso nas gravações do canal'),
        default=False
        )
    use_mac_as_serial = dbsettings.BooleanValue(
        _('Caso não seja fornecido via post, utiliza o MAC como serial'),
        default=True
        )

CHOICES_PARENTAL = (
    ('0', 'Livre',),
    ('10', '10 anos',),
    ('12', '12 anos',),
    ('14', '14 anos',),
    ('16', '16 anos',),
    ('18', '18 anos',),
    ('-1', 'Desativado',),
)


class STBPassValue(dbsettings.Value):

    class field(forms.CharField):

        def __init__(self, max_length=4, min_length=4, *args, **kwargs):
            kwargs['max_length'] = 4
            kwargs['min_length'] = 4
            forms.CharField.__init__(self, *args, **kwargs)

        def clean(self, value):
            try:
                value = int(str(value))
            except (ValueError, TypeError):
                raise forms.ValidationError(
                    'Os campos devem conter somente numeros.')
            return forms.CharField.clean(self, value)

    def to_python(self, value):
        try:
            value = int(str(value))
        except (ValueError, TypeError):
            log.error('Valor invalido')
        return value


class SetTopBoxDefaultConfig(dbsettings.Group):
    password = STBPassValue(
        _('Senha do cliente'),
        help_text='Senha equipamento do cliente', default=None)
    recorder = dbsettings.BooleanValue(
        _('Acesso à Gravações habilitado'),
        default=False)
    parental = dbsettings.StringValue(
        _('Controle parental'),
        choices=CHOICES_PARENTAL,
        default=-1)


def reload_channels(
        nbridge, settopbox, message=None, userchannel=True, channel=True
    ):
    log.debug('Reload [%s] nbridge [%s]=%s', settopbox, nbridge, message)
    # reloaduserdata
    url = 'http://%s/ws/eval' % (nbridge.server.host)
    command = ''
    if userchannel:
        command += 'require(\"api/tv/userchannel\").fetch();'
    if channel:
        command += 'require(\"api/tv/channel\").fetch();'
    if message:
        command += 'alert(\"%s.\");' % (message)
    log.debug('Comando=%s', command)
    try:
        response = requests.post(url, timeout=10, data={
            'server_key': settings.NBRIDGE_SERVER_KEY,
            'command': command,
            'mac': [settopbox.mac]})
        log.debug('Resposta=[%s]%s', response.status_code, response.text)
    except Exception as e:
        log.error('ERROR:%s', e)
    finally:
        log.info('Finalizado o request')


def reboot_stb(nbridge, settopbox):
    log.debug('Send reboot to STB=%s using nbridge=%s', settopbox, nbridge)
    url = 'http://%s/ws/reboot/' % (settopbox.nbridge.server.host)
    try:
        response = requests.post(url, timeout=10, data={
            'server_key': settings.NBRIDGE_SERVER_KEY,
            'command': '',
            'mac': [settopbox.mac]})
        log.debug('Resposta=[%s]%s', response.status_code, response.text)
    except Exception as e:
        log.error('ERROR:%s', e)
    finally:
        log.info('Finalizado o request')


def remote_debug_stb(settopbox):
    log.debug('Enable STB remote debuger=%s', settopbox)
    url = 'http://%s/ws/eval' % (settopbox.nbridge.server.host)
    command = '(function(e){e.src="http://middleware.iptvdomain:8880/target/target-script-min.js#cianet";document.head.appendChild(e);})(document.createElement("script"));'
    log.debug('Comando=%s', command)
    try:
        response = requests.post(url, timeout=10, data={
            'server_key': settings.NBRIDGE_SERVER_KEY,
            'command': command,
            'mac': [settopbox.mac]})
        log.debug('Resposta=[%s]%s', response.status_code, response.text)
    except Exception as e:
        log.error('ERROR:%s', e)
    finally:
        log.info('Finalizado o request')


def reload_frontend_stb(settopbox):
    log.debug('Reload frontend STB remote %s', settopbox)
    url = 'http://%s/ws/eval' % (settopbox.nbridge.server.host)
    command = 'window.location.reload();'
    log.debug('Comando=%s', command)
    try:
        response = requests.post(url, timeout=10, data={
            'server_key': settings.NBRIDGE_SERVER_KEY,
            'command': command,
            'mac': [settopbox.mac]})
        log.debug('Resposta=[%s]%s', response.status_code, response.text)
    except Exception as e:
        log.error('ERROR:%s', e)
    finally:
        log.info('Finalizado o recarregamento do frontend')


class SetTopBox(models.Model):
    'Class to authenticate and manipulate IPTV client - SetTopBox'

    serial_number = models.CharField(
        _('Número serial'), max_length=255,
        help_text=_('Número serial do SetTopBox'), unique=True)
    mac = MACAddressField(
        _('Endereço MAC'), max_length=255,
        help_text=_('Endereço MAC do SetTopBox'), unique=True)
    description = models.CharField(
        _('Descrição opcional'), max_length=255,
        blank=True, null=True)
    online = models.BooleanField(_('On-line'), default=False)
    ip = models.GenericIPAddressField(
        _('Endereço IP'), protocol='IPv4', blank=True, null=True, default=None
    )
    nbridge = models.ForeignKey(
        'nbridge.Nbridge', blank=True, null=True, default=None,
        db_constraint=False)
    # Options
    options = SetTopBoxOptions('Opções do SetTopBox')
    default = SetTopBoxDefaultConfig('Valores do cliente')

    class Meta:
        verbose_name = _('SetTopBox')
        verbose_name_plural = _('SetTopBoxes')

    def __unicode__(self):
        # return 'serial=%s,mac=%s' % (self.serial_number, self.mac)
        return '%s' % (self.serial_number)

    def get_user(self):
        'Returns: User related with this SetTopBox'
        return User.objects.get(
            username='%s%s' % (settings.STB_USER_PREFIX, self.serial_number)
        )

    def get_channels(self):
        'Returns: a list of tv.channel for relation SetTopBoxChannel'
        return Channel.objects.filter(
            settopboxchannel__settopbox=self,
            enabled=True,
            source__isnull=False)

    def reboot(self):
        nbs = Nbridge.objects.filter(status=True)
        for s in nbs:
            thread.start_new_thread(reboot_stb, (s, self))

    def reload_channels(self, channel=False, message=None):
        nbridge = Nbridge.objects.filter(id=self.nbridge_id)
        if self.online and nbridge.exists():
            reload_channels(nbridge, self, channel=True, message=message)

    def remote_debug(self):
        if self.online is True and self.nbridge is not None:
            remote_debug_stb(self)

    def reload_frontend_stb(self):
        nbridge = Nbridge.objects.filter(id=self.nbridge_id)
        if self.online and nbridge.exists():
            reload_frontend_stb(self)

    @classmethod
    def get_stb_from_user(self, user):
        if user.username.find(settings.STB_USER_PREFIX) == 0:
            serial = user.username.replace(settings.STB_USER_PREFIX, '')
            try:
                stb = SetTopBox.objects.get(serial_number=serial)
                return stb
            except:
                return None
        else:
            return None


class SetTopBoxParameter(models.Model):
    'Class to store key -> values of SetTopBox'

    key = models.CharField(
        _('Chave'), max_length=250,
        help_text=_('Chave do parametro. Ex. MACADDR'), db_index=True
    )
    value = models.CharField(
        _('Valor'), max_length=250,
        help_text=_('Valor do parametro. Ex. 00:00:00:00:00'), db_index=True
    )
    settopbox = models.ForeignKey('client.SetTopBox', db_index=True)

    class Meta:
        verbose_name = _('Parametro do SetTopBox')
        verbose_name_plural = _('Parametros dos SetTopBox')
        unique_together = (('key', 'value', 'settopbox'),)

    def __unicode__(self):
        return '%s {%s=%s}' % (self.settopbox, self.key, self.value)


class SetTopBoxChannel(models.Model):
    'Class to link access permission to stb on tv.channel'

    settopbox = models.ForeignKey('client.SetTopBox', db_index=True)
    channel = models.ForeignKey('tv.Channel', db_index=True)
    recorder = models.BooleanField(_('Pode acessar conteúdo gravado'))

    class Meta:
        unique_together = (('settopbox', 'channel',),)
        ordering = ('settopbox', 'channel__number',)
        verbose_name = 'STB <=> Canal (canal habilitado)'
        verbose_name_plural = 'STBs <=> Canais (canais habilitados)'

    def __unicode__(self):
        return 'SetTopBoxChannel[ch=%s stb=%s] rec=%s' % (
            self.channel.number,
            self.settopbox.serial_number, self.recorder
        )


class SetTopBoxConfig(models.Model):
    'Class to store key -> value, value_type of SetTopBox'

    key = models.CharField(
        _('Chave'), max_length=250,
        help_text=_('Chave do parametro. Ex. VOLUME_LEVEL'), db_index=True
    )
    value = models.CharField(
        _('Valor'), max_length=250,
        help_text=_('Valor do parametro. Ex. 0.5'), db_index=True
    )
    value_type = models.CharField(_('Tipo do parametro'), max_length=50)
    settopbox = models.ForeignKey('client.SetTopBox', db_index=True)

    class Meta:
        verbose_name = _('Configuração do Cliente')
        verbose_name_plural = _('Configurações do Cliente')
        unique_together = (('key', 'settopbox'),)

    def __unicode__(self):
        return '%s {%s=%s}' % (self.settopbox, self.key, self.value)


class SetTopBoxMessage(models.Model):
    'Class to store UI messages'
    key = models.CharField(
        _('Chave'), max_length=250, db_index=True,
        help_text=_('Chave de indentificação da mensagem')
    )
    value = models.TextField(_('Conteúdo'))
    api_reference = models.CharField(
        _('Referencia de API'), max_length=250,
        help_text=_('API base para consumo de variáveis')
    )

    class Meta:
        verbose_name = _('Mensagem do cliente')
        verbose_name_plural = _('Mensagens do cliente')

    def __unicode__(self):
        return self.key


class SetTopBoxProgramSchedule(models.Model):
    'Class to store the data and time of Program on Schedule'

    settopbox = models.ForeignKey('client.SetTopBox', db_index=True)
    channel = models.ForeignKey('tv.Channel', db_index=True)
    url = models.TextField('/tv/api/tv/v1/channel/42/')
    message = models.TextField(_('Agendamento realizado com sucesso!'))
    schedule_date = models.BigIntegerField(null=False)

    class Meta:
        verbose_name = _('Agendamento')
        verbose_name_plural = _('Agendamentos')
        ordering = ('settopbox', 'channel__number',)

    def __unicode__(self):
        return 'canal=[%s] stb=[%s] hora=[%s]' % (
            self.channel, self.settopbox.serial_number,
            datetime.datetime.fromtimestamp(self.schedule_date)
        )

class SetTopBoxBehaviorFlag(models.Model):
    'Class to store Behavior flags'
    key = models.CharField(
        _('Chave'), max_length=250, db_index=True,
        help_text=_('Chave de indentificação da flag de comportamento')
    )


    value = models.CharField(
        _('Valor'), max_length=250,
        help_text=_('Valor do comportamento. Ex. 0.5'), db_index=True
    )
    
    value_type = models.CharField(_('Tipo do parametro'), max_length=50)

    class Meta:
        verbose_name = _('Flag de comportamento')
        verbose_name_plural = _('Flags de comportamento')

    def __unicode__(self):
        return '{%s=%s}' % (self.key, self.value)

