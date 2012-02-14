#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.test import TestCase

from models import *
from data_importer import XML_Epg_Importer, Zip_to_XML

input_xml = '''<?xml version="1.0" encoding="ISO-8859-1"?>
		<tv generator-info-name="Revista Eletronica - Unidade Lorenz Ltda" generator-info-url="http://xmltv.revistaeletronica.com.br">
		<channel id="100">
		<display-name lang="pt">Concert Channel</display-name>
		<icon src="100.png" />
		</channel>
		<programme start="20120116000500 -0200" stop="20120116004500 -0200" channel="100" program_id="0000257856">
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

class Test_XML_to_db(TestCase):

	def setUp(self):
		from tempfile import NamedTemporaryFile
		from django.conf import settings
		import os
		MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
		self.f = NamedTemporaryFile(suffix='.xml', dir=os.path.join(MEDIA_ROOT, 'epg/'))
		self.f.write(input_xml)
		self.f.flush()
		self.epg_source = Epg_Source(filefield=self.f.name)
		self.epg_source.save()
		XML_Epg_Importer(xml=self.epg_source.filefield.path, epg_source_instance=self.epg_source).import_to_db()

	def tearDown(self):
		self.f.close()

	def test_Epg_Source(self):
		from dateutil.parser import parse
		self.assertEquals(self.epg_source.generator_info_name, 'Revista Eletronica - Unidade Lorenz Ltda')
		self.assertEquals(self.epg_source.generator_info_url, 'http://xmltv.revistaeletronica.com.br')
		self.assertEquals(self.epg_source.minor_start, parse('20120116000500'))
		self.assertEquals(self.epg_source.major_stop, parse('20120116004500'))
		self.assertEquals(self.epg_source.numberofElements, 2)
	
	def test_Channels(self):
		channels = Channel.objects.all()
		self.assertEquals(channels.count(), 1)
		self.assertEquals(channels[0].channelid, '100')
		self.assertEquals(channels[0].display_names.values_list('lang__value','value')[0], (u'pt',u'Concert Channel',))
		self.assertEquals(channels[0].icons.values_list('src')[0], (u'100.png',))
		self.assertEquals(channels[0].urls.count(), 0)
		


