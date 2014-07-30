#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from epg.models import XMLTV_Source, Epg_Source
from epg.new_data_importer_sem_18 import XML_Epg_Importer

from datetime import datetime
from pytz import timezone
from optparse import make_option
import urllib
import os


class Command(BaseCommand):

    base_url = "http://xmltv.revistaeletronica.com.br/wp/?page_id=36"
    args = "[path to zip file]"
    help = ("Automatically fetch and import a xmltv file to the EPG database. "
            "If a file path is provided, the data will be imported from it.")

    option_list = BaseCommand.option_list + (
        make_option('--force', action='store_true', dest='forced',
                    default=False,
                    help='Force importation even if the xmltv file already exists'
                    ),
    )

    def download_xml(self):
        "Download the xml"
        url = 'http://www.epg.com.br/guia/xmltv.php?gerar=1'
        path = os.path.join(settings.MEDIA_ROOT, 'epg')
        urllib.urlretrieve(url, path + "/xmltv.xml")

    def handle(self, *args, **options):
        # forced = options.get('forced', False)
        if len(args) == 1:
            # Validate the file path, we need an absolute on
            if os.path.exists(args[0]) is False:
                raise CommandError('%s is not a file' % args[0])
            xmlfile = os.path.abspath(args[0])
            # Validate file type by extension
            if xmlfile.split('.')[-1] != 'xml':
                raise CommandError('%s is not a xml file' % args[0])
            self.stdout.write('Using %s\n' % xmlfile)
        else:
            path = os.path.join(settings.MEDIA_ROOT, 'epg')
            xmlfile = path + "/xmltv.xml"
            self.download_xml()
            self.stdout.write('Using %s\n' % xmlfile)

        date = datetime.fromtimestamp(os.path.getctime(xmlfile)).replace(tzinfo=timezone('America/Sao_Paulo'))

        try:
            xmltv_source = XMLTV_Source.objects.get(
                lastModification=date.replace(tzinfo=timezone('UTC')))
            xmltv_source.filefield = xmlfile
            xmltv_source.save()
        except XMLTV_Source.DoesNotExist:
            xmltv_source = XMLTV_Source.objects.create(filefield=xmlfile, lastModification=date.replace(tzinfo=timezone('UTC')))

        epg_source = Epg_Source(filefield=xmlfile)
        XML_Epg_Importer(xml=xmlfile, xmltv_source=xmltv_source,
                         epg_source=epg_source,
                         log=self.stdout).import_to_db()
