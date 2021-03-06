#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import filecmp
import hashlib
import hotshot
import logging
import os.path
import re
import shutil
import tempfile
import time
import zipfile

from datetime import timedelta, datetime
from dateutil.parser import parse
from lxml import etree
from lxml.etree import XMLSyntaxError
from pytz import timezone
from types import NoneType
from xml.etree import ElementTree as ET

from django.apps import apps
from django.conf import settings
from django import db
from django.db import transaction
from django.core import serializers
from django.utils.timezone import utc
from django.core.mail import send_mail

log = logging.getLogger('epg_import')

PROFILE_LOG_BASE = "/tmp"


def profile(log_file):
    """Profile some callable.

    This decorator uses the hotshot profiler to profile some callable (like
    a view function or method) and dumps the profile data somewhere sensible
    for later processing and examination.

    It takes one argument, the profile log name. If it's a relative path, it
    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the
    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof',
    where the time stamp is in UTC. This makes it easy to run and compare
    multiple trials.
    """

    if not os.path.isabs(log_file):
        log_file = os.path.join(PROFILE_LOG_BASE, log_file)

    def _outer(f):
        def _inner(*args, **kwargs):
            # Add a timestamp to the profile output when the callable
            # is actually called.
            (base, ext) = os.path.splitext(log_file)
            base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            final_log_file = base + ext

            prof = hotshot.Poofile(final_log_file)

            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.close()
            return ret

        return _inner
    return _outer


