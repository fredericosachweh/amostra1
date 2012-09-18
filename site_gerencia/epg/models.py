#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext as _

from dateutil import tz
from pytz import timezone
from datetime import datetime
import os


class Epg_Source(models.Model):
    "EPG source information"

    class Meta:
        permissions = (
            ("download_epg", _(u'Permissão para fazer download do EPG')),
        )

    filefield = models.FileField(_(u'Arquivo a ser importado'),
        upload_to='epg/')
    lastModification = models.DateTimeField(
        _(u'Data da última modificação no servidor da revista eletrônica'),
        unique=True)
    # Creation time
    created = models.DateTimeField(_(u'Data de criação'), auto_now=True)
    # Total number of elements in the file
    numberofElements = models.PositiveIntegerField(
        _(u'Número de elementos neste arquivo'),
        blank=True, null=True, default=0)
    # Number of imported elements
    #importedElements = models.PositiveIntegerField(
    #    _(u'Número de elementos ja importados'),
    #    blank=True, null=True, default=0)
    # Time diference between the smallest and the farthest time
    minor_start = models.DateTimeField(
        _(u'Menor tempo de inicio encontrado nos programas'),
        blank=True, null=True)
    major_stop = models.DateTimeField(
        _(u'Maior tempo de final encontrado nos programas'),
        blank=True, null=True)

    @property
    def minor_start_local(self):
        "Returns minimum start time converted to the local timezone"
        return self.minor_start.replace(tzinfo=timezone('UTC')).astimezone(tz.tzlocal())

    @property
    def major_stop_local(self):
        "Returns maxium stop time converted to the local timezone"
        return self.major_stop.replace(tzinfo=timezone('UTC')).astimezone(tz.tzlocal())


