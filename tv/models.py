#!/usr/bin/env python
# -*- encoding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

#from device.models import MulticastOutput


class Channel(models.Model):
    """
    Classe de manipulação de Canal de TV
    """
    class Meta:
        ordering = ('number',)
        verbose_name_plural = _('Canais')
    number = models.PositiveSmallIntegerField(_('Numero'), unique=True)
    name = models.CharField(_('Nome'), max_length=100)
    description = models.TextField(_('Descricao'))
    channelid = models.CharField(_('ID do Canal'), max_length=255)
    image = models.ImageField(
        _('Logo'),
        upload_to='tv/channel/image/tmp',
        help_text='Imagem do canal'
    )
    thumb = models.ImageField(
        _('Miniatura'),
        upload_to='tv/channel/image/thumb',
        help_text='Imagem do canal'
    )
    updated = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(_('Disponível'), default=False)
    source = models.ForeignKey('device.MulticastOutput', unique=False)
    buffer_size = models.PositiveIntegerField(
        _('STB Buffer (milisegundos)'),
        default=1000, help_text='For easy STB 300 > and < 5000'
    )

    _p = None
    _n = None

    def __unicode__(self):
        return "[%d] num=%s %s" % (self.id, self.number, self.name)

    def image_thum(self):
        return '<img width="40" alt="Thum não existe" src="%s" />' % (
            self.thumb.url
        )

    image_thum.short_description = 'Miniatura'
    image_thum.allow_tags = True

    @property
    def sink(self):
        return self.source

    @property
    def previous(self):
        if self._p is not None:
            return self._p
        ch = Channel.objects.filter(
            number__lt=self.number, enabled=True,
            source__isnull=False
        ).order_by('-number')[0]
        return ch

    @previous.setter
    def _previous(self, val):
        self._p = val

    @property
    def next(self):
        if self._n is not None:
            return self._n
        ch = Channel.objects.filter(
            number__gt=self.number, enabled=True,
            source__isnull=False
        ).order_by('number')[0]
        return ch

    @next.setter
    def _next(self, val):
        self._n = val

    def _is_streaming(self):
        return self.source.running()

    def _is_recording(self):
        for recorder in self.streamrecorder_set.all():
            if recorder.status is True:
                return True
        return False

    def switch_link(self):
        if self.source is None and len(self.streamrecorder_set.all()) is 0:
            return '<a>Desconfigurado</a>'
        ret = []
        if self._is_streaming() is True:
            ret.append(_('Estrimando'))
        if self._is_recording() is True:
            ret.append(_('Gravando'))
        if len(ret) > 0:
            print(ret)
            s = _(" e ").join(v for v in ret)
            return '<a href="%s" id="tv_id_%d" style="color:green;">' \
                '%s</a>' % (
                    reverse('channel_stop', args=[self.pk]), self.pk, s
                )
        else:
            return '<a href="%s" id="tv_id_%d" style="color:red;">' \
                'Parado</a>' % (
                    reverse('channel_start', kwargs={'pk': self.pk}), self.pk
                )
    switch_link.allow_tags = True
    switch_link.short_description = 'Status'

    def delete(self):
        """
        Limpeza da imagem.
        Remove o logo e o thumbnail ao remover o canal
        """
        super(Channel, self).delete()
        import os
        try:
            os.unlink(self.image.path)
            os.unlink(self.thumb.path)
        except:
            pass

    def start(self, recursive=True):
        self.source.start(recursive=recursive)
        for recorder in self.streamrecorder_set.all():
            recorder.start(recursive=recursive)

    def stop(self, recursive=True):
        self.source.stop(recursive=recursive)
        for recorder in self.streamrecorder_set.all():
            recorder.stop(recursive=recursive)

    def _get_channel_devices_str(self):
        obj = self.source
        ret = []
        while True:
            ret.append("%s '%s'" % (obj.__class__.__name__, obj))
            if hasattr(obj, 'sink') and obj.sink is not None:
                obj = obj.sink
            else:
                break
        return " --> ".join(ret)
