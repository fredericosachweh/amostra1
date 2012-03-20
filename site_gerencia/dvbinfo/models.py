# -*- encoding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _

# DVB-S/S2 models

class Satellite(models.Model):

    class Meta:
        ordering = ('azimuth_degrees', 'azimuth_direction')
        verbose_name = _(u'Satélite')
        verbose_name_plural = _(u'Satélites')
		
    name = models.CharField(max_length=200)
    azimuth_degrees = models.FloatField()
    azimuth_direction = models.CharField(max_length=10)
    info = models.TextField(blank=True)
    logo = models.CharField(max_length=300)
    
    def __unicode__(self):
        return u'%d °%s - %s' % (self.azimuth_degrees, self.azimuth_direction, self.name)

class Transponder(models.Model):

    class Meta:
        ordering = ('name', 'frequency')
        verbose_name = _(u'Transponder')
        verbose_name_plural = _(u'Transponders')

    name = models.CharField(max_length=200, blank=True)
    band = models.CharField(max_length=20, blank=True)
    frequency = models.PositiveIntegerField()
    symbol_rate = models.PositiveIntegerField()
    polarization = models.CharField(max_length=100)
    fec = models.CharField(max_length=10)
    system = models.CharField(max_length=10, null=True)
    modulation = models.CharField(max_length=10, null=True)
    logo = models.CharField(max_length=300)
    satellite = models.ForeignKey(Satellite)
    
    def __unicode__(self):
        return self.name if self.name else self.dvbschannel_set.all()[0].name

class DvbsChannel(models.Model):

    class Meta:
        ordering = ('name',)
        verbose_name = _(u'Canal de Satélite')
        verbose_name_plural = _(u'Canais de Satélite')

    name = models.CharField(_(u'Nome'), max_length=200)
    idiom = models.CharField(_(u'Idioma'), max_length=200, null=True)
    category = models.CharField(_(u'Categoria'), max_length=50, null=True)
    codec = models.CharField(_(u'Codec'), max_length=50, null=True)
    crypto = models.CharField(_(u'Criptografia'), max_length=50, null=True)
    last_info = models.TextField(null=True)
    last_update = models.DateField(null=True)
    logo = models.CharField(_(u'Logotipo'), max_length=300, null=True)
    definition = models.CharField(_(u'Definição'), max_length=2, null=True)
    transponder = models.ForeignKey(Transponder)
    
    def __unicode__(self):
        return self.name

# ISDB-Tb models

class State(models.Model):
    name = models.CharField(_(u'Nome'), max_length=200)

class City(models.Model):
    name = models.CharField(_(u'Nome'), max_length=200)
    state = models.ForeignKey(State)
    
class PhysicalChannel(models.Model):
    number = models.PositiveSmallIntegerField(_(u'Canal físico'))
    city = models.ForeignKey(City)
    def _get_frequency(self):
        "Returns the frequency based on the channel number."
        return ((self.number - 14) * 6000) + 473143
    frequency = property(_get_frequency)
    
    def __unicode__(self):
        return str(self.number)

class VirtualChannel(models.Model):
    
    class Meta:
        ordering = ('name',)
        verbose_name = _(u'Canal de TV Digital')
        verbose_name_plural = _(u'Canais de TV Digitais')
    
    number = models.FloatField(_(u'Canal virtual'))
    name = models.CharField(_(u'Nome'), max_length=200)
    epg = models.BooleanField(_(u'Guia de programação'))
    interactivity = models.BooleanField(_(u'Interatividade'))
    physical_channel = models.ForeignKey(PhysicalChannel)
    
    def city(self):
        return self.physical_channel.city.name
    
    def state(self):
        return self.physical_channel.city.state.name