class XMLTV_Source(Epg_Source):
    "Information exclusive to XMLTV format"
    # Grabbed from <tv> element
    source_info_url = models.CharField(_(u'Source info url'),max_length=100, blank=True, null=True)
    source_info_name = models.CharField(_(u'Source info name'),max_length=100, blank=True, null=True)
    source_data_url = models.CharField(_(u'Source data url'),max_length=100, blank=True, null=True)
    generator_info_name = models.CharField(_(u'Generator info name'),max_length=100, blank=True, null=True)
    generator_info_url = models.CharField(_(u'Generator info url'),max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _(u'Arquivo XML/ZIP EPG')
        verbose_name_plural = _(u'Arquivos XML/ZIP EPG')

    def __unicode__(self):
        return 'ID: %d - Start: %s - Stop: %s' % (self.id, self.minor_start, self.major_stop)


class Lang(models.Model):
    value = models.CharField(max_length=10)


class Display_Name(models.Model):
    value = models.CharField(max_length=100)
    lang = models.ForeignKey(Lang, blank=True, null=True)

    def __unicode__(self):
        return self.value


class Icon(models.Model):
    src = models.CharField(max_length=10)


class Url(models.Model):
    value = models.CharField(max_length=200)


class Channel(models.Model):
    source = models.ForeignKey(Epg_Source)
    channelid = models.CharField(max_length=255, unique=True)
    display_names = models.ManyToManyField(Display_Name, blank=True, null=True)
    icons = models.ManyToManyField(Icon, blank=True, null=True)
    urls = models.ManyToManyField(Url, blank=True, null=True)

    def __unicode__(self):
        return u"%s [%s]" % (self.display_names.values_list()[0][1],
            self.channelid);


class Title(models.Model):
    value = models.CharField(max_length=128)
    lang = models.ForeignKey(Lang, blank=True, null=True)


class Description(models.Model):
    value = models.CharField(max_length=512, blank=True, null=True)
    lang = models.ForeignKey(Lang, blank=True, null=True)


class Staff(models.Model):
    name = models.CharField(max_length=512)


class Actor(models.Model):
    name = models.CharField(max_length=512)
    role = models.CharField(max_length=100, blank=True, null=True)


class Category(models.Model):
    value = models.CharField(max_length=100)
    lang = models.ForeignKey(Lang)


class Country(models.Model):
    value = models.CharField(max_length=100)


class Episode_Num(models.Model):
    value = models.CharField(max_length=100)
    system = models.CharField(max_length=100)


class Rating(models.Model):
    system = models.CharField(max_length=100)
    value = models.CharField(max_length=100)


class Language(models.Model):
    value = models.CharField(max_length=50)
    lang = models.ForeignKey(Lang, blank=True, null=True)


class Subtitle(models.Model):
    subtitle_type = models.CharField(max_length=20, blank=True, null=True)
    language = models.ForeignKey(Language, blank=True, null=True)


class Star_Rating(models.Model):
    value = models.CharField(max_length=10)
    system = models.CharField(max_length=100, blank=True, null=True)
    icons = models.ManyToManyField(Icon, blank=True, null=True)


class Programme(models.Model):
    source = models.ForeignKey(Epg_Source)
    programid = models.CharField(max_length=10, unique=True)
    titles = models.ManyToManyField(Title, related_name='titles', blank=True, null=True)
    secondary_titles = models.ManyToManyField(Title, related_name='secondary_titles', blank=True, null=True)
    descriptions = models.ManyToManyField(Description, blank=True, null=True)
    date = models.CharField(max_length=50,blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    episode_numbers = models.ManyToManyField(Episode_Num, blank=True, null=True)
    rating = models.ForeignKey(Rating, blank=True, null=True)
    language = models.ForeignKey(Language, related_name='language', blank=True, null=True)
    original_language = models.ForeignKey(Language, related_name='original_language', blank=True, null=True)
    length = models.PositiveIntegerField(blank=True, null=True)
    subtitles = models.ManyToManyField(Language, blank=True, null=True)
    star_ratings = models.ManyToManyField(Star_Rating, blank=True, null=True)
    # Video
    video_present = models.CharField(max_length=10,blank=True, null=True)
    video_colour = models.CharField(max_length=10,blank=True, null=True)
    video_aspect = models.CharField(max_length=10,blank=True, null=True)
    video_quality = models.CharField(max_length=10,blank=True, null=True)
    # Audio
    audio_present = models.CharField(max_length=10,blank=True, null=True)
    audio_stereo = models.CharField(max_length=10,blank=True, null=True)
    # Credits
    actors = models.ManyToManyField(Actor, blank=True, null=True)
    directors = models.ManyToManyField(Staff, related_name='director', blank=True, null=True)
    writers = models.ManyToManyField(Staff, related_name='writer', blank=True, null=True)
    adapters = models.ManyToManyField(Staff, related_name='adapter', blank=True, null=True)
    producers = models.ManyToManyField(Staff, related_name='producer', blank=True, null=True)
    composers = models.ManyToManyField(Staff, related_name='composer', blank=True, null=True)
    editors = models.ManyToManyField(Staff, related_name='editor', blank=True, null=True)
    presenters = models.ManyToManyField(Staff, related_name='presenter', blank=True, null=True)
    commentators = models.ManyToManyField(Staff, related_name='commentator', blank=True, null=True)
    guests = models.ManyToManyField(Staff, related_name='guest', blank=True, null=True)


class Guide(models.Model):
    source = models.ForeignKey(Epg_Source)
    programme = models.ForeignKey(Programme)
    channel = models.ForeignKey(Channel)
    start = models.DateTimeField(blank=True, null=True)
    stop = models.DateTimeField(blank=True, null=True)

# Signal used to delete the zip/xml file when a Epg_Source object is deleted from db
def dvb_source_post_delete(signal, instance, sender, **kwargs):
    # Delete the archive
    path_source_file = instance.filefield.path
    path_epg_full_dump = u'%s/%dfull.zip' % (
        os.path.dirname(path_source_file), instance.id)
    path_epg_diff_dump = u'%s/%ddiff.zip' % (
        os.path.dirname(path_source_file), instance.id)

    print '*********'
    print 'Deleting:', path_source_file
    print 'Deleting:', path_epg_full_dump
    if (os.path.exists(path_epg_diff_dump)):
        print 'Deleting:', path_epg_diff_dump
    print '*********'
    try:
        os.remove(path_source_file)
        os.remove(path_epg_full_dump)
        if (os.path.exists(path_epg_diff_dump)):
            os.remove(path_epg_diff_dump)
    except Exception as e:
        print 'Could not remove file:', e

signals.post_delete.connect(dvb_source_post_delete, sender=Epg_Source)
