#!/usr/bin/env python
# -*- encoding:utf-8 -*-

#FIXME: GMT para importação deve ser corrigido.
#
# O valor que vem do XML segue seguinte padrão: yyyyMMddhhmmssmmmm gmt (20120713083000 -0300)
# Para corrigir é necessário pegar o valor do GMT no fim, aplicar o inverso de horas e minutos
# na data/hora informada e salvar informando que o valor do timezone está em UTF
#
# Assim se for importar horários de outras regiões, não vai dar conflito, pois atualmente
# após a alteração para timezone ativado do Django, apenas coloquei como a região origem
# do da data/hora como sendo America/Sao_Paulo (isso é, GMT -0300), isso não vai funcionar
# Quando a gente importar programação de outras regiões que usem GMT diferente de -0300
# Por isso a solução descrita acima.
#
# Mais informações em: https://docs.djangoproject.com/en/1.4/topics/i18n/timezones/#default-current-time-zone
#
# PS2: Não coloque o tzinfo=None, se isso for feito, o Django aplica o tzinfo como padrão
# Isso é, se o servidor tiver um como GMT -0300, ele vai aplicar -3 horas em toda importação
# o que vai gerar uma base de dados fora de UTC, por tanto quando for feita uma pesquisa pelo
# Django por ele vai tentar corrigir o valor novamente, trazendo a informação de
# data em -6
#
# Só vi o erro, uma semana depois que a gente ativou o tz, isso é, quando foi necessário
# importar a base de dados, pois antes a gente não usava tz e o None fazia com que o
# Django ignorasse o valor do tzinfo e simplismente salvasse do jeito que a data
# estava sendo informada.



import zipfile
from lxml import etree
from django.db import transaction
from datetime import tzinfo, timedelta, datetime
from dateutil.parser import parse
from pytz import timezone
from types import NoneType
from django.utils.timezone import utc

from models import *

#from profilehooks import profile


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
            ret.append(self.input_file.open(f))
        return ret

    # Return a file handle of a XML file
    def _get_xml(self):
        return (open(self.input_file),)