class xmlVerification:
    """ this class is used to verify xml file """

    linkxml = None

    def xml_value_encode_validation(self, line):
        if isinstance(line, unicode):
            return line
        try:
            return line.decode('utf-8')
        except UnicodeDecodeError:
            return line.decode('latin1').encode('utf-8')

    def xml_value_validation(self, filename):
        f = open(filename, "r")
        lines = f.readlines()
        f.close()
        f = open(filename, "w")
        i = 1
        aux = ''
        for line in lines:
            line = self.xml_value_encode_validation(line)
            remove = False
            if i == 1:
                f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
            elif i == 2:
                f.write("<tv generator-info-name=\"WWW.CIANET.IND.BR\" generator-info-url=\"http://www.cianet.ind.br\">")
            else:
                m = re.search("start=\"(\S* \S*)\"", str(line))
                if m:
                    try:
                        start = parse(str(m.group(1)))
                    except:
                        log.info('programa com problema: start inválido')
                        remove = True
                m = re.search("stop=\"(\S* \S*)\"", str(line))
                if m:
                    try:
                        stop = parse(str(m.group(1)))
                    except:
                        log.info('programa com problema: stop inválido')
                        remove = True
                m = re.search("<date>(\S*)<", str(line))
                if m:
                    try:
                        date = int(m.group(1))
                    except:
                        log.info('programa com problema: date inválido')
                        remove = True
                m = re.search("<value>(.*?)<", str(line))
                if m:
                    if '/' in m.group(1):
                        f.write("<value>{}</value>".format(m.group(1)))
                    else:
                        v = re.search("(\d+)", m.group(1))
                        if v:
                            f.write("<value>{}</value>".format(v.group(1)))
                        else:
                            f.write("<value>0</value>") 
                if not remove:
                    f.write(line)
            i += 1
        f.close()
        log.info('This document has value validated')


    def xml_validation(self, filename):
        validated = False
        while not validated:
            try:
                with open(filename) as f:
                    doc = etree.parse(f)
                log.info('This document is valid to verification')
                validated = True
            except XMLSyntaxError as e:
                log.info('This documment have some problems:')
                log.info(e)
                m = re.search("Document is empty,", str(e))
                if m is not None:
                    exit(1)
                m = re.search("line (\d+),", str(e))
                if m is None:
                    m = re.search("line (\d+)", str(e))
                remove_line = int(m.group(1))
                f = open(filename,"r")
                lines = f.readlines()
                f.close()
                f = open(filename,"w")
                i = 1
                is_trash = False
                aux = ''
                for line in lines:
                    if i <= 2:
                        f.write(line)
                    elif not is_trash:
                        if i != remove_line:
                            aux += line
                            result = re.match("</programme>", line)
                            if result is not None:
                                if result.group(0) == "</programme>":
                                    f.write(aux)
                                    aux = ''
                        else:
                            is_trash = True
                    else:
                        result = re.search("<programme", line)
                        if result is not None:
                            if result.group(0) == "<programme":
                                aux += line
                                is_trash = False
                    result = re.match("</tv>", line)
                    if result is not None:
                        if result.group(0) == "</tv>":
                            f.write(line)
                    i += 1
                f.close()

    def insert_unavailable(self, channel, start, stop, rating):
        self.linkxml.write(u'<programme start="%s" stop="%s" channel="%s">\n'.encode('ascii', 'xmlcharrefreplace') % (start, stop, channel))
        self.linkxml.flush()
        self.linkxml.write(u'<title lang="pt">Programação Indisponível</title>\n'.encode('ascii', 'xmlcharrefreplace'))
        self.linkxml.flush()
        self.linkxml.write(u'<category lang="pt">Categoria Indisponível</category>\n'.encode('ascii', 'xmlcharrefreplace'))
        self.linkxml.flush()
        self.linkxml.write(u'<country>País Indisponível</country>\n'.encode('ascii', 'xmlcharrefreplace'))
        self.linkxml.flush()
        self.linkxml.write("<video>\n")
        self.linkxml.flush()
        self.linkxml.write("<colour>yes</colour>\n")
        self.linkxml.flush()
        self.linkxml.write("</video>\n")
        self.linkxml.flush()
        self.linkxml.write("<rating system=\"Advisory\">\n")
        self.linkxml.flush()
        self.linkxml.write("<value>%s</value>\n" % rating)
        self.linkxml.flush()
        self.linkxml.write("</rating>\n")
        self.linkxml.flush()
        self.linkxml.write("</programme>\n")
        self.linkxml.flush()

    def xml_verification(self, filename, number=0):
        xml = filename
        current_channel = None

        # create XML - TV
        self.linkxml = file(os.path.join('/tmp/xml_verified_{}.xml'.format(number)), "w+")
        #self.linkxml = open('/tmp/xml_verified.xml', 'w')

        head = "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n"
        tv_info = "<tv generator-info-name=\"WWW.EPG.COM.BR\" generator-info-url=\"http://epg.com.br\">\n"
        self.linkxml.write(head)
        self.linkxml.flush()
        self.linkxml.write(tv_info)
        self.linkxml.flush()
        past_elem = None
        critical_list = {}
        for event, elem in etree.iterparse(xml, tag='programme'):
            for child in elem.iterchildren():
                if child.tag == 'rating':
                    rating = child.find('value').text
                    if not rating.isdigit():
                        child.find('value').text = '18'

            if elem.get('channel') is not None:
                channel = elem.get('channel')
            else:
                channel = None

            start = parse(elem.get('start'))
            stop = parse(elem.get('stop'))
            critical_list[channel] = start
            if (current_channel is None) or (current_channel != channel):
                current_channel = channel
                past_stop = parse(elem.get('stop'))
                past_start = parse(elem.get('start'))
                past_elem = elem
            else:
                if start > stop:
                    log.info('programa com problema: start > stop')
                elif past_start > start:
                    log.info('programa com problema: start do atual < start do anterior')
                elif start > past_stop:
                    log.info('intervalo vazio')
                    if (start - past_stop) > timedelta(minutes=5):
                        log.info('intervalo maior que 5 min')
                        self.linkxml.write(ET.tostring(past_elem))
                        insert = True
                        while insert:
                            if (start - past_stop) <= timedelta(minutes=60):
                                self.insert_unavailable(channel, past_stop, start, rating)
                                insert = False
                            else:
                                self.insert_unavailable(channel, past_stop, past_stop + timedelta(minutes=60), rating)
                                past_stop += timedelta(minutes=60)

                        past_stop = parse(elem.get('stop'))
                        past_start = parse(elem.get('start'))
                        past_elem = elem
                    else:
                        log.info('intervalo menor que 5 min')
                        past_elem.set('stop', elem.get('start'))
                        past_stop = parse(elem.get('stop'))
                        past_start = parse(elem.get('start'))
                        self.linkxml.write(ET.tostring(past_elem))
                        past_elem = elem
                elif start < past_stop:
                    log.info('intercessão')
                    if start == past_start:
                        log.info('programa repetido')
                    else:
                        past_elem.set('stop', elem.get('start'))
                        past_stop = parse(elem.get('stop'))
                        past_start = parse(elem.get('start'))
                        self.linkxml.write(ET.tostring(past_elem))
                        past_elem = elem
                elif start == past_stop:
                    past_stop = parse(elem.get('stop'))
                    past_start = parse(elem.get('start'))
                    self.linkxml.write(ET.tostring(past_elem))
                    past_elem = elem

        self.linkxml.write(ET.tostring(past_elem))
        tv_end = "</tv>\n"
        self.linkxml.write(tv_end)
        self.linkxml.flush()
        now = datetime.now()
        current_date = datetime(now.year, now.month, now.day,
                                now.hour, 0, 0, 0, None)
        email_msg = 'Olá Maneca\nEu sou apenas um script do Douglas\nEstou aqui para te dar uma triste notícia, sim é verdade, estamos novamente com problemas com a guia =(\nSegue a seguir a lista de canais como \'problemas\':\n'
        log.info(critical_list)
        need_mail = False
        for dic in critical_list.items():
            last_date = dic[1]
            last_date = datetime(last_date.year, last_date.month, last_date.day,
                                 last_date.hour, 0, 0, 0, None)
            if last_date < current_date:
                need_mail = True
                email_msg += 'Critial problems: \n'
                email_msg += 'Channel: %s\n' % dic[0]
                email_msg += 'atual: %s\n' % current_date
                email_msg += 'ultima: %s\n' % last_date
            elif ((last_date - timedelta(days=2)) < current_date):
                need_mail = True
                email_msg += 'Not a Critial problems: \n'
                email_msg += 'Channel: %s\n' % dic[0]
                email_msg += 'atual: %s\n' % current_date
                email_msg += 'ultima: %s\n' % last_date
        if need_mail:
            send_mail('EPG Critical Channels', email_msg, 'douglas.figueiredo@cianet.ind.br',
                    ['emanoel@cianet.ind.br'], fail_silently=False)
        log.info('This document is valid to import')
        return self.linkxml

