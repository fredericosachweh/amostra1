#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.test import TestCase
from django.test.client import Client
import simplejson as json

from models import *
from data_importer import XML_Epg_Importer, Zip_to_XML

input_xml_1 = '''<?xml version="1.0" encoding="UTF-8"?>
		<tv generator-info-name="Revista Eletronica - Unidade Lorenz Ltda" generator-info-url="http://xmltv.revistaeletronica.com.br">
		<channel id="100">
		<display-name lang="pt">Concert Channel</display-name>
		<icon src="100.png" />
		</channel>
		<programme start="20120115220500 -0200" stop="20120115224500 -0200" channel="100" program_id="0000257856">
		<title lang="pt">BBC Sessions: The Verve</title>
		<title lang="en">BBC Sessions: Verve; The</title>
		<desc>Uma impressionante atuação do The Verve no famoso estúdio Maida Vale, da BBC. Desfrute desta íntima, porém poderosa gravação da banda de Richard Ashcroft, que inclui músicas como Bitter Sweet Symphony e Love is Noise. - www.revistaeletronica.com.br </desc>
		<date>2008</date>
		<category lang="pt">Espetáculo</category>
		<category lang="pt">Show</category>
		<video>
		<colour>yes</colour>
		</video>
		<rating system="Advisory">
		<value>Programa livre para todas as idades</value>
		</rating>
		</programme>
		</tv>
	'''

input_xml_2 = '''<?xml version="1.0" encoding="UTF-8"?>
		<tv generator-info-name="Revista Eletronica - Unidade Lorenz Ltda" generator-info-url="http://xmltv.revistaeletronica.com.br">
		<channel id="505">
		<display-name lang="pt">Band HD</display-name>
		<icon src="505.png" />
		</channel>
		<programme start="20120115234500 -0200" stop="20120116014500 -0200" channel="505" program_id="0000025536">
		<title lang="pt">Três Homens em Conflito</title>
		<title lang="en">The Good, The Bad and the Ugly</title>
		<desc>Durante a Guerra Civil Americana, três aventureiros tentam pôr as mãos numa fortuna. - www.revistaeletronica.com.br </desc>
		<credits>
		<director>Sergio Leone</director>
		<actor>Clint Eastwood</actor>
		<actor>Lee Van Cleef</actor>
		<actor>Eli Wallach</actor>
		<actor>Rada Rassimov</actor>
		<actor>Mario Brega</actor>
		</credits>
		<date>1966</date>
		<category lang="pt">Filme</category>
		<category lang="pt">Western</category>
		<country>Itália/Espanha</country>
		<video>
		<colour>yes</colour>
		</video>
		<rating system="Advisory">
		<value>Programa impróprio para menores de 14 anos</value>
		</rating>
		<star-rating>
		<value>5/5</value>
		</star-rating>
		</programme>
		</tv>
	'''

class Test_XML_to_db(object):

	def test_Epg_Source(self):
		from dateutil.parser import parse
		self.assertEquals(self.epg_source.generator_info_name, 'Revista Eletronica - Unidade Lorenz Ltda')
		self.assertEquals(self.epg_source.generator_info_url, 'http://xmltv.revistaeletronica.com.br')
		self.assertEquals(self.epg_source.minor_start, parse('20120116000500'))
		self.assertEquals(self.epg_source.major_stop, parse('20120116004500'))
		self.assertEquals(self.epg_source.numberofElements, 2)

	def test_Channel_1(self):
		channel = Channel.objects.get(channelid='100')
		self.assertEquals(channel.source, self.epg_source)
		self.assertEquals(channel.display_names.values_list('lang__value','value')[0], (u'pt',u'Concert Channel',))
		self.assertEquals(channel.icons.values_list('src')[0], (u'100.png',))
		self.assertEquals(channel.urls.count(), 0)

	def test_Programme_1(self):
		programme = Programme.objects.get(programid='0000257856')
		self.assertEquals(programme.source, self.epg_source)
		titles = [(u'pt', u'BBC Sessions: The Verve'),(u'en', u'BBC Sessions: Verve; The')]
		self.assertItemsEqual(programme.titles.values_list('lang__value', 'value'), titles)
		descs = (None, u'Uma impressionante atuação do The Verve no famoso estúdio Maida Vale, da BBC. Desfrute desta íntima, porém poderosa gravação da banda de Richard Ashcroft, que inclui músicas como Bitter Sweet Symphony e Love is Noise.')
		self.assertEquals(programme.descriptions.values_list('lang__value','value')[0], descs)
		self.assertEquals(programme.date, '2008')
		self.assertItemsEqual(programme.categories.values_list('lang__value', 'value'), [(u'pt',u'Espetáculo'),(u'pt', u'Show')])
		self.assertEquals(programme.video_colour, u'yes')
		self.assertEquals(programme.rating.system, u'Advisory')
		self.assertEquals(programme.rating.value, u'Programa livre para todas as idades')

