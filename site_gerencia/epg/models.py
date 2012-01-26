#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.db import models
from django.db import transaction
from django.db.models import signals
from django import db
from django.core.files.storage import FileSystemStorage

from django.utils.translation import ugettext as _
import logging
import zipfile
from lxml import etree
from datetime import tzinfo, timedelta, datetime
from dateutil.parser import parse
from types import NoneType

from sys import getrefcount
from guppy import hpy

class Arquivo_Epg(models.Model):

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
		super(Arquivo_Epg, self).save(*args, **kwargs)

		if self.numberofElements > 0:
			return

		path = str(self.filefield.path)
		numberofElements = 0
		if path.endswith('xml'):
			file = open(path, 'r')
			obj = XML_Epg_Importer(file)
			numberofElements += obj.get_number_of_elements()
			file.close()
		elif path.endswith('zip'):
			z = zipfile.ZipFile(path, 'r')
			for f in z.namelist():
				file = z.open(f)
				obj = XML_Epg_Importer(file)
				numberofElements += obj.get_number_of_elements()
				file.close()
		else:
			raise Exception('Unknow file type to import')

		# Update Arquivo_Epg fields
		self.numberofElements = numberofElements
		self.minor_start, self.major_stop = obj.get_period_of_the_file()
		info = obj.get_xml_info()
		self.source_info_url = info['source_info_url']
		self.source_info_name = info['source_info_name']
		self.source_data_url = info['source_data_url']
		self.generator_info_name = info['generator_info_name']
		self.generator_info_url = info['generator_info_url']

		# Call the "real" save() method.
		super(Arquivo_Epg, self).save(*args, **kwargs)

class Lang(models.Model):
	value = models.CharField(max_length=10)

class Display_Name(models.Model):
	value = models.CharField(max_length=100)
	lang = models.ForeignKey(Lang)

class Channel(models.Model):
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

class Zip_to_XML:
	def __init__(self,input_file_path):
		import mimetypes
		file_type, encoding = mimetypes.guess_type(input_file_path)
		if file_type == 'application/zip':
			self.input_file = zipfile.ZipFile(input_file_path, 'r')
			self.get_all_files = self._get_zip
		elif file_type == 'application/xhtml+xml':
			self.input_file = input_file_path
			self.get_all_files = self._get_xml
		else:
			raise Exception('Unkown type of file to import')

	def _get_zip(self):
		ret = []
		for f in self.input_file.namelist():
			ret.append(self.input_file.open(f))
		return ret

	def _get_xml(self):
		return open(self.input_file)
			
