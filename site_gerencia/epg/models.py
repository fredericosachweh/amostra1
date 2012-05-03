#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.db import models
from django.db.models import signals

from django.utils.translation import ugettext as _

from dateutil import tz
from pytz import timezone

class Epg_Source(models.Model):

	class Meta:
		verbose_name = _(u'Arquivo XML/ZIP EPG')
		verbose_name_plural = _(u'Arquivos XML/ZIP EPG')
		
	filefield = models.FileField(_(u'Arquivo a ser importado'),upload_to='epg/')
	# Grabbed from <tv> element
	source_info_url = models.CharField(_(u'Source info url'),max_length=100, blank=True, null=True)
	source_info_name = models.CharField(_(u'Source info name'),max_length=100, blank=True, null=True)
	source_data_url = models.CharField(_(u'Source data url'),max_length=100, blank=True, null=True)
	generator_info_name = models.CharField(_(u'Generator info name'),max_length=100, blank=True, null=True)
	generator_info_url = models.CharField(_(u'Generator info url'),max_length=100, blank=True, null=True)
	# Time diference between the smallest and the farthest time
	minor_start = models.DateTimeField(_(u'Menor tempo de inicio encontrado nos programas'),blank=True, null=True)
	major_stop = models.DateTimeField(_(u'Maior tempo de final encontrado nos programas'),blank=True, null=True)
	# Total number of elements in the file
	numberofElements = models.PositiveIntegerField(_(u'Número de elementos neste arquivo'),blank=True, null=True, default=0)
	# Number of imported elements
	importedElements = models.PositiveIntegerField(_(u'Número de elementos ja importados'),blank=True, null=True, default=0)
	# Creation time
	created = models.DateTimeField(_(u'Data de criação'), auto_now=True)
	
	def _get_start_local(self):
		"Returns minimum start time converted to the local timezone"
		return self.minor_start.replace(tzinfo=timezone('UTC')).astimezone(tz.tzlocal())
	minor_start_local = property(_get_start_local)

	def _get_stop_local(self):
		"Returns maxium stop time converted to the local timezone"
		return self.major_stop.replace(tzinfo=timezone('UTC')).astimezone(tz.tzlocal())
	major_stop_local = property(_get_stop_local)

	def __unicode__(self):
		return 'ID: %d - Start: %s - Stop: %s' % (self.id, self.minor_start, self.major_stop)

	def save(self, *args, **kwargs):

		# It's necessary to get the real file path
		# Call the "real" save() method.
		super(Epg_Source, self).save(*args, **kwargs)

		# Check if there is need to update the following fields
		if self.numberofElements > 0:
			return
		
		from data_importer import get_info_from_epg_source
		get_info_from_epg_source(self)

		# Call the "real" save() method.
		super(Epg_Source, self).save(*args, **kwargs)

class Lang(models.Model):
	value = models.CharField(max_length=10)

class Display_Name(models.Model):
	value = models.CharField(max_length=100)
	lang = models.ForeignKey(Lang, blank=True, null=True)

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
		return u"%s [%s]" % (self.display_names.values_list()[0][1], self.channelid);

class Title(models.Model):
	value = models.CharField(max_length=100)
	lang = models.ForeignKey(Lang, blank=True, null=True)

class Description(models.Model):
	value = models.CharField(max_length=500, blank=True, null=True)
	lang = models.ForeignKey(Lang, blank=True, null=True)

class Staff(models.Model):
	name = models.CharField(max_length=100)

class Actor(models.Model):
	name = models.CharField(max_length=100)
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
	programid = models.CharField(max_length=10)
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
	import os
	# Delete the archive
	path = str(instance.filefield.path)
	print '*********'
	print 'Deleting:', path
	print '*********'
	try:
		os.remove(path)
	except:
		print 'Could not remove the file:', path
			
signals.post_delete.connect(dvb_source_post_delete, sender=Epg_Source)
