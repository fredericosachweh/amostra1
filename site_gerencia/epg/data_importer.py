#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import zipfile
from lxml import etree
from django.db import transaction
from datetime import tzinfo, timedelta, datetime
from dateutil.parser import parse
from types import NoneType

from models import *

#from profilehooks import profile

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

	# Return one or multiple XML file handles inside a Zip archive
	def _get_zip(self):
		ret = []
		for f in self.input_file.namelist():
			ret.append(self.input_file.open(f))
		return ret
	
	# Return a file handle of a XML file
	def _get_xml(self):
		return open(self.input_file)
			
class XML_Epg_Importer:

	def __init__(self,xml,epg_source_instance):
	
		self._epg_source_instance=epg_source_instance
		if type(xml) == str:
			# Input is string
			self.tree = etree.fromstring(xml)
		else:
			# Input is a file-like object (provides a read method)
			self.tree = etree.parse(xml)

	def count_channel_elements(self):
		return len( self.tree.findall('channel') )
	
	def count_programme_elements(self):
		return len( self.tree.findall('programme') )

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
		if isinstance(self._epg_source_instance,Epg_Source):
			self._epg_source_instance.importedElements += 1
			self._epg_source_instance.save()

	@transaction.commit_on_success
	def _decrement_importedElements(self):
		if isinstance(self._epg_source_instance,Epg_Source) and self._epg_source_instance.importedElements > 0:
			self._epg_source_instance.importedElements -= 1
			self._epg_source_instance.save()

	def _get_dict_for_langs(self):
		# Search for lang attributes in the xml
		lang_set = set()
		for l in self.tree.findall(".//*[@lang]"):
			lang_set.add(l.get('lang'))	# Auto exclude dupplicates
		langs = dict()
		for lang in lang_set:
			L, created = Lang.objects.get_or_create(value=lang)
			langs[lang]=L
		return langs

	def import_channel_elements(self):
	
		# Search for lang attributes in the xml
		langs = self._get_dict_for_langs()
	
		for e in self.tree.iter('channel'):
			print '***********************************************************************************************'
			try:
				C = Channel.objects.only('channelid').get(channelid=e.get('id'))
				continue
			except:
				C = Channel.objects.create(source=self._epg_source_instance, \
														icon_src = e.find('icon').get('src'), \
														channelid=e.get('id'))
			displays = []
			for d in e.iter('display-name'):
				D, created = Display_Name.objects.get_or_create(value=d.text,lang=langs[d.get('lang')])
				displays.append(D)
			
			if len(displays) > 0:
				C.displays.add(*displays)
			# Update Arquivo_Epg instance, for the progress bar
			#self._increment_importedElements()
		
	def import_programme_elements(self):
	
		# Get channels from db
		channels = dict()
		for c in Channel.objects.only('channelid'):
			channels[c.channelid] = c
		# Search for lang attributes in the xml
		langs = self._get_dict_for_langs()
		
		for e in self.tree.iter('programme'):
			print '***********************************************************************************************'
			# Try to get a date element, if availble
			try:
				date=parse(e.find('date').text)
			except:
				date=None

			# Try to find the programme in db
			try:
				P = Programme.objects.only('programid').get(programid=e.get('program_id'))
				continue
			except:
				# MySQL backend does not support timezone-aware datetimes. That's why I'm cutting off this information.
				P = Programme.objects.create(programid=e.get('program_id'), \
															desc=e.find('desc').text, \
															date=date,
															source=self._epg_source_instance)

			# Get titles
			for t in e.iter('title'):
				T, created = Title.objects.get_or_create(value=t.text,lang=langs[t.get('lang')])
				P.titles.add(T)
			# Get Sub titles
			for st in e.iter('sub-title'):
				ST, created = Sub_Title.objects.get_or_create(value=st.text,lang=langs[t.get('lang')])
				P.sub_titles.add(ST)
			# Get categories
			for c in e.iter('category'):
				C, created = Category.objects.get_or_create(value=c.text,lang=langs[t.get('lang')])
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

			# Update Epg_Source instance, for the progress bar
			#self._increment_importedElements()

	def import_exibition_times(self):

		channels = dict()
		programmes = dict()
		
		for c in list(Channel.objects.only('channelid').filter(source=self._epg_source_instance)):
			channels[c.channelid] = c
			
		for p in list(Programme.objects.only('programid').filter(source=self._epg_source_instance)):
			programmes[p.programid] = p
		
		for e in self.tree.iter('programme'):
			print '***********************************************************************************************'
			try:
				c = channels[e.get('channel')]
				p = programmes[e.get('program_id')]
			except:
				continue
			G, created = Guide.objects.get_or_create(source=self._epg_source_instance, \
																	channel=c, \
																	programme=p, \
																	start=parse(e.get('start')[0:-6]), \
																	stop=parse(e.get('stop')[0:-6]))
			
	@transaction.commit_on_success
	def import_to_db(self):
		# Import <channel> elements
		self.import_channel_elements()
		# Import <programme> elements
		self.import_programme_elements()
		# Import exibiton times
		self.import_exibition_times()
		
	def delete_from_db(self):
		# Delete <programme> elements
		Programme.objects.filter(source=self._epg_source_instance).delete()
		# Delete <channel> elements
		Channel.objects.filter(source=self._epg_source_instance).delete()
		# TODO: Maybe put inside a transaction, but I don't know if it's necessary
		deleteElements = self._epg_source_instance.importedElements
		self._epg_source_instance.importedElements = 0
		self._epg_source_instance.save()
		return deleteElements
		
def get_info_from_epg_source(epg_source):

	# Update Epg_Source fields
	numberofElements = 0
	file_list = Zip_to_XML(epg_source.filefield.path)
	for f in file_list.get_all_files():
		importer = XML_Epg_Importer(f,epg_source_instance=epg_source)
		numberofElements += importer.get_number_of_elements()
		f.close()

	# Update Epg_Source fields
	epg_source.numberofElements = numberofElements
	epg_source.importedElements = 0
	epg_source.minor_start, epg_source.major_stop = importer.get_period_of_the_file()
	info = importer.get_xml_info()
	epg_source.source_info_url = info['source_info_url']
	epg_source.source_info_name = info['source_info_name']
	epg_source.source_data_url = info['source_data_url']
	epg_source.generator_info_name = info['generator_info_name']
	epg_source.generator_info_url = info['generator_info_url']