class XML_Epg_Importer:
	def __init__(self,xml,arquivo_epg_instance=None):
		self._arquivo_epg_instance=arquivo_epg_instance
		if type(xml) == str:
			# Input is string
			print 'XML_Epg_Importer arg was a string:', self
			self.tree = etree.fromstring(xml)
		else:
			# Input is a file-like object (provides a read method)
			print 'XML_Epg_Importer arg was a file-like object:', self
			self.tree = etree.parse(xml)

	def __del__(self):
		print '********************************************'
		print 'Um objeto XML_Epg_Importer vai ser deletado:', self
		print '********************************************'

	def __get_or_create_lang(self,lang):
		if lang is None:
                	return None
        	L, created = Lang.objects.get_or_create(value=lang)
	        return L

	def count_channel_elements(self):
		count = 0
		for e in self.tree.iter('channel'):
			count = count + 1
		return count
	
	def count_programme_elements(self):
		count = 0
		for e in self.tree.iter('programme'):
			count = count + 1
		return count

	def get_number_of_elements(self):
		return self.count_channel_elements() + self.count_programme_elements()

	def get_period_of_the_file(self):
		minor_start = parse(self.tree.find('programme').get('start')[0:-6])
		major_stop = parse(self.tree.find('programme').get('stop')[0:-6])
		for e in self.tree.iter('programme'):
			start = parse(e.get('start')[0:-6])
			stop=parse(e.get('stop')[0:-6])
			if minor_start > start:
				minor_start=start
			if major_stop < stop:
				major_stop=stop
		return minor_start,major_stop
			
	def get_xml_info(self):
		tv = self.tree.getroot()
		return { 'source_info_url' : tv.get('source-info-url'), \
			'source_info_name' : tv.get('source-info-name'), \
			'source_data_url' : tv.get('source-data-url'), \
			'generator_info_name' : tv.get('generator-info-name'), \
			'generator_info_url' : tv.get('generator-info-url') }

	@transaction.commit_on_success
	def _increment_importedElements(self):
		if isinstance(self._arquivo_epg_instance,Arquivo_Epg):
			self._arquivo_epg_instance.importedElements = 1 + self._arquivo_epg_instance.importedElements
			self._arquivo_epg_instance.save()

	def parse_channel_elements(self):
		for e in self.tree.iter('channel'):
			C, created = Channel.objects.get_or_create(channelid=e.get('id'),icon_src = e.find('icon').get('src'))
			for d in e.iter('display-name'):
				D, created = Display_Name.objects.get_or_create(value=d.text,lang=self.__get_or_create_lang(d.get('lang')))
				C.displays.add(D)
			C.save()
			# Update Arquivo_Epg instance, for the progress bar
                        self._increment_importedElements()

	def parse_programme_elements(self):
		for e in self.tree.iter('programme'):
			# Get the channel object
			try:
				chan = Channel.objects.get(channelid=e.get('channel'))
			except:
				raise Exception('Trying to create a programme from a channel that wasn\'t created yet')
			# Try to get a date element, if availble
			try:
				date=parse(e.find('date').text)
			except:
				date=None
			# MySQL backend does not support timezone-aware datetimes. That's why I'm cutting off this information.
			P, created = Programme.objects.get_or_create(start=parse(e.get('start')[0:-6]), \
								stop=parse(e.get('stop')[0:-6]), \
								channel=chan, \
								programid=e.get('program_id'), \
								desc=e.find('desc').text, \
								date=date, \
								)
			# Get titles
			for t in e.iter('title'):
				T, created = Title.objects.get_or_create(value=t.text,lang=self.__get_or_create_lang(t.get('lang')))
				P.titles.add(T)
			# Get Sub titles
			for st in e.iter('sub-title'):
				ST, created = Sub_Title.objects.get_or_create(value=st.text,lang=self.__get_or_create_lang(st.get('lang')))
				P.sub_titles.add(ST)
			# Get categories
			for c in e.iter('category'):
				C, created = Category.objects.get_or_create(value=c.text,lang=self.__get_or_create_lang(c.get('lang')))
				P.categories.add(C)
			# Get video element
			try:
				color=e.find('video').find('colour').text
			except:
				color=None
			if color is not None:
				V, created = Video.objects.get_or_create(color=e.find('video').find('colour').text)
				P.video=V
			# Get country element
			try:
				country=e.find('country').text
			except:
				country=None
			if country is not None:
				Ct, created = Country.objects.get_or_create(value=country)
				P.country=Ct
			# Get rating
			try:
				system=e.find('rating').get('system')
				value=e.find('rating').find('value').text
			except:
				system=None
				value=None
			if (system is not None) and (value is not None):
				R, created = Rating.objects.get_or_create(system=system,value=value)
				P.rating=R
			# Get credits
			if type(e.find('credits')) is not NoneType:
				for d in e.find('credits').iter('director'):
					D, created = Director.objects.get_or_create(name=d.text)
					P.directors.add(D)
				for a in e.find('credits').iter('actor'):
					A, created = Actor.objects.get_or_create(name=a.text)
					P.actors.add(A)

			# Save relationship modifications
			P.save()
			# Update Arquivo_Epg instance, for the progress bar
			self._increment_importedElements()

	def parse(self):
		# Parse <channel> elements
		self.parse_channel_elements()
		# Parse <programme> elements
		self.parse_programme_elements()

		print '*****************************'
		print 'Number of processed elements:', self.get_number_of_elements()
		print '*****************************'

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
			
signals.post_delete.connect(arquivo_post_delete, sender=Arquivo_Epg)