class XML_Epg_Importer(object):
    '''
    Used to import XMLTV compliant files to the database.
    It receives a XML file handle as input.
    '''

    def __init__(self, xml, epg_source_instance):

        self._epg_source_instance = epg_source_instance
        if type(xml) == str:
            # Input is string
            self.tree = etree.fromstring(xml)
        else:
            # Input is a file-like object (provides a read method)
            self.tree = etree.parse(xml)

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
        return {'source_info_url': tv.get('source-info-url'), \
            'source_info_name': tv.get('source-info-name'), \
            'source_data_url': tv.get('source-data-url'), \
            'generator_info_name': tv.get('generator-info-name'), \
            'generator_info_url': tv.get('generator-info-url')}

    @transaction.commit_on_success
    def _increment_importedElements(self):
        if isinstance(self._epg_source_instance, Epg_Source):
            self._epg_source_instance.importedElements += 1
            self._epg_source_instance.save()

    @transaction.commit_on_success
    def _decrement_importedElements(self):
        if isinstance(self._epg_source_instance, Epg_Source) and \
            self._epg_source_instance.importedElements > 0:
            self._epg_source_instance.importedElements -= 1
            self._epg_source_instance.save()

    def _get_dict_for_langs(self):
        # Search for lang attributes in the xml
        lang_set = set()
        for l in self.tree.findall(".//*[@lang]"):
            lang_set.add(l.get('lang'))    # Auto exclude dupplicates
        langs = dict()
        for lang in lang_set:
            L, created = Lang.objects.get_or_create(value=lang)
            langs[lang] = L.id
        return langs

    def import_channel_elements(self):

        # Search for lang attributes in the xml
        langs = self._get_dict_for_langs()

        for e in self.tree.iter('channel'):

            try:
                C = Channel.objects.only('channelid').get(
                    channelid=e.get('id'))
                continue
            except:
                C = Channel.objects.create(source=self._epg_source_instance,
                    channelid=e.get('id'))
            # Display_Names
            displays = []
            for d in e.iter('display-name'):
                D, created = Display_Name.objects.get_or_create(value=d.text,
                    lang_id=langs[d.get('lang')])
                displays.append(D)
            if len(displays) > 0:
                C.display_names.add(*displays)
            # Icons
            icons = []
            for i in e.iter('icon'):
                I, created = Icon.objects.get_or_create(src=i.get('src'))
                icons.append(I)
            if len(icons) > 0:
                C.icons.add(*icons)
            # URLs
            urls = []
            for u in e.iter('url'):
                U, created = Url.objects.get_or_create(value=u.text)
                urls.append(U)
            if len(urls) > 0:
                C.urls.add(*urls)
            # Update Arquivo_Epg instance, for the progress bar
            #self._increment_importedElements()

    def import_programme_elements(self):

        # Get channels from db
        channels = dict()
        for c in Channel.objects.values_list('channelid', 'pk'):
            channels[c[0]] = c[1]
        # Search for lang attributes in the xml
        langs = self._get_dict_for_langs()
        # init guide list
        guide = []

        for e in self.tree.iter('programme'):

            if e.find('date') is not None:
                date = e.find('date').text
            else:
                date = None

            # Get time and convert it to UTC
            start = parse(e.get('start')).astimezone(timezone('UTC')).replace(
                tzinfo=utc)
            stop = parse(e.get('stop')).astimezone(timezone('UTC')).replace(
                tzinfo=utc)

            # Try to find the programme in db
            try:
                P = Programme.objects.only('programid').get(
                    programid=e.get('program_id'))
                # Insert guide
                G, created = Guide.objects.get_or_create(
                    source=self._epg_source_instance,
                    start=start,
                    stop=stop,
                    channel_id=channels[e.get('channel')],
                    programme_id=P.id)
                continue
            except:
                P = Programme.objects.create(
                    programid=e.get('program_id'),
                    date=date,
                    source=self._epg_source_instance)
            # Insert guide
            G, created = Guide.objects.get_or_create(
                source=self._epg_source_instance,
                start=start,
                stop=stop,
                channel_id=channels[e.get('channel')],
                programme_id=P.id)
            # Get descriptions
            for d in e.iter('desc'):
                if langs.has_key(d.get('lang')):
                    lang = langs[d.get('lang')]
                else:
                    lang = None
                # Strip the banner ' - www.revistaeletronica.com.br '
                if len(d.text) > 32:
                    desc = d.text[:-32]
                else:
                    desc = d.text
                D, created = Description.objects.get_or_create(value=desc,
                    lang_id=lang)
                P.descriptions.add(D)
            # Get titles
            for t in e.iter('title'):
                T, created = Title.objects.get_or_create(value=t.text,
                    lang_id=langs[t.get('lang')])
                P.titles.add(T)
            # Get Sub titles
            for st in e.iter('sub-title'):
                ST, created = Title.objects.get_or_create(value=st.text,
                    lang_id=langs[st.get('lang')])
                P.secondary_titles.add(ST)
            # Get categories
            for c in e.iter('category'):
                C, created = Category.objects.get_or_create(value=c.text,
                    lang_id=langs[c.get('lang')])
                P.categories.add(C)
            # Get <video> element
            video = e.find('video')
            if video is not None:
                if video.find('colour') is not None:
                    P.video_colour = video.find('colour').text
                if video.find('present') is not None:
                    P.video_present = video.find('present').text
                if video.find('aspect') is not None:
                    P.video_aspect = video.find('aspect').text
                if video.find('quality') is not None:
                    P.video_quality = video.find('quality').text
            # Get <audio> element
            audio = e.find('audio')
            if audio is not None:
                if audio.find('present') is not None:
                    P.audio_present = audio.find('present').text
                if audio.find('stereo') is not None:
                    P.audio_stereo = audio.find('stereo').text
            # Get country element
            try:
                country = e.find('country').text
                Ct, created = Country.objects.get_or_create(value=country)
                P.country = Ct
            except:
                pass
            # Get <rating>
            rating = e.find('rating')
            if rating is not None:
                system = rating.get('system')
            try:
                value = e.find('rating').find('value').text
            except:
                value = None
            if (system is not None) and (value is not None):
                R, created = Rating.objects.get_or_create(system=system,
                    value=value)
                P.rating = R
            # <star-rating>
            for sr in e.findall('star-rating'):
                SR, created = Star_Rating.objects.get_or_create(
                    value=sr.find('value').text, system=sr.get('system'))
                for i in sr.findall('icon'):
                    I, created = Icon.objects.get_or_create(src=i.get('src'))
                    SR.icons.add(I)
                P.star_ratings.add(SR)
            # <language>
            language = e.find('language')
            if language is not None:
                L, created = Language.objects.get_or_create(
                    value=language.text, lang_id=langs[language.get('lang')])
                P.language = L
            # <original_language>
            original_language = e.find('original_language')
            if original_language is not None:
                L, created = Language.objects.get_or_create(
                    value=original_language.text,
                    lang_id=langs[original_language.get('lang')])
                P.original_language = L
            # <subtitles>
            subtitles = e.find('subtitles')
            if subtitles is not None:
                for sub in subtitles.findall('language'):
                    L, created = Language.objects.get_or_create(value=sub.text,
                        lang_id=langs[sub.get('lang')])
                    S, created = Subtitle.objects.get_or_create(language=L,
                        subtitle_type=sub.get('type'))
                    P.subtitles.add(S)
            # <length>
            length = e.find('length')
            if length is not None:
                units = length.get('units')
                if units == 'seconds':
                    P.length = int(length.text)
                elif units == 'minutes':
                    P.length = int(length.text) * 60
                elif units == 'hours':
                    P.length = int(length.text) * 3600
            # Get <credits>
            credits = e.find('credits')
            if credits is not None:
                for a in credits.findall('actor'):
                    A, created = Actor.objects.get_or_create(name=a.text,
                        role=a.get('role'))
                    P.actors.add(A)
                for s in credits.findall('director'):
                    S, created = Staff.objects.get_or_create(name=s.text)
                    P.directors.add(S)
                for s in credits.findall('writer'):
                    S, created = Staff.objects.get_or_create(name=s.text)
                    P.writers.add(S)
                for s in credits.findall('adapter'):
                    S, created = Staff.objects.get_or_create(name=s.text)
                    P.adapters.add(S)
                for s in credits.findall('producer'):
                    S, created = Staff.objects.get_or_create(name=s.text)
                    P.producers.add(S)
                for s in credits.findall('composer'):
                    S, created = Staff.objects.get_or_create(name=s.text)
                    P.composers.add(S)
                for s in credits.findall('editor'):
                    S, created = Staff.objects.get_or_create(name=s.text)
                    P.editors.add(S)
                for s in credits.findall('presenter'):
                    S, created = Staff.objects.get_or_create(name=s.text)
                    P.presenters.add(S)
                for s in credits.findall('commentator'):
                    S, created = Staff.objects.get_or_create(name=s.text)
                    P.commentators.add(S)
                for s in credits.findall('guest'):
                    S, created = Staff.objects.get_or_create(name=s.text)
                    P.guests.add(S)
            P.save()
            # Update Epg_Source instance, for the progress bar
            #self._increment_importedElements()

    @transaction.commit_on_success
    def import_to_db(self):
        # Import <channel> elements
        self.import_channel_elements()
        # Import <programme> elements
        self.import_programme_elements()
        # Update importedElements
        self._epg_source_instance.importedElements = self._epg_source_instance.numberofElements
        self._epg_source_instance.save()


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
            epg_source.minor_start, epg_source.major_stop = importer.get_period_of_the_file()

    # Update Epg_Source fields
    epg_source.numberofElements = numberofElements
    epg_source.importedElements = 0
    info = importer.get_xml_info()
    epg_source.source_info_url = info['source_info_url']
    epg_source.source_info_name = info['source_info_name']
    epg_source.source_data_url = info['source_data_url']
    epg_source.generator_info_name = info['generator_info_name']
    epg_source.generator_info_url = info['generator_info_url']