class One_Raw_XML(Test_XML_to_db, TestCase):

	def setUp(self):
		from tempfile import NamedTemporaryFile
		from django.conf import settings
		import os
		MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
		self.f = NamedTemporaryFile(suffix='.xml', dir=os.path.join(MEDIA_ROOT, 'epg/'))
		self.f.write(input_xml_1)
		self.f.flush()
		self.epg_source = Epg_Source(filefield=self.f.name)
		self.epg_source.save()
		XML_Epg_Importer(xml=self.epg_source.filefield.path, epg_source_instance=self.epg_source).import_to_db()

	def tearDown(self):
		self.f.close()

	def test_Models_count(self):
		self.assertEquals(Channel.objects.all().count(), 1)
		self.assertEquals(Programme.objects.all().count(), 1)
		self.assertEquals(Guide.objects.all().count(), 1)

class One_Zipped_XML(Test_XML_to_db, TestCase):

	def setUp(self):
		from tempfile import NamedTemporaryFile
		from django.conf import settings
		import os
		MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
		self.f = NamedTemporaryFile(suffix='.xml', dir=os.path.join(MEDIA_ROOT, 'epg/'))
		from zipfile import ZipFile
		zipped = ZipFile( self.f.name[:-3] + 'zip', 'w' )
		zipped.writestr('xmltv.xml', input_xml_1)
		zipped.close()
		self.epg_source = Epg_Source(filefield=self.f.name[:-3] + 'zip')
		self.epg_source.save()
		file_list = Zip_to_XML(self.epg_source.filefield.path)
		for f in file_list.get_all_files():
			XML_Epg_Importer(xml=f,epg_source_instance=self.epg_source).import_to_db()

	def tearDown(self):
		self.f.close()

	def test_Models_count(self):
		self.assertEquals(Channel.objects.all().count(), 1)
		self.assertEquals(Programme.objects.all().count(), 1)
		self.assertEquals(Guide.objects.all().count(), 1)

