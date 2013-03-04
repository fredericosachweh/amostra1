#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from epg.models import XMLTV_Source, Epg_Source
from epg.data_importer import Zip_to_XML, XML_Epg_Importer

from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
from ftplib import FTP
from optparse import make_option
import tempfile
import urllib2
import re
import os


class Command(BaseCommand):

    base_url = "http://xmltv.revistaeletronica.com.br/wp/?page_id=36"
    args = "[path to zip file]"
    help = ("Automatically fetch and import a xmltv file to the EPG database. "
            "If a file path is provided, the data will be imported from it.")

    option_list = BaseCommand.option_list + (
        make_option('--force',
            action='store_true',
            dest='forced',
            default=False,
            help='Force importation even if the xmltv file already exists'),
        )

    def fetch_url(self, url):
        try:
            request = urllib2.Request(url)
            # Abre a conexão
            fd = urllib2.urlopen(request)
            # Efetua a leitura do conteúdo.
            content = fd.read()
            fd.close()
        except urllib2.HTTPError, e:
            raise CommandError("Error fetching! Cod.: %d\n" % e.code)
        except urllib2.URLError, e:
            raise CommandError("Invalid URL! Cod.: %d\n" % e.code)
        except Exception as e:
            raise e
        return content

    def download_zip(self, forced):
        "Download the zip file from revista eletronica's website"
        self.stdout.write('Getting HTML...\n')
        content = self.fetch_url(self.base_url)
        # Get download link
        self.stdout.write('Parsing download link...\n')
        try:
            link = re.findall('<a href="(.*)">Download XMLTV tudo em um</a>',
                content)[0]
        except:
            CommandError('Could not find, aborting...\n')
        # Download file
        self.stdout.write('Downloading zip file...\n')
        webFile = self.fetch_url(link)
        name = re.findall('file=(.*)/xmltv.zip', link)[0] + '.zip'
        path = os.path.join(settings.MEDIA_ROOT, 'epg/%s' % name)
        if not forced and os.path.exists(path):
            CommandError('File %s already exists! Re-run with --force to \
import anyway.\n' % path)
        localFile = open(path, 'w')
        localFile.write(webFile)
        localFile.close()
        return localFile.name

    def download_zip_ftp(self, forced):
        "Download the zip file from revista eletronica's FTP"

        fileName = 'xmltv.zip'

        self.stdout.write('Connecting to FTP server...\n')
        ftp = FTP(settings.EPG_IMPORT_CREDENTIALS['site'])
        self.stdout.write('Authenticating...\n')
        ftp.login(settings.EPG_IMPORT_CREDENTIALS['username'],
            settings.EPG_IMPORT_CREDENTIALS['password'])
        f = []
        ftp.retrlines('LIST %s' % fileName, callback=f.append)
        s = f[0].split()
        # I know this modification time is from Sao Paulo
        date = parse('%s %s %s' % (s[5], s[6], s[7])).replace(
            tzinfo=timezone('America/Sao_Paulo'))
        size = int(s[4])
        self.stdout.write('Last date of modification was %s\n' % date)
        try:
            source = XMLTV_Source.objects.get(
                lastModification=date.replace(tzinfo=timezone('UTC')))
            # we already have that object
            if forced is False:
                raise CommandError(('File already imported! '
                    'Re-run with --force to import anyway.\n'))
        except XMLTV_Source.DoesNotExist:
            pass
        path = os.path.join(settings.MEDIA_ROOT, 'epg')
        localFile = tempfile.NamedTemporaryFile(prefix='', suffix='.zip',
            dir=path, delete=False)

        self.stdout.write('Downloading %s (%d bytes) to %s ...\n' % (
            fileName, size, localFile.name))
        ftp.retrbinary('RETR %s' % fileName, localFile.write)
        self.stdout.write('Download complete!\n')
        localFile.close()
        ftp.close()

        return localFile.name, date

    def handle(self, *args, **options):
        forced = options.get('forced', False)
        if len(args) == 1:
            # Validate the file path, we need an absolute on
            if os.path.exists(args[0]) is False:
                raise CommandError('%s is not a file' % args[0])
            xml_zip_file = os.path.abspath(args[0])
            # Validate file type by extension
            if xml_zip_file.split('.')[-1] != 'zip':
                raise CommandError('%s is not a zip file' % args[0])
            date = datetime.fromtimestamp(
                os.path.getctime(xml_zip_file)).replace(
                    tzinfo=timezone('America/Sao_Paulo'))
            self.stdout.write('Using %s\n' % xml_zip_file)
        else:
            xml_zip_file, date = self.download_zip_ftp(forced)
        # Unzip and Import to database
        self.stdout.write('Importing to database... (this can take a while)\n')
        try:
            xmltv_source = XMLTV_Source.objects.get(
                lastModification=date.replace(tzinfo=timezone('UTC')))
            if xmltv_source.filefield:
                self.stdout.write('Deleting old zip file %s\n' %
                    xmltv_source.filefield.name)
                os.remove(xmltv_source.filefield.name)
            xmltv_source.filefield = xml_zip_file
            xmltv_source.save()
        except XMLTV_Source.DoesNotExist:
            xmltv_source = XMLTV_Source.objects.create(filefield=xml_zip_file,
                lastModification=date.replace(tzinfo=timezone('UTC')))
        file_list = Zip_to_XML(xmltv_source.filefield.path).get_all_files()
        epg_source = Epg_Source(filefield=xml_zip_file)
        for f in file_list:
            XML_Epg_Importer(xml=f, xmltv_source=xmltv_source,
                epg_source=epg_source,
                log=self.stdout).import_to_db()
