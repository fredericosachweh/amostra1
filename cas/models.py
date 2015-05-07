#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from __future__ import division, unicode_literals
import logging
from django.db import models
from django.utils.translation import ugettext_lazy as _
# from django.core.urlresolvers import reverse

log = logging.getLogger('cas')

DEVICE_TYPE = (('stb_iptv', 'STB_IPTV'),)


class RTESServer(models.Model):
    name = models.CharField(_(u'Nome'), max_length=200, unique=True,
                            default='RTES1', help_text=u'Inicialmente deve ser RTES1')
    host = models.IPAddressField(_(u'Host'), blank=False, unique=True)
    definition_uri = models.URLField(_(u'URL de descrição do serviço (WSDL)'),
                                     help_text=u'https://10.1.1.56:8094/services/RTES?wsdl')
    service_uri = models.URLField(_(u'URL do Web Service'),
                                  help_text=u'https://10.1.1.56:8094/services/RTES')
    username = models.CharField(_(u'Usuário'), max_length=200, blank=False)
    password = models.CharField(_(u'Senha'), max_length=200, blank=False)

    class Meta:
        verbose_name = _(u'Servidor RTES - Verimatrix')
        verbose_name_plural = _(u'Servidores RTES - Verimatrix')

    def __str__(self):
        return self.name


class Device(models.Model):
    device_id = models.CharField(_(u'Descrição do dispositivo'), max_length=200,
                                 help_text=u'SetTopBox de teste', primary_key=True,
                                 unique=True
                                 )
    device_type = models.CharField('Tipo de dispositivo', max_length=100,
                                   choices=DEVICE_TYPE)
    network_id = models.PositiveSmallIntegerField(_(u'Id da rede'), default='1')
    network_device_id = models.CharField(_(u'MAC'), max_length=200, unique=True,
                                         help_text=u'00:1A:D0:BE:EF:5F')

    def __str__(self):
        return self.network_device_id


class Entitlement(models.Model):
    channel_id = models.PositiveSmallIntegerField(_('ID do Canal'), unique=True,
                                                  null=False, primary_key=True)
    ip_src = models.IPAddressField(_('Endereço IP - Origem'), unique=True)
    port_src = models.PositiveSmallIntegerField(_('Porta - Origem'), default=10000)
    ip_dest = models.IPAddressField(_('Endereço IP - Destino'), unique=True)
    port_dest = models.PositiveSmallIntegerField(_('Porta - Destino'), default=10000)

    def __str__(self):
        return str(self.channel_id)


class DeviceEntitlement(models.Model):
    device = models.ForeignKey(Device)
    entitlement = models.ForeignKey(Entitlement)

    def __str__(self):
        return "%s-%s" % (self.device, self.entitlement)