class Zip_to_XML(object):
    '''
    This class is used to pre-treat an input file
    that can be a XML, a ZIP with one XML file inside or
    a ZIP file with multiple XML files inside
    '''

    def __init__(self, input_file_path):
        
        import mimetypes
        file_type, encoding = mimetypes.guess_type(input_file_path)
        if file_type == 'application/zip':
            self.input_file = zipfile.ZipFile(input_file_path, 'r')
            self.get_all_files = self._get_zip
        elif file_type in ('application/xhtml+xml', 'text/xml'):
            self.input_file = input_file_path
            self.get_all_files = self._get_xml
        else:
            raise Exception('Unkown type of file to import:', file_type)

    # Return one or multiple XML file handles inside a Zip archive
    def _get_zip(self):
        ret = []
        for n, f in enumerate(reversed(self.input_file.namelist())):

            filename = os.path.basename(f)
            # skip directories
            if not filename:
                continue
            # copy file (taken from zipfile's extract)
            source = self.input_file.open(f)
            target = file(os.path.join('/tmp', filename), "w+")
            shutil.copyfileobj(source, target)
            source.close()
            target.close()
            if os.path.isfile('/tmp/' + filename + '.old'):
                if filecmp.cmp('/tmp/' + filename, '/tmp/' + filename + '.old'):
                    log.info('Arquivos iguais, importação encerrada.')
                    exit(0)
                else:
                    os.unlink('/tmp/' + filename + '.old')
                    shutil.copy2('/tmp/' + filename, '/tmp/' + filename + '.old')
                    log.info('Arquivos diferentes, iniciando importação')
            else:
                log.info('Arquivo antigo não encontrado, iniciando importação')
                shutil.copy2('/tmp/' + filename, '/tmp/' + filename + '.old')

            log.info('/tmp/'+filename)
            verif = xmlVerification()
            verif.xml_value_validation('/tmp/'+filename)
            verif.xml_validation('/tmp/'+filename)
            verified = verif.xml_verification('/tmp/'+filename, n)
            #verified = file(os.path.join('/tmp/xml_verified.xml'), "w+")
            #verified.seek(0)

            ret.append(verified)
        return ret

    # Return a file handle of a XML file
    def _get_xml(self):

        return (open(self.input_file),)


