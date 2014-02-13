# -*- encoding:utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import thread
import requests

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.conf import settings

import dbsettings
from django.contrib.contenttypes.generic import GenericForeignKey
server_key = settings.NBRIDGE_SERVER_KEY
from tv import models as tvmodels
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
            dst = '/iptv/var/www/sites/frontend/dist/img/menu.png'
            log.debug('Save to:%s', dst)
            thumb.save(dst)
        if self.attribute_name == 'logo_small':
            fname = os.path.join(settings.MEDIA_ROOT, val)
            thumb = Image.open(fname)
            thumb.thumbnail((100, 26), Image.ANTIALIAS)
            dst = '/iptv/var/www/sites/frontend/dist/img/logo_menor2.png'
            log.debug('Save to:%s', dst)
            thumb.save(dst)
        if self.attribute_name == 'logo_small_men':
            fname = os.path.join(settings.MEDIA_ROOT, val)
            thumb = Image.open(fname)
            thumb.thumbnail((263, 67), Image.ANTIALIAS)
            dst = '/iptv/var/www/sites/frontend/dist/img/logo_menor1.png'
            log.debug('Save to:%s', dst)
            thumb.save(dst)
        if self.attribute_name == 'banner_epg':
            fname = os.path.join(settings.MEDIA_ROOT, val)
            thumb = Image.open(fname)
            thumb.thumbnail((450, 80), Image.ANTIALIAS)
            dst = '/iptv/var/www/sites/frontend/dist/img/banner_aron.jpg'
            log.debug('Save to:%s', dst)
            thumb.save(dst)
        log.debug('name=%s', self.attribute_name)
        return val


class CompanyLogo(dbsettings.Group):
    logo_main = LogoToReplace(_('Logo principal'), upload_to='',
        help_text='Formato PNG transparente 450 x 164 px', required=False)
    logo_small_menu = LogoToReplace(_('Logo pequeno Men'), upload_to='',
        help_text='Formato PNG transparente 100 x 26 px', required=False)
    logo_small = LogoToReplace(_('Logo pequeno TV'), upload_to='',
        help_text='Formato PNG transparente 100 x 26 px', required=False)
    banner_epg = LogoToReplace(_('Banner na guia de programação'),
        upload_to='', required=False,
        help_text='Formato PNG transparente 450 x 80 px')

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

def reload_channels(nbridge, settopbox, message=None, userchannel=True,
        channel=True):
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
        response = requests.post(url, timeout=10, data={
            'server_key': server_key,
            'command': command,
            'mac': [settopbox.mac]})
        log.debug('Resposta=[%s]%s', response.status_code, response.text)
    except Exception as e:
        log.error('ERROR:%s', e)
    finally:
        log.info('Finalizado o request')

def reboot_stb(nbridge, settopbox):
    log.debug('Send reboot to STB=%s using nbridge=%s', settopbox, nbridge)
    url = 'http://%s/ws/reboot/' % (nbridge.server.host)
    try:
        response = requests.post(url, timeout=10, data={
            'server_key': server_key,
            'command': '',
            'mac': [settopbox.mac]})
        log.debug('Resposta=[%s]%s', response.status_code, response.text)
    except Exception as e:
        log.error('ERROR:%s', e)
    finally:
        log.info('Finalizado o request')


class SetTopBox(models.Model):
    'Class to authenticate and manipulate IPTV client - SetTopBox'

    serial_number = models.CharField(_('Número serial'), max_length=255,
        help_text=_('Número serial do SetTopBox'), unique=True)
    mac = models.CharField(_('Endereço MAC'), max_length=255,
        help_text=_('Endereço MAC do SetTopBox'), unique=True)
    options = SetTopBoxOptions('Opções do SetTopBox')

    class Meta:
        verbose_name = _('SetTopBox')
        verbose_name_plural = _('SetTopBoxes')

    def __unicode__(self):
        #return 'serial=%s,mac=%s' % (self.serial_number, self.mac)
        return '%s' % (self.serial_number)

    def get_user(self):
        'Returns: User related with this SetTopBox'
        return User.objects.get(username='%s%s' % (settings.STB_USER_PREFIX,
            self.serial_number))

    def get_channels(self):
        'Returns: a list of tv.channel for relation SetTopBoxChannel'
        return tvmodels.Channel.objects.filter(
            settopboxchannel__settopbox=self,
            enabled=True,
            source__isnull=False)

    def reboot(self):
        nbs = Nbridge.objects.filter(status=True)
        for s in nbs:
            thread.start_new_thread(reboot_stb, (s, self)) 

    def reload_channels(self, channel=False, message=None):
        nbs = Nbridge.objects.filter(status=True)
        for s in nbs:
            thread.start_new_thread(reload_channels, (s, self),
                {'channel': True, 'message': message} ) 
 
 
class SetTopBoxParameter(models.Model):
    'Class to store key -> values of SetTopBox'

    key = models.CharField(_('Chave'), max_length=250,
        help_text=_('Chave do parametro. Ex. MACADDR'), db_index=True)
    value = models.CharField(_('Valor'), max_length=250,
        help_text=_('Valor do parametro. Ex. 00:00:00:00:00'), db_index=True)
    settopbox = models.ForeignKey(SetTopBox, db_index=True)

    class Meta:
        verbose_name = _('Parametro do SetTopBox')
        verbose_name_plural = _('Parametros dos SetTopBox')
        unique_together = (('key', 'value', 'settopbox'),)

    def __unicode__(self):
        return '%s {%s=%s}' % (self.settopbox, self.key, self.value)


class SetTopBoxChannel(models.Model):
    'Class to link access permission to stb on tv.channel'

    settopbox = models.ForeignKey(SetTopBox, db_index=True)
    channel = models.ForeignKey(tvmodels.Channel, db_index=True)
    recorder = models.BooleanField(_('Pode acessar conteúdo gravado'))

    class Meta:
        unique_together = (('settopbox', 'channel',),)
        ordering = ('settopbox', 'channel__number',)
        verbose_name = 'STB <=> Canal (canal habilitado)'
        verbose_name_plural = 'STBs <=> Canais (canais habilitados)'

    def __unicode__(self):
        return 'SetTopBoxChannel[ch=%s stb=%s] rec=%s' % (self.channel.number,
            self.settopbox.serial_number, self.recorder)


class SetTopBoxConfig(models.Model):
    'Class to store key -> value, value_type of SetTopBox'

    key = models.CharField(_('Chave'), max_length=250,
        help_text=_('Chave do parametro. Ex. VOLUME_LEVEL'), db_index=True)
    value = models.CharField(_('Valor'), max_length=250,
        help_text=_('Valor do parametro. Ex. 0.5'), db_index=True)
    value_type = models.CharField(_('Tipo do parametro'), max_length=50)
    settopbox = models.ForeignKey(SetTopBox, db_index=True)

    class Meta:
        verbose_name = _('Configuração do Cliente')
        verbose_name_plural = _('Configurações do Cliente')
        unique_together = (('key', 'settopbox'),)

    def __unicode__(self):
        return '%s {%s=%s}' % (self.settopbox, self.key, self.value)


class SetTopBoxMessage(models.Model):
    'Class to store UI messages'
    key = models.CharField(_('Chave'), max_length=250, db_index=True,
        help_text=_('Chave de indentificação da mensagem'))
    value = models.TextField(_('Conteúdo'))
    api_reference = models.CharField(_('Referencia de API'), max_length=250,
        help_text=_('API base para consumo de variáveis'))

    class Meta:
        verbose_name = _('Mensagem do cliente')
        verbose_name_plural = _('Mensagens do cliente')

    def __unicode__(self):
        return self.key
