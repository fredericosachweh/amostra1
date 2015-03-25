#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _

import os
import logging
log = logging.getLogger('debug')


class Epg_Source(models.Model):
    "EPG source information"

    class Meta:
        permissions = (
            ("download_epg", _('Permissão para fazer download do EPG')),
        )

    filefield = models.FileField(_('Arquivo a ser importado'),
        upload_to='epg/')
    lastModification = models.DateTimeField(
        _('Data da última modificação no servidor da revista eletrônica'),
        unique=True, auto_now=True)
    # Creation time
    created = models.DateTimeField(_('Data de criação'), auto_now=True)
    # Total number of elements in the file
    numberofElements = models.PositiveIntegerField(
        _('Número de elementos neste arquivo'),
        blank=True, null=True, default=0)
    # Number of imported elements
    #importedElements = models.PositiveIntegerField(
    #    _('Número de elementos ja importados'),
    #    blank=True, null=True, default=0)
    # Time diference between the smallest and the farthest time
    minor_start = models.DateTimeField(
        _('Menor tempo de inicio encontrado nos programas'),
        blank=True, null=True)
    major_stop = models.DateTimeField(
        _('Maior tempo de final encontrado nos programas'),
        blank=True, null=True)


class XMLTV_Source(Epg_Source):
    "Information exclusive to XMLTV format"
    # Grabbed from <tv> element
    source_info_url = models.CharField(_('Source info url'),
        max_length=100, blank=True, null=True)
    source_info_name = models.CharField(_('Source info name'),
        max_length=100, blank=True, null=True)
    source_data_url = models.CharField(_('Source data url'),
        max_length=100, blank=True, null=True)
    generator_info_name = models.CharField(_('Generator info name'),
        max_length=100, blank=True, null=True)
    generator_info_url = models.CharField(_('Generator info url'),
        max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _('Arquivo XML/ZIP EPG')
        verbose_name_plural = _('Arquivos XML/ZIP EPG')

    def __unicode__(self):
        return 'ID: %d - Start: %s - Stop: %s' % (self.id, self.minor_start,
            self.major_stop)


class Lang(models.Model):
    value = models.CharField(max_length=10, db_index=True)


class Display_Name(models.Model):
    value = models.CharField(max_length=100, db_index=True)
    lang = models.ForeignKey(Lang, blank=True, null=True)

    def __unicode__(self):
        return self.value


class Icon(models.Model):
    src = models.CharField(max_length=10, db_index=True)


class Url(models.Model):
    value = models.CharField(max_length=200, db_index=True)


class Channel(models.Model):
    channelid = models.CharField(max_length=254, unique=True, db_index=True)
    display_names = models.ManyToManyField(Display_Name, blank=True, null=True)
    icons = models.ManyToManyField(Icon, blank=True, null=True)
    urls = models.ManyToManyField(Url, blank=True, null=True)

    def __unicode__(self):
        names = self.display_names.values_list()
        if len(names) == 1:
            name = self.display_names.values_list()[0][1]
        else:
            name = ''
        return "%s [%s]" % (name, self.channelid)


class Title(models.Model):
    value = models.CharField(max_length=128, db_index=True)
    lang = models.ForeignKey(Lang, blank=True, null=True)


class Description(models.Model):
    value = models.TextField(blank=True, null=True)
    lang = models.ForeignKey(Lang, blank=True, null=True)


class Staff(models.Model):
    name = models.CharField(max_length=512)


class Actor(models.Model):
    name = models.CharField(max_length=512)
    role = models.CharField(max_length=100, blank=True, null=True,
        db_index=True)


class Category(models.Model):
    value = models.CharField(max_length=100, db_index=True)
    lang = models.ForeignKey(Lang, db_index=True)


class Country(models.Model):
    value = models.CharField(max_length=100, db_index=True)


class Episode_Num(models.Model):
    value = models.CharField(max_length=100, db_index=True)
    system = models.CharField(max_length=100, db_index=True)


class Rating(models.Model):
    system = models.CharField(max_length=100, db_index=True)
    value = models.CharField(max_length=100, db_column='value', db_index=True)
    int_value = models.PositiveSmallIntegerField(null=True, default=0)

    class Meta:
        unique_together = (('system', 'value'),)

    def __unicode__(self):
        return '%s:%s' % (self.system, self.value)

    def save(self, *args, **kwargs):
        if self.value.isdigit():
            self.value = int(self.value)
        if (self.value == 'Programa livre para todas as idades') or (self.value < 10):
            self.int_value = 0
        elif self.value == 'Programa impróprio para menores de 10 anos' or (self.value == 10):
            self.int_value = 10
        elif self.value == 'Programa impróprio para menores de 12 anos' or (self.value == 11) or (self.value == 12):
            self.int_value = 12
        elif self.value == 'Programa impróprio para menores de 14 anos' or (self.value == 13) or (self.value == 14):
            self.int_value = 14
        elif self.value == 'Programa impróprio para menores de 16 anos' or (self.value == 15) or (self.value == 16):
            self.int_value = 16
        elif self.value == 'Programa impróprio para menores de 18 anos' or (str(self.value).isdigit() and self.value >= 17):
            self.int_value = 18
        else:
            self.int_value = 18
        super(Rating, self).save(*args, **kwargs)


class Language(models.Model):
    value = models.CharField(max_length=50, db_index=True)
    lang = models.ForeignKey(Lang, blank=True, null=True)


class Subtitle(models.Model):
    subtitle_type = models.CharField(max_length=20, blank=True, null=True)
    language = models.ForeignKey(Language, blank=True, null=True)


class Star_Rating(models.Model):
    value = models.CharField(max_length=10, db_index=True)
    system = models.CharField(max_length=100, blank=True, null=True,
        db_index=True)
    icons = models.ManyToManyField(Icon, blank=True, null=True)


class Programme(models.Model):
    programid = models.CharField(max_length=32,db_index=True)
    titles = models.ManyToManyField(Title, related_name='titles', blank=True,
        null=True)
    secondary_titles = models.ManyToManyField(Title,
        related_name='secondary_titles', blank=True, null=True)
    descriptions = models.ManyToManyField(Description, blank=True, null=True)
    date = models.CharField(max_length=50, blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    episode_numbers = models.ManyToManyField(Episode_Num, blank=True,
        null=True)
    rating = models.ForeignKey(Rating, blank=True, null=True)
    language = models.ForeignKey(Language, related_name='language', blank=True,
        null=True)
    original_language = models.ForeignKey(Language,
        related_name='original_language', blank=True, null=True)
    length = models.PositiveIntegerField(blank=True, null=True)
    subtitles = models.ManyToManyField(Language, blank=True, null=True)
    star_ratings = models.ManyToManyField(Star_Rating, blank=True, null=True)
    # Video
    video_present = models.CharField(max_length=10, blank=True, null=True)
    video_colour = models.CharField(max_length=10, blank=True, null=True)
    video_aspect = models.CharField(max_length=10, blank=True, null=True)
    video_quality = models.CharField(max_length=10, blank=True, null=True)
    # Audio
    audio_present = models.CharField(max_length=10, blank=True, null=True)
    audio_stereo = models.CharField(max_length=10, blank=True, null=True)
    # Credits
    actors = models.ManyToManyField(Actor, blank=True, null=True)
    directors = models.ManyToManyField(Staff, related_name='director',
        blank=True, null=True)
    writers = models.ManyToManyField(Staff, related_name='writer', blank=True,
        null=True)
    adapters = models.ManyToManyField(Staff, related_name='adapter',
        blank=True, null=True)
    producers = models.ManyToManyField(Staff, related_name='producer',
        blank=True, null=True)
    composers = models.ManyToManyField(Staff, related_name='composer',
        blank=True, null=True)
    editors = models.ManyToManyField(Staff, related_name='editor', blank=True,
        null=True)
    presenters = models.ManyToManyField(Staff, related_name='presenter',
        blank=True, null=True)
    commentators = models.ManyToManyField(Staff, related_name='commentator',
        blank=True, null=True)
    guests = models.ManyToManyField(Staff, related_name='guest', blank=True,
        null=True)

    def __unicode__(self):
        vlist = self.titles.values_list()
        if len(vlist) == 0:
            return ""
        return "%s" % (self.titles.values_list()[0][1])


class Guide(models.Model):
    programme = models.ForeignKey(Programme)
    channel = models.ForeignKey(Channel)
    start = models.DateTimeField(blank=True, null=True, db_index=True)
    stop = models.DateTimeField(blank=True, null=True, db_index=True)
    previous = models.ForeignKey('self', related_name='previous_set',
        null=True, blank=True, on_delete=models.SET_NULL)
    next = models.ForeignKey('self', related_name='next_set',
        null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('start',)

    def __unicode__(self):
        pid = '*'
        nid = '*'
        if self.previous is not None:
            pid = self.previous.id
        if self.next is not None:
            nid = self.next.id
        return '"(%s-%s-%s) %s (%s)" %s - %s' % (
            pid,
            self.id,
            nid,
            self.programme,
            self.channel.channelid,
            self.start,
            self.stop)


@receiver(post_save, sender=Guide)
def Guide_post_save(sender, instance, created, **kwargs):
    "Before save lookup for previous and next guide for channel"
    if created:
        log = logging.getLogger('debug')
        ## Remove conflicts
        guides_del = Guide.objects.filter(
            channel=instance.channel,
            stop__gt=instance.start,
            start__lt=instance.stop
            ).exclude(id=instance.id)
        if len(guides_del) > 0:
            log.debug('## Conflito:%s - %s', instance, guides_del)
            n = None
            p = guides_del[0].previous
            botton = guides_del.latest('start')
            if botton is not None:
                n = botton.next
                if n is not None:
                    n.previous = instance
                    n.save()
            instance.next = n
            if p is not None:
                p.next = instance
                p.save()
            instance.previous = p
            instance.save()
            guides_del.delete()
            #log.debug('previous:%s', p)
            #log.debug('Instance:%s', instance)
            #log.debug('next:%s', n)
            return
        #return
        ## find previous
        pr = Guide.objects.filter(
            channel=instance.channel,
            start__lt=instance.start
            ).order_by('-start')[:1]
        nx = Guide.objects.filter(
            channel=instance.channel,
            start__gt=instance.start
            ).order_by('start')[:1]
        p = '*'
        n = '*'
        if len(pr) > 0:
            p = pr[0]
            instance.previous = p
            p.next = instance
            #log.debug('PR:%s', p)
            p.save()
        if len(nx) > 0:
            n = nx[0]
            instance.next = n
            n.previous = instance
            #log.debug('NX:%s', n)
            n.save()
        instance.save()
        #log.info('ANT:%s', p)
        #log.info('ATUAL:%s', instance)
        #log.info('PROX:%s', n)


# Signal used to delete the zip/xml file when a Epg_Source object is deleted
def dvb_source_post_delete(signal, instance, sender, **kwargs):
    # Delete the archive
    path_source_file = instance.filefield.path
    path_epg_full_dump = '%s/%dfull.zip' % (
        os.path.dirname(path_source_file), instance.id)
    path_epg_diff_dump = '%s/%ddiff.zip' % (
        os.path.dirname(path_source_file), instance.id)

    if (os.path.exists(path_epg_diff_dump)):
        print 'Deleting:', path_epg_diff_dump
    try:
        os.remove(path_source_file)
        os.remove(path_epg_full_dump)
        if (os.path.exists(path_epg_diff_dump)):
            os.remove(path_epg_diff_dump)
    except Exception as e:
        print 'Could not remove file:', e

signals.post_delete.connect(dvb_source_post_delete, sender=Epg_Source)
