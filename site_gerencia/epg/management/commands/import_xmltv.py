#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management import BaseCommand
from optparse import make_option

class Command(BaseCommand):

	base_url = "http://xmltv.revistaeletronica.com.br/wp/?page_id=36"
	
	help = 'Automatically fetch and import a xmltv file to the EPG database'

	option_list = BaseCommand.option_list + (
        make_option('--force',
            action='store_true',
            dest='forced',
            default=False,
            help='Force importation even if the xmltv file already exists'),
        )

	def handle(self, forced, **kwargs):
		from urllib2 import URLError
		from urllib2 import HTTPError
		import urllib2

		self.stdout.write('Getting HTML...\n')
		try:
			request = urllib2.Request(self.base_url)

			# Abre a conexão
			fd = urllib2.urlopen(request)

			# Efetua a leitura do conteúdo.
			content = fd.read()
			fd.close()

		except HTTPError, e:
			self.stdout.write("Ocorreu um erro ao requisitar o conteúdo do servidor!\n")
			self.stdout.write("Cod.: ", e.code)
		   
		except URLError, e:
			self.stdout.write("URL inválido!\n")
			self.stdout.write("Mensagem: ", e.reason)
		
		# Get download link
		self.stdout.write('Parsing download link...\n')
		import re
		
		r = re.compile('<a href="(.*)">Download XMLTV tudo em um</a>')
		link = r.findall(content)[0]
		
		# Download file
		self.stdout.write('Downloading zip file...\n')
		from django.conf import settings
		import os
		
		request = urllib2.Request(link)
		webFile = urllib2.urlopen(request)
		r = re.compile('file=(.*)/xmltv.zip')
		name = r.findall(link)[0] + '.zip'
		MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
		path = os.path.join(MEDIA_ROOT, 'epg/%s'%name)
		if ( not forced and os.path.exists(path) ):
			self.stdout.write('File %s already exists\n' % path)
			return
		localFile = open(path, 'w')
		localFile.write(webFile.read())
		webFile.close()
		localFile.close()
		
		# Unzip and Import to database
		self.stdout.write('Importing to database... (this can take a while)\n')
		from epg.models import Epg_Source
		from epg.data_importer import Zip_to_XML, XML_Epg_Importer
		
		epg_source = Epg_Source(filefield=localFile.name)
		epg_source.save()
		
		file_list = Zip_to_XML(epg_source.filefield.path)
		for f in file_list.get_all_files():
			XML_Epg_Importer(xml=f,epg_source_instance=epg_source).import_to_db()
		
		
