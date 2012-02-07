#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.db import models
from django.db.models import signals

from django.utils.translation import ugettext as _

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
	numberofElements = models.PositiveIntegerField(_(u'Número de elementos neste arquivo'),blank=True, null=True)
	# Number of imported elements
	importedElements = models.PositiveIntegerField(_(u'Número de elementos ja importados'),blank=True, null=True)
	
	def __unicode__(self):
		return self.filefield.path

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
	lang = models.ForeignKey(Lang)

class Channel(models.Model):
	source = models.ForeignKey(Epg_Source)
	channelid = models.CharField(max_length=3)
	displays = models.ManyToManyField(Display_Name, blank=True, null=True)
	icon_src = models.CharField(max_length=10)

class Title(models.Model):
	value = models.CharField(max_length=100)
	lang = models.ForeignKey(Lang)

class Sub_Title(models.Model):
	value = models.CharField(max_length=100)
	lang = models.ForeignKey(Lang)

class Director(models.Model):
	name = models.CharField(max_length=100)

class Actor(models.Model):
	name = models.CharField(max_length=100)
	
class Category(models.Model):
	value = models.CharField(max_length=100)
	lang = models.ForeignKey(Lang)

class Country(models.Model):
	value = models.CharField(max_length=100)

class Episode_Num(models.Model):
	value = models.CharField(max_length=100)
	system = models.CharField(max_length=100)

class Video(models.Model):
	color = models.CharField(max_length=10)
	aspect = models.CharField(max_length=10)

class Rating(models.Model):
	system = models.CharField(max_length=100)
	value = models.CharField(max_length=100)

class Programme(models.Model):
	source = models.ForeignKey(Epg_Source)
	start = models.DateTimeField()
	stop = models.DateTimeField()
	channel = models.ForeignKey(Channel)
	programid = models.CharField(max_length=10)
	titles = models.ManyToManyField(Title, blank=True, null=True)
	sub_titles = models.ManyToManyField(Sub_Title, blank=True, null=True)
	desc = models.CharField(max_length=500, blank=True, null=True)
	date = models.DateField(blank=True, null=True)
	categories = models.ManyToManyField(Category, blank=True, null=True)
	country = models.ForeignKey(Country, blank=True, null=True)
	episode_numbers = models.ManyToManyField(Episode_Num, blank=True, null=True)
	video = models.ForeignKey(Video, blank=True, null=True)
	rating = models.ForeignKey(Rating, blank=True, null=True)
	directors = models.ManyToManyField(Director, blank=True, null=True)
	actors = models.ManyToManyField(Actor, blank=True, null=True)

# Signal used to delete the zip/xml file when a Epg_Source object is deleted from db
def arquivo_post_delete(signal, instance, sender, **kwargs):
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
			
signals.post_delete.connect(arquivo_post_delete, sender=Epg_Source)
