# -*- encoding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _

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
        return self.name if self.name else self.channel_set.all()[0].name

class Channel(models.Model):

    class Meta:
        ordering = ('name',)
        verbose_name = _(u'Canal')
        verbose_name_plural = _(u'Canais')

    name = models.CharField(max_length=200)
    idiom = models.CharField(max_length=200, null=True)
    category = models.CharField(max_length=50, null=True)
    codec = models.CharField(max_length=50, null=True)
    crypto = models.CharField(max_length=50, null=True)
    last_info = models.TextField(null=True)
    last_update = models.DateField(null=True)
    logo = models.CharField(max_length=300, null=True)
    definition = models.CharField(max_length=2, null=True)
    transponder = models.ForeignKey(Transponder)
    
    def __unicode__(self):
        return self.name

