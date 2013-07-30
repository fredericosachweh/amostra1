# -*- encoding:utf-8 -*-

import logging
from PIL import Image
import os

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.conf import settings
import dbsettings
from tv import models as tvmodels


class LogoToReplace(dbsettings.ImageValue):

    def get_db_prep_save(self, value):
        log = logging.getLogger('client')
        log.debug('Modificando logo=%s', value)
        val = super(LogoToReplace, self).get_db_prep_save(value)
        log.debug('Depois do super logo=%s', val)
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
        log.debug('name=%s', self.attribute_name)
        return val


class CompanyLogo(dbsettings.Group):
    logo_main = LogoToReplace(_(u'Logo principal'), upload_to='',
        help_text=u'Formato PNG transparente 450 x 164 px')
    logo_small = LogoToReplace(_(u'Logo pequeno'), upload_to='',
        help_text=u'Formato PNG transparente 100 x 26 px')

logo = CompanyLogo(u'Logo da interface')


class SetTopBoxOptions(dbsettings.Group):
    auto_create = dbsettings.BooleanValue(
        _(u'Auto criação de settopbox no login'), default=False)
    auto_add_channel = dbsettings.BooleanValue(
        _(u'Cria automaticamente o vinculo entre settopbox e canal'),
        default=False
        )
    auto_enable_recorder_access = dbsettings.BooleanValue(
        _(u'Automaticamente libera o acesso nas gravações do canal'),
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
        u'Returns: User related with this SetTopBox'
        return User.objects.get(username='%s%s' % (settings.STB_USER_PREFIX,
            self.serial_number))

    def get_channels(self):
        u'Returns: a list of tv.channel for relation SetTopBoxChannel'
        return tvmodels.Channel.objects.filter(
            settopboxchannel__settopbox=self,
            enabled=True,
            source__isnull=False)


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
    channel = models.ForeignKey(tvmodels.Channel, db_index=True)
    recorder = models.BooleanField(_(u'Pode acessar conteúdo gravado'))

    class Meta:
        unique_together = (('settopbox', 'channel',),)

    def __unicode__(self):
        return u'SetTopBoxChannel[ch=%s stb=%s] rec=%s' % (self.channel.number,
            self.settopbox.serial_number, self.recorder)


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