class XML_Epg_Importer(object):
    '''
    Used to import XMLTV compliant files to the database.
    It receives a XML file handle as input.
    Imports xml into xmltv_source object
    '''

    def __init__(self, xml, xmltv_source=None, epg_source=None,
            log=open('/dev/null', 'w')):

        self.xmltv_source = xmltv_source
        self.epg_source = epg_source
        self.xml = xml
        self.log = log
        self.tree = etree.parse(self.xml.name)
        # get number of elements
        #self.total_channel = self.tree.xpath("count(//channel)")
        self.total_programme = self.tree.xpath("count(//programme)")
        #log.info('channel=%d , programme=%d', self.total_channel,
        log = logging.getLogger('epg_import')
        #    self.total_programme)
        log.info('programme=%d', self.total_programme)
        #self.epg_source.numberofElements += \
        #    self.total_channel +\
        #    self.total_programme
        self.epg_source.numberofElements += \
            self.total_programme
        # get meta data
        self.xmltv_source.generator_info_name = \
            self.tree.xpath('string(//tv[1]/@generator-info-name)')
        self.xmltv_source.generator_info_url = \
            self.tree.xpath('string(//tv[1]/@generator-info-url)')
        # save
        self.xmltv_source.save()

    def serialize(self, obj):
        
        # use recursion to iterate
        try:
            [self.serialize(o) for o in obj]
        except TypeError:
            pass

        name = obj.__class__.__name__
        # check if there is an opened file descriptor for this kind of obj
        if not name in self.dump_data['file_handlers']:
            self.dump_data['file_handlers'][name] = open(
                '%s/%s.json' % (self.tempdir, name), 'w')
            self.dump_data['object_ids'][name] = []
        if self.already_serialized(obj):
            # already serialized, so skip it
            return

        self.dump_data['object_ids'][name].append(obj.id)
        data = serializers.serialize("json", [obj, ], indent=2)
        self.dump_data['file_handlers'][name].write(data)

    def already_serialized(self, obj):
        
        name = obj.__class__.__name__
        try:
            self.dump_data['object_ids'][name].index(obj.id)
            # already serialized
            return 1
        except KeyError:
            return 0
        except ValueError:
            return 0

    def count_channel_elements(self):
        
        return len(self.tree.findall('channel'))

    def count_programme_elements(self):
        
        return len(self.tree.findall('programme'))

    def get_number_of_elements(self):
        
        return self.count_channel_elements() + self.count_programme_elements()

    def get_period_of_the_file(self):
        
        programmes = self.tree.findall('programme')
        starts = map(lambda p: parse(p.get('start')), programmes)
        stops = map(lambda p: parse(p.get('stop')), programmes)
        starts.sort()
        s_start = starts[0]
        stops.sort(reverse=True)
        s_stop = stops[0]
        return s_start.astimezone(timezone('UTC')).replace(tzinfo=utc), \
            s_stop.astimezone(timezone('UTC')).replace(tzinfo=utc)

    def get_xml_info(self):
        
        tv = self.tree.getroot()
        return {
            'source_info_url': tv.get('source-info-url'), \
            'source_info_name': tv.get('source-info-name'), \
            'source_data_url': tv.get('source-data-url'), \
            'generator_info_name': tv.get('generator-info-name'), \
            'generator_info_url': tv.get('generator-info-url')
        }

    #@transaction.commit_on_success
    def _increment_importedElements(self):
        Epg_Source = apps.get_model('epg','Epg_Source')
        if isinstance(self.epg_source, Epg_Source):
            self.epg_source.importedElements += 1
            self.epg_source.save()

    #@transaction.commit_on_success
    def _decrement_importedElements(self):
        Epg_Source = apps.get_model('epg','Epg_Source')
        if isinstance(self.epg_source, Epg_Source) \
            and self.epg_source.importedElements > 0:
            self.epg_source.importedElements -= 1
            self.epg_source.save()

    def _get_dict_for_langs(self):
        Lang = apps.get_model('epg','Lang')
        # Search for lang attributes in the xml
        lang_set = set()
        for l in self.tree.findall(".//*[@lang]"):
            lang_set.add(l.get('lang'))  # Auto exclude dupplicates
        langs = dict()
        for lang in lang_set:
            L, created = Lang.objects.get_or_create(value=lang)
            langs[lang] = L.id
        return langs

    def grab_info(self):
        log.info('Grabbing meta information')

        self.xml.seek(0)
        for event, elem in etree.iterparse(self.xml, tag='tv'):
            self.xmltv_source.generator_info_name = \
                elem.get('generator-info-name')
            self.xmltv_source.generator_info_url = \
                elem.get('generator-info-url')

        self.xmltv_source.save()

    #@transaction.commit_on_success
    def import_channel_elements(self):
        Channel = apps.get_model('epg','Channel')
        Channel = apps.get_model('epg','Channel')
        Lang = apps.get_model('epg','Lang')
        Display_Name = apps.get_model('epg','Display_Name')
        log.info('Importing Channel elements')
        self.xml.seek(0)
        #for ev, elem in etree.iterparse(self.xml.name, tag='channel'):
        for elem in self.tree.xpath('programme'):
            C, created = Channel.objects.get_or_create(
                channelid=elem.get('channel'))

            L, created = Lang.objects.get_or_create(
                value='pt')
            D, created = Display_Name.objects.get_or_create(
                value=elem.get('channel') or '', lang=L)

            C.display_names.add(D)

            self.serialize(D)

            #self.serialize(C)

            elem.clear()
            # Also eliminate now-empty references from the root node to <Title>
            while elem.getprevious() is not None:
                del elem.getparent()[0]


    # @profile("programme.prof")
    @transaction.commit_manually
    def import_programme_elements(self, limit=0):
        Lang = apps.get_model('epg', 'Lang')
        Title = apps.get_model('epg', 'Title')
        Programme = apps.get_model('epg', 'Programme')
        Guide = apps.get_model('epg', 'Guide')
        Channel = apps.get_model('epg', 'Channel')
        Description = apps.get_model('epg', 'Description')
        Category = apps.get_model('epg', 'Category')
        Rating = apps.get_model('epg', 'Rating')
        Star_Rating = apps.get_model('epg', 'Star_Rating')
        Country = apps.get_model('epg', 'Country')
        Icon = apps.get_model('epg', 'Icon')
        Language = apps.get_model('epg', 'Language')
        Subtitle = apps.get_model('epg', 'Subtitle')
        Actor = apps.get_model('epg', 'Actor')
        Staff = apps.get_model('epg', 'Staff')

        log.debug('Importing Programme elements:%s', self.xml)
        # Get channels from db
        channels = dict()
        for c in Channel.objects.values_list('channelid', 'pk'):
            channels[c[0]] = c[1]
        # import_start = datetime.now()
        import_ant = datetime.now()
        nant = 0
        imported = 0
        title = ''
        desc = ''
        pornlist = []
        pornlist.append('SEXY HOT')
        pornlist.append('PLAYBOY')
        pornlist.append('VENUS')
        pornlist.append('FORMAN')
        pornlist.append('SEX PRIVÉ')
        try:
            # for event, elem in etree.iterparse(self.xml, tag='programme'):
            for event, elem in etree.iterparse(self.xml, tag='programme'):
                # 
                # remove = False
                # for child in elem.iterchildren():
                #    if child.tag == 'rating':
                #        if child.find('value').text == '18':
                #            remove = True

                if elem.get('channel') is not None:
                    channel = elem.get('channel')
                else:
                    channel = None

                remove = False
                for i in pornlist:
                    if channel == i:
                        remove = True

                if elem.find('date') is not None:
                    date = elem.find('date').text
                else:
                    date = None

                if elem.find('title') is not None:
                    if remove:
                        title = 'Programação ' + channel
                    else:
                        title = elem.find('title').text
                else:
                    title = ''

                if elem.find('desc') is not None:
                    if remove:
                        desc = ''
                    else:
                        desc = elem.find('desc').text
                else:
                    desc = ''

                programid = title + desc

                m = hashlib.md5()
                m.update(programid.encode("utf8", "ignore"))
                programid = m.hexdigest()

                # Get time and convert it to UTC
                start = parse(elem.get('start')).astimezone(
                    timezone('UTC')).replace(tzinfo=utc)
                stop = parse(elem.get('stop')).astimezone(
                    timezone('UTC')).replace(tzinfo=utc)

                fucking_remove = False
                if stop < start:
                    log.info('################')
                    log.info(channel)
                    log.info(title)
                    log.info(start)
                    log.info(stop)
                    log.info('################')
                    fucking_remove = True
                if not fucking_remove:
                    P, c = Programme.objects.get_or_create(programid=programid)
                    P.date = date
                    P.save()

                    # Insert guide
                    channel_id = channels[elem.get('channel')]
                    G, created = Guide.objects.get_or_create(
                        start=start, stop=stop,
                        channel_id=channel_id, programme=P)
                    for child in elem.iterchildren():
                        if child.tag == 'desc':
                            if child.get('lang'):
                                L, created = Lang.objects.get_or_create(
                                    value=child.get('lang'))
                            else:
                                L = None
                            if type(child.text) is NoneType:
                                continue

                            if remove:
                                desc = ''
                            else:
                                desc = child.text.replace(
                                    ' - www.revistaeletronica.com.br ', '')

                            obj, created = Description.objects.get_or_create(
                                value=desc, lang=L)
                            P.descriptions.add(obj)
                        elif child.tag == 'title':
                            L, created = Lang.objects.get_or_create(
                                value=child.get('lang'))
                            if remove:
                                obj, created = Title.objects.get_or_create(
                                    value=title, lang=L)
                            else:
                                obj, created = Title.objects.get_or_create(
                                    value=child.text, lang=L)
                            P.titles.add(obj)
                        elif child.tag == 'sub-title':
                            L, created = Lang.objects.get_or_create(
                                value=child.get('lang'))
                            if remove:
                                obj, created = Title.objects.get_or_create(
                                    value=title, lang=L)
                            else:
                                obj, created = Title.objects.get_or_create(
                                    value=child.text, lang=L)
                            P.secondary_titles.add(obj)
                        elif child.tag == 'category':
                            L, created = Lang.objects.get_or_create(
                                value=child.get('lang'))
                            obj, created = Category.objects.get_or_create(
                                value=child.text, lang=L)
                            P.categories.add(obj)
                        elif child.tag == 'video':
                            for grand_child in child.iterchildren():
                                if grand_child.tag == 'colour':
                                    P.video_colour = grand_child.text
                                elif grand_child.tag == 'present':
                                    P.video_present = grand_child.text
                                elif grand_child.tag == 'aspect':
                                    P.video_aspect = grand_child.text
                                elif grand_child.tag == 'quality':
                                    P.video_quality = grand_child.text
                        elif child.tag == 'audio':
                            for grand_child in child.iterchildren():
                                if grand_child.tag == 'present':
                                    P.audio_present = grand_child.text
                                elif grand_child.tag == 'stereo':
                                    P.audio_stereo = grand_child.text
                        elif child.tag == 'country':
                            obj, created = Country.objects.get_or_create(
                                value=child.text)
                            P.country = obj
                        elif child.tag == 'rating':
                            obj, created = Rating.objects.get_or_create(
                                system=child.get('system'),
                                value=child.find('value').text)
                            P.rating = obj
                        elif child.tag == 'star-rating':
                            obj, created = Star_Rating.objects.get_or_create(
                                value=child.find('value').text,
                                system=child.get('system'))
                            for i in child.iterfind('icon'):
                                I, created = Icon.objects.get_or_create(
                                    src=i.get('src'))
                                obj.icons.add(I)
                            P.star_ratings.add(obj)
                        elif child.tag == 'language':
                            L, created = Lang.objects.get_or_create(
                                value=child.get('lang'))
                            obj, created = Language.objects.get_or_create(
                                value=child.text, lang=L)
                            P.language = obj
                        elif child.tag == 'original_language':
                            L, created = Lang.objects.get_or_create(
                                value=child.get('lang'))
                            obj, created = Language.objects.get_or_create(
                                value=child.text, lang=L)
                            P.original_language = obj
                        elif child.tag == 'subtitles':
                            obj = set()
                            for sub in child.iterchildren('language'):
                                lang, created = Lang.objects.get_or_create(
                                    value=child.get('lang'))
                                L, created = Language.objects.get_or_create(
                                    value=sub.text, lang=lang)
                                S, created = Subtitle.objects.get_or_create(
                                    language=L, subtitle_type=sub.get('type'))
                                P.subtitles.add(S)
                                obj.add((L, S))
                        elif child.tag == 'length':
                            units = child.get('units')
                            if units == 'seconds':
                                P.length = int(child.text)
                            elif units == 'minutes':
                                P.length = int(child.text) * 60
                            elif units == 'hours':
                                P.length = int(child.text) * 3600
                        elif child.tag == 'credits':
                            for grand_child in child.iterchildren():
                                if grand_child.tag == 'actor':
                                    obj, created = Actor.objects.get_or_create(
                                        name=grand_child.text,
                                        role=grand_child.get('role'))
                                    P.actors.add(obj)
                                elif grand_child.tag == 'director':
                                    obj, created = Staff.objects.get_or_create(
                                        name=grand_child.text)
                                    P.directors.add(obj)
                                elif grand_child.tag == 'writer':
                                    obj, created = Staff.objects.get_or_create(
                                        name=grand_child.text)
                                    P.writers.add(obj)
                                elif grand_child.tag == 'adapter':
                                    obj, created = Staff.objects.get_or_create(
                                        name=grand_child.text)
                                    P.adapters.add(obj)
                                elif grand_child.tag == 'producer':
                                    obj, created = Staff.objects.get_or_create(
                                        name=grand_child.text)
                                    P.producers.add(obj)
                                elif grand_child.tag == 'composer':
                                    obj, created = Staff.objects.get_or_create(
                                        name=grand_child.text)
                                    P.composers.add(obj)
                                elif grand_child.tag == 'editor':
                                    obj, created = Staff.objects.get_or_create(
                                        name=grand_child.text)
                                    P.editors.add(obj)
                                elif grand_child.tag == 'presenter':
                                    obj, created = Staff.objects.get_or_create(
                                        name=grand_child.text)
                                    P.presenters.add(obj)
                                elif grand_child.tag == 'commentator':
                                    obj, created = Staff.objects.get_or_create(
                                        name=grand_child.text)
                                    P.commentators.add(obj)
                                elif grand_child.tag == 'guest':
                                    obj, created = Staff.objects.get_or_create(
                                        name=grand_child.text)
                                    P.guests.add(obj)

                    P.save()

                    # self.serialize(P)

                    elem.clear()
                    # Also eliminate now-empty references
                    # from the root node to <Title>
                    while elem.getprevious() is not None:
                        del elem.getparent()[0]

                    imported += 1
                    if imported % 1000 == 0:
                        nant = imported - nant
                        # db.transaction.autocommit()
                        db.transaction.commit()
                        db.reset_queries()
                        delta = datetime.now() - import_ant
                        vel = nant / delta.total_seconds()
                        percent = (imported / self.total_programme) * 100
                        log.info('Imported %d/%d (%.2g) vel=%d i/s', imported,
                                self.total_programme, percent, vel)
                        nant = imported
                        import_ant = datetime.now()
                    if limit > 0 and imported >= limit:
                        break
        except Exception as e:
            log.error('Error:%s', e)
        db.transaction.commit()
        db.reset_queries()


    #@transaction.commit_on_success
    def import_to_db(self):
        zip = zipfile.ZipFile(
            '%s/%dfull.zip' % (os.path.join(settings.MEDIA_ROOT, 'epg'),
                self.xmltv_source.pk), "w", zipfile.ZIP_DEFLATED)

        # create temp dir
        self.tempdir = tempfile.mkdtemp()

        # init dict with file handlers and
        self.dump_data = {'file_handlers': {}, 'object_ids': {}}

        #self.grab_info()

        #epg_source = self.xmltv_source.epg_source_ptr

        # Import <channel> elements
        self.import_channel_elements()
        # Import <programme> elements
        self.import_programme_elements(limit=0)
        # count elements
        #epg_source.numberofElements = \
        #    Programme.objects.filter(source=epg_source).count() + \
        #    Channel.objects.filter(source=epg_source).count()
        # Update importedElements
        #epg_source.importedElements = self.xmltv_source.numberofElements
        # save changes
        #epg_source.save()
        #self.xmltv_source.save()

        #self.serialize(epg_source)
        for k, v in self.dump_data['file_handlers'].items():
            log.info('Writing %d %s objects' % (
                len(self.dump_data['object_ids'][k]), k))
            v.flush()
            v.close()

            file = open(v.name, 'r+')

            # edit file
            data = file.read()
            output = re.sub(r'^\]\[$', r',', data, flags=re.MULTILINE)
            file.seek(0)
            file.truncate(0)
            file.write(output)
            file.flush()

            zip.write(file.name, os.path.basename(file.name))
            file.close()
        zip.close()
        # remove temp dir
        shutil.rmtree(self.tempdir)
        ## Rebuild linked list
        sql_linked_list = "update epg_guide g set \
previous_id = (\
select o.id from epg_guide o where o.start < g.start AND \
o.channel_id = g.channel_id order by o.start desc limit 1\
),\
next_id = (\
select o.id from epg_guide o where o.start > g.start AND \
o.channel_id = g.channel_id order by o.start asc limit 1\
);\
"
        #from django.db import connection
        #cursor = connection.cursor()
        #cursor.execute(sql_linked_list)


