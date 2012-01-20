from django.db import models
from django.db.models import signals

import zipfile
from lxml import etree
from datetime import tzinfo, timedelta, datetime
from dateutil.parser import parse

class Arquivo(models.Model):
	path = models.FileField(upload_to='epg/')
	def __unicode__(self):
	        return self.path.path

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
	class Credit:
		directors = models.ManyToManyField(Director, blank=True, null=True)
		actors = models.ManyToManyField(Actor, blank=True, null=True)

def get_or_create_lang(lang):
	if lang is None:
		return None
	L, created = Lang.objects.get_or_create(value=lang)
	return L

def arquivo_post_save(signal, instance, sender, **kwargs):

	if instance.path is None:
		return

	z = zipfile.ZipFile(instance.path)
	
	try:
		file = z.open('xmltv.xml')
	except:
		print "File xmltv.xml wasnt found"
		return
	
	tree = etree.parse(file)
	file.close()

	for e in tree.findall('channel'):
		C, created = Channel.objects.get_or_create(channelid=e.get('id'),icon_src = e.find('icon').get('src'))
		for d in e.findall('display-name'):
			D, created = Display_Name.objects.get_or_create(value=d.text,lang=get_or_create_lang(d.get('lang')))
			C.displays.add(D)
		C.save()

	for e in tree.findall('programme'):
		#programme = Programme()
		# MySQL backend does not support timezone-aware datetimes. That's why I'm cutting off this information.
		#programme.start=parse(e.get('start')[0:-6]
		#programme.stop=parse(e.get('stop')[0:-6]
		chan, created = Channel.objects.get_or_create(channelid=e.get('channel'))
		#programme.channel=chan
		
		#titles = list()
		#for t in e.find('title'):
		#	title, foo = Title.objects.get_or_create(lang=t.get('lang'), value=t.text)
		#	titles.append(title)
		try:
			date=parse(e.find('date').text)
		except:
			date=parse('')
		# MySQL backend does not support timezone-aware datetimes. That's why I'm cutting off this information.
		P, created = Programme.objects.get_or_create(start=parse(e.get('start')[0:-6]), \
							stop=parse(e.get('stop')[0:-6]), \
							channel=chan, \
							programid=e.get('program_id'), \
							desc=e.find('desc').text, \
							date=date, \
							)
def gambi():
        inst = Arquivo(path='/tmp/xmltv.zip')
        arquivo_post_save(signal=False, instance=inst, sender=False)

signals.post_save.connect(arquivo_post_save, sender=Arquivo)

