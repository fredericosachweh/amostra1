#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf import settings
from django import db
from django.db import transaction
from django.core import serializers
from django.utils.timezone import utc

import re
import zipfile
import tempfile
import shutil
from lxml import etree
#from datetime import tzinfo, timedelta, datetime
from dateutil.parser import parse
#from pytz import timezone
from types import NoneType
#from django.contrib.contenttypes.models import ContentType
#from cStringIO import StringIO

from models import *

import hotshot
import time

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

            prof = hotshot.Profile(final_log_file)
            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.close()
            return ret

        return _inner
    return _outer


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
        for f in self.input_file.namelist():
            filename = os.path.basename(f)

            # skip directories
            if not filename:
                continue

            # copy file (taken from zipfile's extract)
            source = self.input_file.open(f)
            target = file(os.path.join('/tmp', filename), "w+")
            shutil.copyfileobj(source, target)
            source.close()
            target.seek(0)

            ret.append(target)
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

    def __init__(self, xml, xmltv_source, log=open('/dev/null', 'w')):

        self.xmltv_source = xmltv_source
        self.xml = xml
        self.log = log

        tree = etree.parse(self.xml.name)
        # get number of elements
        self.xmltv_source.numberofElements += tree.xpath("count(//channel)") +\
            tree.xpath("count(//programme)")
        # get meta data
        self.xmltv_source.generator_info_name = \
            tree.xpath('string(//tv[1]/@generator-info-name)')
        self.xmltv_source.generator_info_url = \
            tree.xpath('string(//tv[1]/@generator-info-url)')
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

    @transaction.commit_on_success
    def _increment_importedElements(self):
        if isinstance(self.xmltv_source, Epg_Source):
            self.xmltv_source.importedElements += 1
            self.xmltv_source.save()

    @transaction.commit_on_success
    def _decrement_importedElements(self):
        if isinstance(self.xmltv_source, Epg_Source) \
            and self.xmltv_source.importedElements > 0:
            self.xmltv_source.importedElements -= 1
            self.xmltv_source.save()

    def _get_dict_for_langs(self):
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

        self.log.write('Grabbing meta information')

        self.xml.seek(0)
        for event, elem in etree.iterparse(self.xml, tag='tv'):
            self.xmltv_source.generator_info_name = \
                elem.get('generator-info-name')
            self.xmltv_source.generator_info_url = \
                elem.get('generator-info-url')

        self.xmltv_source.save()

    #@profile("channel.prof")
    def import_channel_elements(self):

        self.log.write('Importing Channel elements')

        self.xml.seek(0)
        for event, elem in etree.iterparse(self.xml, tag='channel'):

            C, created = Channel.objects.get_or_create(
                channelid=elem.get('id'))
            #C.save()

            for child in elem.iterchildren():
                if child.tag == 'display-name':
                    L, created = Lang.objects.get_or_create(
                        value=child.get('lang'))
                    D, created = Display_Name.objects.get_or_create(
                        value=child.text, lang=L)
                    C.display_names.add(D)
                    self.serialize(D)
                elif child.tag == 'icon':
                    I, created = Icon.objects.get_or_create(
                        src=child.get('src'))
                    C.icons.add(I)
                    self.serialize(I)
                elif child.tag == 'url':
                    U, created = Url.objects.get_or_create(value=child.text)
                    C.urls.add(U)
                    self.serialize(U)

            #self.serialize(C)

            elem.clear()
            # Also eliminate now-empty references from the root node to <Title>
            while elem.getprevious() is not None:
                del elem.getparent()[0]

    #@profile("programme.prof")
    def import_programme_elements(self, limit=0):

        self.log.write('Importing Programme elements')
        # Get channels from db
        channels = dict()
        for c in Channel.objects.values_list('channelid', 'pk'):
            channels[c[0]] = c[1]

        imported = 0

        self.xml.seek(0)
        try:
            for event, elem in etree.iterparse(self.xml, tag='programme'):

                if elem.find('date') is not None:
                    date = elem.find('date').text
                else:
                    date = None

                try:
                    P = Programme.objects.get(programid=elem.get('program_id'))
                    P.date = date
                    P.save()
                except Programme.DoesNotExist:
                    P, created = Programme.objects.get_or_create(
                        programid=elem.get('program_id'),
                        date=date)

                # Get time and convert it to UTC
                start = parse(elem.get('start')).astimezone(
                    timezone('UTC')).replace(tzinfo=utc)
                stop = parse(elem.get('stop')).astimezone(
                    timezone('UTC')).replace(tzinfo=utc)
                # Insert guide
                channel_id = channels[elem.get('channel')]
                G, created = Guide.objects.get_or_create(
                    start=start, stop=stop,
                    channel_id=channel_id, programme=P)

                self.serialize(G)
                # this enables a huge gain in performance
                if self.already_serialized(P):
                    continue

                for child in elem.iterchildren():
                    if child.tag == 'desc':
                        if child.get('lang'):
                            L, created = Lang.objects.get_or_create(
                                value=child.get('lang'))
                        else:
                            L = None
                        if type(child.text) is NoneType:
                            continue

                        obj, created = Description.objects.get_or_create(
                            value=child.text, lang=L)
                        P.descriptions.add(obj)
                    elif child.tag == 'title':
                        L, created = Lang.objects.get_or_create(
                            value=child.get('lang'))
                        obj, created = Title.objects.get_or_create(
                            value=child.text, lang=L)
                        P.titles.add(obj)
                    elif child.tag == 'sub-title':
                        L, created = Lang.objects.get_or_create(
                            value=child.get('lang'))
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

                    self.serialize(obj)

                P.save()

                self.serialize(P)

                elem.clear()
                # Also eliminate now-empty references
                # from the root node to <Title>
                while elem.getprevious() is not None:
                    del elem.getparent()[0]

                imported += 1
                if imported % 100 == 0:
                    db.reset_queries()
                    self.log.write('Imported %d' % imported)

                if limit > 0 and imported >= limit:
                    break
        except:
            pass

    @transaction.commit_on_success
    def import_to_db(self):

        zip = zipfile.ZipFile(
            '%s/%dfull.zip' % (os.path.join(settings.MEDIA_ROOT, 'epg'),
                self.xmltv_source.pk), "w", zipfile.ZIP_DEFLATED)

        # create temp dir
        self.tempdir = tempfile.mkdtemp()

        # init dict with file handlers and
        self.dump_data = {'file_handlers': {}, 'object_ids': {}}

        #self.grab_info()

        epg_source = self.xmltv_source.epg_source_ptr

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

        self.serialize(epg_source)

        for k, v in self.dump_data['file_handlers'].items():
            self.log.write('Writing %d %s objects' % (
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

        # generate a diff
        try:
            id1 = Epg_Source.objects.filter(
                lastModification__lt=self.xmltv_source.lastModification
                ).order_by('-lastModification')[0].id
        except:
            self.log.write(
                'There is no previous full dump, so will not generate a diff')
            return
        id2 = self.xmltv_source.id
        self.log.write('Generating a diff between "%s" and "%s"' % (
            Epg_Source.objects.get(id=id1).lastModification,
            self.xmltv_source.lastModification))
        folder = os.path.dirname(self.xmltv_source.filefield.path)
        diff_epg_dumps(os.path.join(folder, '%dfull.zip' % id1),
            os.path.join(folder, '%dfull.zip' % id2))


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