def get_info_from_epg_source(epg_source):
    

    # Update Epg_Source fields
    numberofElements = 0
    file_list = Zip_to_XML(epg_source.filefield.path)
    
    for f in file_list.get_all_files():
        importer = XML_Epg_Importer(f, epg_source_instance=epg_source)
        numberofElements += importer.get_number_of_elements()
        # Retrive maximum stop time and minimum start time
        if (epg_source.minor_start != None) and (epg_source.major_stop != None):
            minor_start, major_stop = importer.get_period_of_the_file()
            if (epg_source.minor_start > minor_start):
                epg_source.minor_start = minor_start
            if (epg_source.major_stop < major_stop):
                epg_source.major_stop = major_stop
        else:
            epg_source.minor_start, epg_source.major_stop = \
                importer.get_period_of_the_file()

    # Update Epg_Source fields
    epg_source.numberofElements = numberofElements
    epg_source.importedElements = 0
    info = importer.get_xml_info()
    epg_source.source_info_url = info['source_info_url']
    epg_source.source_info_name = info['source_info_name']
    epg_source.source_data_url = info['source_data_url']
    epg_source.generator_info_name = info['generator_info_name']
    epg_source.generator_info_url = info['generator_info_url']

    epg_source.save()


def diff_epg_dumps(input1, input2):
    
    "diff 2 zip files containing json object dumps"
    # create tempdir and output zip file
    tempdir = tempfile.mkdtemp()
    zip = zipfile.ZipFile('%sdiff.zip' % input2[:-8],
        "w", zipfile.ZIP_DEFLATED)
    # open input zip files
    z1 = zipfile.ZipFile(input1, 'r')
    z2 = zipfile.ZipFile(input2, 'r')

    p = re.compile(r'^,$', re.MULTILINE)
    for file in z2.namelist():
        f2 = z2.open(file)
        try:
            f1 = z1.open(file)
        except KeyError:
            zip.writestr(file, f2.read())
            f2.close()
            continue
        lines1 = f1.read()
        lines2 = f2.read()
        set1 = set(filter(None, p.split(lines1[1:-2])))
        set2 = set(filter(None, p.split(lines2[1:-2])))
        diff = list(set2 - set1)
        out = open(os.path.join(tempdir, f2.name), 'w')
        out.write('[')
        out.writelines(','.join(diff))
        out.write(']\n')
        out.close()
        f1.close()
        f2.close()
        zip.write(out.name, os.path.basename(out.name))
    # cleanups
    zip.close()
    shutil.rmtree(tempdir)

