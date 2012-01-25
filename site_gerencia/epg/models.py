from django.db import models
from django.db.models import signals

import logging
import zipfile
from lxml import etree
from datetime import tzinfo, timedelta, datetime
from dateutil.parser import parse
from types import NoneType

from sys import getrefcount
from guppy import hpy

class Arquivo(models.Model):
	filefield = models.FileField(upload_to='epg/')
	def __unicode__(self):
	        return self.filefield.path

class Epg(models.Model):
	generator_info_name = models.CharField(max_length=100)
	generator_info_url = models.CharField(max_length=100)

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

class XML_Epg_Importer:
	def __init__(self,input):
		self.input = input

	def __del__(self):
		print 'Um objeto XML_Epg_Importer vai ser deletado'

	def __get_or_create_lang(self,lang):
		if lang is None:
                	return None
        	L, created = Lang.objects.get_or_create(value=lang)
	        return L

	def parse_channel_elements(self,element_tree):
		for e in element_tree.iter('channel'):
			C, created = Channel.objects.get_or_create(channelid=e.get('id'),icon_src = e.find('icon').get('src'))
			for d in e.iter('display-name'):
				D, created = Display_Name.objects.get_or_create(value=d.text,lang=self.__get_or_create_lang(d.get('lang')))
				C.displays.add(D)
			C.save()

	def parse_programme_elements(self,element_tree):
		for e in element_tree.iter('programme'):
			chan, created = Channel.objects.get_or_create(channelid=e.get('channel'))
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

	def parse(self):
		if type(self.input) == str:
			# Input is string
			tree = etree.fromstring(self.input)
		else:
			# Input is a file-like object (provides a read method)
			tree = etree.parse(self.input)

		# Parse <channel> elements
		self.parse_channel_elements(tree)

		# Parse <programme> elements
		self.parse_programme_elements(tree)

def arquivo_post_save(signal, instance, sender, **kwargs):

	if instance.filefield is None:
		raise Exception('Empty uploaded file path')

	# TODO: Improve this handling
	path = str(instance.filefield.path)
	if path.endswith('xml'):
		file = open(path, 'r')
		obj = XML_Epg_Importer(file)
		obj.parse()
		file.close()
	elif path.endswith('zip'):
		z = zipfile.ZipFile(path, 'r')
		for f in z.namelist():
			file = z.open(f)
			obj = XML_Epg_Importer(file)
			obj.parse()
			file.close()
	else:
		raise Exception('Unknow file type to import')


signals.post_save.connect(arquivo_post_save, sender=Arquivo)

