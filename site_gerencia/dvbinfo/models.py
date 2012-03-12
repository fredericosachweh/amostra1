# -*- encoding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _

class Satellite(models.Model):

    class Meta:
        ordering = ('location',)
        verbose_name = _(u'Satélite')
        verbose_name_plural = _(u'Satélites')
		
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=10)
    info = models.TextField(blank=True)
    logo = models.CharField(max_length=300)
    
    def __unicode__(self):
        return self.location + ' - ' + self.name

class Transponder(models.Model):

    class Meta:
        verbose_name = _(u'Transponder')
        verbose_name_plural = _(u'Transponders')

    name = models.CharField(max_length=200, blank=True)
    band = models.CharField(max_length=20, blank=True)
    frequency = models.PositiveIntegerField()
    symbol_rate = models.PositiveIntegerField()
    polarization = models.CharField(max_length=1)
    fec = models.CharField(max_length=10)
    system = models.CharField(max_length=10, null=True)
    modulation = models.CharField(max_length=10, null=True)
    logo = models.CharField(max_length=300)
    satellite = models.ForeignKey(Satellite)
    
    def __unicode__(self):
        return self.name if self.name else self.channel_set.all()[0].name

class Channel(models.Model):

    class Meta:
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

