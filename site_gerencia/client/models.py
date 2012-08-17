# -*- encoding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _


class SetTopBox(models.Model):
    u'Class to authenticate and manipulate IPTV client - SetTopBox'

    serial_number = models.CharField(_(u'Número serial'), max_length=255,
        help_text=_(u'Número serial do SetTopBox'), unique=True)

    class Meta:
        verbose_name = _(u'SetTopBox')
        verbose_name_plural = _(u'SetTopBoxes')

    def __unicode__(self):
        return u'id:%d serial:%s' % (self.id, self.serial_number)


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