class Two_Zipped_XMLs(Test_XML_to_db, TestCase):

	def setUp(self):
		from tempfile import NamedTemporaryFile
		from django.conf import settings
		import os
		MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
		self.f = NamedTemporaryFile(suffix='.zip', dir=os.path.join(MEDIA_ROOT, 'epg/'))
		from zipfile import ZipFile
		zipped = ZipFile( self.f, 'w' )
		zipped.writestr('100.xml', input_xml_1)
		zipped.writestr('505.xml', input_xml_2)
		zipped.writestr('101.xml', input_xml_1)
		zipped.writestr('506.xml', input_xml_2)
		zipped.close()
		self.epg_source = Epg_Source(filefield=self.f.name)
		self.epg_source.save()
		file_list = Zip_to_XML(self.epg_source.filefield.path)
		for f in file_list.get_all_files():
			XML_Epg_Importer(xml=f,epg_source_instance=self.epg_source).import_to_db()

	def tearDown(self):
		self.f.close()

	def test_Epg_Source(self):
		from dateutil.parser import parse
		self.assertEquals(self.epg_source.generator_info_name, 'Revista Eletronica - Unidade Lorenz Ltda')
		self.assertEquals(self.epg_source.generator_info_url, 'http://xmltv.revistaeletronica.com.br')
		self.assertEquals(self.epg_source.minor_start, parse('20120116000500'))
		self.assertEquals(self.epg_source.major_stop, parse('20120116034500'))
		self.assertEquals(self.epg_source.numberofElements, 8)

	def test_Models_count(self):
		self.assertEquals(Channel.objects.all().count(), 2)
		self.assertEquals(Programme.objects.all().count(), 2)
		self.assertEquals(Guide.objects.all().count(), 2)

	def test_Channel_2(self):
		channel = Channel.objects.get(channelid='505')
		self.assertEquals(channel.source, self.epg_source)
		self.assertEquals(channel.display_names.values_list('lang__value','value')[0], (u'pt',u'Band HD',))
		self.assertEquals(channel.icons.values_list('src')[0], (u'505.png',))
		self.assertEquals(channel.urls.count(), 0)

	def test_Programme_2(self):
		programme = Programme.objects.get(programid='0000025536')
		self.assertEquals(programme.source, self.epg_source)
		titles = [(u'pt', u'Três Homens em Conflito'),(u'en', u'The Good, The Bad and the Ugly')]
		self.assertItemsEqual(programme.titles.values_list('lang__value', 'value'), titles)
		descs = (None, u'Durante a Guerra Civil Americana, três aventureiros tentam pôr as mãos numa fortuna.')
		self.assertEquals(programme.descriptions.values_list('lang__value','value')[0], descs)
		self.assertEquals(programme.date, '1966')
		self.assertItemsEqual(programme.categories.values_list('lang__value', 'value'), [(u'pt',u'Filme'),(u'pt', u'Western')])
		self.assertEquals(programme.video_colour, u'yes')
		self.assertEquals(programme.rating.system, u'Advisory')
		self.assertEquals(programme.rating.value, u'Programa impróprio para menores de 14 anos')
		self.assertEquals(programme.country.value, u'Itália/Espanha')
		actors = ( ((u'Clint Eastwood'),), ((u'Lee Van Cleef'),), ((u'Eli Wallach'),), ((u'Rada Rassimov'),), ((u'Mario Brega'),), )
		self.assertItemsEqual(programme.actors.values_list('name'), actors)
		self.assertItemsEqual(programme.directors.values_list('name'), ( ((u'Sergio Leone'),), ))
		self.assertItemsEqual(programme.star_ratings.values_list('value'), ( ((u'5/5'),), ))

	def test_Channel_REST(self):
		c = Client()
		response = c.get('/tv/api/channels/')
		expected = [{'urls': [], 'channelid': '100', 'id': 1, 'display_names': [{'lang': {'value': 'pt'}, 'value': 'Concert Channel'}], \
		'icons': [{'src': '100.png'}], 'resource_uri' : '/tv/api/channels/1'}, \
		{'urls': [], 'channelid': '505', 'id': 2, 'display_names': [{'lang': {'value': 'pt'}, 'value': 'Band HD'}], 'icons': [{'src': '505.png'}],\
		 'resource_uri' : '/tv/api/channels/2'}]
		self.assertEquals(response.status_code, 200, msg=response.request)
		self.assertItemsEqual(json.loads(response.content), expected)
		# More tests
		test_cases = (
			{ 'expected' : expected,
			  'requests' : (('/tv/api/channels/', {}),
			  				('/tv/api/channels', {}),
			  				('/tv/api/channels/1,2/', {}),
			  				('/tv/api/channels/1,2', {}),
			  )
			},
			{ 'expected' : [expected[1]],
			  'requests' : (('/tv/api/channels/', {'channelid' : '505'}),
			  )
			},
		)

		for test in test_cases:
			for request in test['requests']:
				response = c.get(request[0], request[1])
				self.assertEquals(response.status_code, 200, msg=response.request)
				self.assertEquals(json.loads(response.content), test['expected'], msg=response.request)
		# Check for 404 if resource doesn't exists
		response = c.get('/tv/api/channels/3/')
		self.assertEquals(response.status_code, 404)

	def test_Programme_REST(self):
		c = Client()
		response = c.get('/tv/api/programmes/')
		expected = [{'rating': {'system': 'Advisory', 'value': 'Programa livre para todas as idades'}, \
		'presenters': [], 'titles': [{'lang': {'value': 'pt'}, 'value': 'BBC Sessions: The Verve'}, {'lang': {'value': 'en'}, 'value': 'BBC Sessions: Verve; The'}], \
		'guests': [], \
		'commentators': [], \
		'id': 1, \
		'composers': [], \
		'editors': [], \
		'writers': [], \
		'actors': [], \
		'subtitles': [], \
		'length': None, \
		'secondary_titles': [], \
		'episode_numbers': [], \
		'descriptions': \
		[{'value': u'Uma impressionante atuação do The Verve no famoso estúdio Maida Vale, da BBC. Desfrute desta íntima, porém poderosa gravação da banda de Richard Ashcroft, que inclui músicas como Bitter Sweet Symphony e Love is Noise.'}], \
		 'video_aspect': None, \
		 'date': '2008', \
		 'categories': [{'lang': {'value': 'pt'}, 'value': u'Espetáculo'}, {'lang': {'value': 'pt'}, 'value': 'Show'}], \
		 'audio_present': None, \
		 'video_present': None, \
		 'producers': [], \
		 'directors': [], \
		 'video_colour': 'yes', \
		 'video_quality': None, \
		 'adapters': [], \
		 'audio_stereo': None,
		 'resource_uri' : '/tv/api/programmes/1'}, \
		 {'rating': {'system': 'Advisory', 'value': u'Programa impróprio para menores de 14 anos'}, \
		 'presenters': [], \
		 'titles': [{'lang': {'value': 'pt'}, 'value': u'Três Homens em Conflito'}, \
		 	{'lang': {'value': 'en'}, 'value': 'The Good, The Bad and the Ugly'}], \
		 'guests': [], \
		 'commentators': [], \
		 'id': 2, \
		 'composers': [], \
		 'editors': [], \
		 'writers': [], \
		 'actors': [{'role': None, 'name': 'Clint Eastwood'}, {'role': None, 'name': 'Lee Van Cleef'}, {'role': None, 'name': 'Eli Wallach'}, \
		 	{'role': None, 'name': 'Rada Rassimov'}, {'role': None, 'name': 'Mario Brega'}], \
		 'subtitles': [], \
		 'length': None, \
		 'secondary_titles': [], \
		 'episode_numbers': [], \
		 'descriptions': [{'value': u'Durante a Guerra Civil Americana, três aventureiros tentam pôr as mãos numa fortuna.'}], \
		 'video_aspect': None, \
		 'date': '1966', \
		 'categories': [{'lang': {'value': 'pt'}, 'value': 'Filme'}, {'lang': {'value': 'pt'}, 'value': 'Western'}], \
		 'audio_present': None, 'video_present': None, \
		 'producers': [], \
		 'country': {'value': u'Itália/Espanha'}, \
		 'directors': [{'name': 'Sergio Leone'}], \
		 'video_colour': 'yes', \
		 'video_quality': None, \
		 'adapters': [], \
		 'audio_stereo': None, \
		 'resource_uri' : '/tv/api/programmes/2'}]
		self.assertEquals(response.status_code, 200, msg=response.request)
		self.assertItemsEqual(json.loads(response.content), expected)
		# More tests
		test_cases = (
			{ 'expected' : expected,
			  'requests' : (('/tv/api/programmes/', {}),
			  				('/tv/api/programmes', {}),
			  				('/tv/api/programmes/', {'video_colour' : 'yes'}),
			  				('/tv/api/programmes/1,2/', {}),
			  				('/tv/api/programmes/1,2', {}),
			  				('/tv/api/programmes/1,2/', {'video_colour' : 'yes'}),
			  				('/tv/api/programmes/1,2', {'video_colour' : 'yes'}),
			  )
			},
			{ 'expected' : [expected[1]],
			  'requests' : (('/tv/api/programmes/', {'actors' : 'Clint Eastwood'}),
			  )
			},
		)

		for test in test_cases:
			for request in test['requests']:
				response = c.get(request[0], request[1])
				self.assertEquals(response.status_code, 200, msg=response.request)
				self.assertEquals(json.loads(response.content), test['expected'], msg=response.request)
		# Check for 404 if resource doesn't exists
		response = c.get('/tv/api/programmes/3/')
		self.assertEquals(response.status_code, 404)

	def test_Guide_REST(self):	    
		c = Client()
		test_cases = (
		# First programme
			{ 'expected' : [{'id' : 1, 'start': '2012-01-16 00:05:00', 'programme_id': 1, 'stop': '2012-01-16 00:45:00', 'channel_id': 1, 'resource_uri' : '/tv/api/guide/1'},],
			  'requests' : (('/tv/api/guide/', {'start' : '20120116000500', 'stop' : '20120116004500'}),
			  				('/tv/api/guide/', {'stop' : '20120116004500'}),
			  				('/tv/api/guide/', {'start' : '20120116000600', 'stop' : '20120116004400'}),
			  				('/tv/api/guide/', {'stop' : '20120116004400'}),
			  				('/tv/api/guide/channels/1/', {}),
			  				('/tv/api/guide/channels/1', {}),
							('/tv/api/guide/channels/1/', {'start' : '20120116000500', 'stop' : '20120116004500'}),
							('/tv/api/guide/channels/1', {'start' : '20120116000500', 'stop' : '20120116004500'}),
			  				('/tv/api/guide/programmes/1/', {}),
			  				('/tv/api/guide/programmes/1', {}),
			  				('/tv/api/guide/programmes/1/', {'start' : '20120116000500', 'stop' : '20120116004500'}),
			  				('/tv/api/guide/programmes/1', {'start' : '20120116000500', 'stop' : '20120116004500'}),
			  				# Pagination
			  				('/tv/api/guide/', {'limit' : '1', 'page' : '1'}),
			  )
			},
		# Second programme
			{ 'expected' : [{'id' : 2, 'start': '2012-01-16 01:45:00', 'programme_id': 2, 'stop': '2012-01-16 03:45:00', 'channel_id': 2, 'resource_uri' : '/tv/api/guide/2'},],
			  'requests' : (('/tv/api/guide/', {'start' : '20120116014500', 'stop' : '20120116034500'}),
			  				('/tv/api/guide/', {'start' : '20120116014500'}),
			  				('/tv/api/guide/channels/2/', {}),
			  				('/tv/api/guide/channels/2', {}),
							('/tv/api/guide/channels/2/', {'start' : '20120116014500', 'stop' : '20120116034500'}),
							('/tv/api/guide/channels/2', {'start' : '20120116014500', 'stop' : '20120116034500'}),
			  				('/tv/api/guide/programmes/2/', {}),
			  				('/tv/api/guide/programmes/2', {}),
			  				('/tv/api/guide/programmes/2/', {'start' : '20120116014500', 'stop' : '20120116034500'}),
			  				('/tv/api/guide/programmes/2', {'start' : '20120116014500', 'stop' : '20120116034500'}),
			  				# Pagination
			  				('/tv/api/guide/', {'limit' : '1', 'page' : '2'}),
			  )
			},
		# Both programmes
			{ 'expected' : [{'id' : 1, 'start': '2012-01-16 00:05:00', 'programme_id': 1, 'stop': '2012-01-16 00:45:00', 'channel_id': 1, 'resource_uri' : '/tv/api/guide/1'},
							{'id' : 2, 'start': '2012-01-16 01:45:00', 'programme_id': 2, 'stop': '2012-01-16 03:45:00', 'channel_id': 2, 'resource_uri' : '/tv/api/guide/2'},],
			  'requests' : (('/tv/api/guide/', {'start' : '20120116000500', 'stop' : '20120116034500'}),
			  				('/tv/api/guide/', {'stop' : '20120116034500'}),
			  				('/tv/api/guide/', {'stop' : '20120116034400'}),
			  				('/tv/api/guide/', {'start' : '20120116000600', 'stop' : '20120116034400'}),
			  				('/tv/api/guide/', {'start' : '20120116000600'}),
			  				('/tv/api/guide/channels/1,2/', {}),
			  				('/tv/api/guide/channels/1,2', {}),
							('/tv/api/guide/channels/1,2/', {'start' : '20120116000500', 'stop' : '20120116034500'}),
							('/tv/api/guide/channels/1,2', {'start' : '20120116000500', 'stop' : '20120116034500'}),
			  				('/tv/api/guide/programmes/1,2/', {}),
			  				('/tv/api/guide/programmes/1,2', {}),
			  				('/tv/api/guide/programmes/1,2/', {'start' : '20120116000500', 'stop' : '20120116034500'}),
			  				('/tv/api/guide/programmes/1,2', {'start' : '20120116000500', 'stop' : '20120116034500'}),
			  				# Pagination
			  				('/tv/api/guide/', {'limit' : '2', 'page' : '1'}),
			  )
			},
		)

		for test in test_cases:
			for request in test['requests']:
				response = c.get(request[0], request[1])
				self.assertEquals(response.status_code, 200, msg=response.__dict__)
				self.assertEquals(json.loads(response.content), test['expected'])


