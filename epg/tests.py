#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from __future__ import unicode_literals
from django.utils import timezone
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
import simplejson as json

from models import *
from new_data_importer_sem_18 import XML_Epg_Importer, Zip_to_XML
import logging
log = logging.getLogger('unittest')

input_xml_1 = str('''<?xml version="1.0" encoding="UTF-8"?>
<tv generator-info-name="Revista Eletronica - Unidade Lorenz Ltda" \
generator-info-url="http://xmltv.revistaeletronica.com.br">
<programme start="20120115220500 -0200" stop="20120115224500 -0200" \
channel="Concert Channel" program_id="0000257856">
<title lang="pt">BBC Sessions: The Verve</title>
<title lang="en">BBC Sessions: Verve; The</title>
<desc>Uma impressionante atuação do The Verve no famoso estúdio Maida Vale, da\
 BBC. Desfrute desta íntima, porém poderosa gravação da banda de Richard \
Ashcroft, que inclui músicas como Bitter Sweet Symphony e Love is Noise. - \
www.revistaeletronica.com.br </desc>
<date>2008</date>
<category lang="pt">Espetáculo</category>
<category lang="pt">Show</category>
<video>
<colour>yes</colour>
</video>
<rating system="Advisory">
<value>18</value>
</rating>
</programme>
</tv>''')

input_xml_2 = str('''<?xml version="1.0" encoding="UTF-8"?>
<tv generator-info-name="Revista Eletronica - Unidade Lorenz Ltda" \
generator-info-url="http://xmltv.revistaeletronica.com.br">
<programme start="20120115234500 -0200" stop="20120116014500 -0200" \
channel="Band HD" program_id="0000025536">
<title lang="pt">Três Homens em Conflito</title>
<title lang="en">The Good, The Bad and the Ugly</title>
<desc>Durante a Guerra Civil Americana, três aventureiros tentam pôr as mãos \
numa fortuna. - www.revistaeletronica.com.br </desc>
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
<value>14</value>
</rating>
<star-rating>
<value>5/5</value>
</star-rating>
</programme>
</tv>''')

input_xml_3 = str('''<?xml version='1.0' encoding='iso-8859-1'?>\
<tv generator-info-name="CIANET" generator-info-url="www.cianet.ind.br">\
<programme start="20120115234500 -0200" stop="20120116014500 -0200" \
channel="Band HD" program_id="0000025536">
<title lang="pt">Três Homens em Conflito</title>
<title lang="en">The Good, The Bad and the Ugly</title>
<desc>Durante a Guerra Civil Americana, três aventureiros tentam pôr as mãos \
numa fortuna. - www.revistaeletronica.com.br </desc>
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
<programme start="20120115220500 -0200" stop="20120115224500 -0200" \
channel="Concert Channel" program_id="0000257856">
<title lang="pt">BBC Sessions: The Verve</title>
<title lang="en">BBC Sessions: Verve; The</title>
<desc>Uma impressionante atuação do The Verve no famoso estúdio Maida Vale, da\
 BBC. Desfrute desta íntima, porém poderosa gravação da banda de Richard \
Ashcroft, que inclui músicas como Bitter Sweet Symphony e Love is Noise. - \
www.revistaeletronica.com.br </desc>
<date>2008</date>
<category lang="pt">Espetáculo</category>
<category lang="pt">Show</category>
<video>
<colour>yes</colour>
</video>
<rating system="Advisory">
<value>18</value>
</rating>
</programme>
</tv>''')

xml_programme1 = str('''<?xml version="1.0" encoding="ISO-8859-1"?>
<tv generator-info-name="Revista Eletronica - Unidade Lorenz Ltda" \
generator-info-url="http://xmltv.revistaeletronica.com.br">
<programme start="20120713033000 -0300" stop="20120713050000 -0300" \
channel="Concert Channel" program_id="0000289501">
<title lang="pt">Austin City Limits 2010</title>
<title lang="en">Austin City Limits 2010</title>
<desc>O festival musical que enche durante três dias a cidade texana contou, \
em 2010, com as atuações de estrelas como The Eagles, Muse, The Strokes, \
Norah Jones, Sonic Youth, The Black Keys, Miike Snow e Devendra Banhart, entre\
 muitos outros. - www.revistaeletronica.com.br </desc>
<date>2010</date>
<category lang="pt">Espetáculo</category>
<category lang="pt">Show</category>
<video>
<colour>yes</colour>
</video>
<rating system="Advisory">
<value>Programa livre para todas as idades</value>
</rating>
</programme>''')

input_xml_rating = str('''<?xml version="1.0" encoding="UTF-8"?>
<tv generator-info-name="Revista Eletronica - Unidade Lorenz Ltda" \
generator-info-url="http://xmltv.revistaeletronica.com.br">
<programme start="20120115234500 -0200" stop="20120116014500 -0200" \
channel="Band HD" program_id="0000025536">
<title lang="pt">Três Homens em Conflito</title>
<title lang="en">The Good, The Bad and the Ugly</title>
<desc>Durante a Guerra Civil Americana, três aventureiros tentam pôr as mãos \
numa fortuna. - www.revistaeletronica.com.br </desc>
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
<programme start="20120116014500 -0200" stop="20120116024500 -0200" channel="\
Band HD" program_id="0000219575" event_id="00000000000006278834" series_key="">
<title lang="pt">Pet Shop Boys no BBC</title>
<desc>De volta com o esperado 10° disco de estúdio, Yes", e recebendo o Brit \
Award de 2009, não há um momento melhor para uma retrospectiva da carreira \
fenomenal dos Pet Shop Boys. "</desc>
<category lang="pt">Espetáculo</category>
<category lang="pt">Musical</category>
<video>
<colour>yes</colour>
</video>
<rating system="Advisory">
<value>Programa impróprio para menores de 10 anos</value>
</rating>
</programme>
<programme start="20120116024500 -0200" stop="20120116034500 -0200" channel="\
Band HD" program_id="0000292544" event_id="00000000000006278835" series_key="">
<title lang="pt">Lovebox Festival 2011</title>
<title lang="en">Lovebox Festival 2011 - Part 2</title>
<desc>A 2ª parte do festival criado pela dupla de DJs Groove Armada, em 2002, \
onde apresentam o mais novo da cena eletrônica. E em sua edição de 2011, \
convidaram Snoop Dogg, Scissor Sisters, Beth Ditto, Santigold, Ziggy Marley \
e a lenda: Blondie.</desc>
<category lang="pt">Espetáculo</category>
<category lang="pt">Show</category>
<video>
<colour>yes</colour>
</video>
<rating system="Advisory">
<value>Programa livre para todas as idades</value>
</rating>
</programme>
<programme start="20120116034500 -0200" stop="20120116044500 -0200" channel="\
Band HD" program_id="0000318062" event_id="00000000000005836669" series_key="">
<title lang="pt">O Segredo da Cabana</title>
<title lang="en">The Cabin in the Woods</title>
<desc>Autoproclamada por seu criadores como "uma revolução no cinema de terror\
", a história conta as desventuras de cinco amigos "presos" no bosque e \
prisioneiros de uma verdadeira armadilha mortal.</desc>
<credits>
<director>Drew Goddard</director>
<actor>Kristen Connolly</actor>
<actor>Chris Hemsworth</actor>
<actor>Anna Hutchison</actor>
<actor>Fran Kranz</actor>
</credits>
<date>2011</date>
<category lang="pt">Filme</category>
<category lang="pt">Terror</category>
<country>EUA</country>
<video>
<colour>yes</colour>
</video>
<rating system="Advisory">
<value>Programa impróprio para menores de 18 anos</value>
</rating>
<star-rating>
<value>3/5</value>
</star-rating>
</programme>
<programme start="20120116044500 -0200" stop="20120116054500 -0200" channel="\
Band HD" program_id="0000318080" event_id="00000000000005837088" series_key="">
<title lang="pt">Looper: Assassinos do Futuro</title>
<title lang="en">Looper</title>
<desc>Joe vive em 2044 e sua função é matar pessoas enviadas do futuro por \
associações criminosas. O que fará ao descobrir que uma dessas pessoas do \
futuro que terá que matar será ele próprio?</desc>
<credits>
<director>Rian Johnson</director>
<actor>Bruce Willis</actor>
<actor>Emily Blunt</actor>
<actor>Joseph Gordon-Levitt</actor>
</credits>
<date>2012</date>
<category lang="pt">Filme</category>
<category lang="pt">Ação</category>
<video>
<colour>yes</colour>
</video>
<rating system="Advisory">
<value>Programa impróprio para menores de 16 anos</value>
</rating>
<star-rating>
<value>3/5</value>
</star-rating>
</programme>
</tv>''')


class Test_Timezone(TestCase):

    def test_parse_datetime(self):
        ## '%Y%m%d%H%M%S %z'
        #from datetime import datetime
        from dateutil import parser
        from dateutil import zoneinfo
        utc = zoneinfo.gettz('UTC')
        start1 = '20120713033000 -0300'
        start1utc = '20120713063000 +0000'
        stop1 = '20120713050000 -0300'
        stop1utc = '20120713080000 +0000'
        ## dt1.parse(timestr, default, ignoretz, tzinfos)
        dt1 = parser.parse(start1)
        u = dt1.astimezone(utc).strftime('%Y%m%d%H%M%S %z')
        self.assertEqual(start1utc, u)
        dt2 = parser.parse(stop1)
        u = dt2.astimezone(utc).strftime('%Y%m%d%H%M%S %z')
        self.assertEqual(stop1utc, u)


class Test_XML_to_db(object):

    def test_Channel_1(self):
        channel = Channel.objects.get(channelid='Concert Channel')
        self.assertEquals(channel.display_names.values_list('lang__value',
            'value')[0], ('pt', 'Concert Channel',))
        self.assertEquals(channel.urls.count(), 0)

    def test_Programme_1(self):
        self.maxDiff = None
        programme = Programme.objects.get(
            guide__channel__display_names__value='Concert Channel')
        titles = [('pt', 'BBC Sessions: The Verve'),
                  ('en', 'BBC Sessions: Verve; The')]
        self.assertItemsEqual(
            programme.titles.values_list('lang__value', 'value'), titles)
        descs = (None, 'Uma impressionante atuação do The Verve no famoso \
estúdio Maida Vale, da BBC. Desfrute desta íntima, porém poderosa gravação da \
banda de Richard Ashcroft, que inclui músicas como Bitter Sweet Symphony e \
Love is Noise.')
        self.assertEquals(programme.descriptions.values_list('lang__value',
            'value')[0], descs)
        self.assertEquals(programme.date, '2008')
        self.assertItemsEqual(programme.categories.values_list('lang__value',
            'value'), [('pt', 'Espetáculo'), ('pt', 'Show')])
        self.assertEquals(programme.video_colour, 'yes')
        self.assertEquals(programme.rating.system, 'Advisory')
        self.assertEquals(programme.rating.value, '18')


class One_Raw_XML(Test_XML_to_db, TestCase):

    def test_Epg_Source(self):
        #from dateutil.parser import parse
        self.maxDiff = None
        self.assertEquals(self.xmltv_source.generator_info_name,
            'Revista Eletronica - Unidade Lorenz Ltda')
        self.assertEquals(self.xmltv_source.generator_info_url,
            'http://xmltv.revistaeletronica.com.br')
        self.assertEquals(self.epg_source.numberofElements, 1)

    def setUp(self):
        from tempfile import NamedTemporaryFile
        from django.conf import settings
        MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
        self.f = NamedTemporaryFile(suffix='.xml', dir=os.path.join(MEDIA_ROOT,
            'epg/'))
        self.f.write(input_xml_1)
        self.f.flush()
        self.epg_source = Epg_Source(filefield=self.f.name)
        self.epg_source.save()
        self.xmltv_source = XMLTV_Source.objects.create(filefield=self.f.name)
        XML_Epg_Importer(xml=self.f,
            xmltv_source=self.xmltv_source,
            epg_source=self.epg_source).import_to_db()

    def tearDown(self):
        self.f.close()

    def test_Models_count(self):
        self.assertEquals(Channel.objects.all().count(), 1)
        self.assertEquals(Programme.objects.all().count(), 1)
        self.assertEquals(Guide.objects.all().count(), 1)


class One_Zipped_XML(Test_XML_to_db, TestCase):

    def test_Epg_Source_Replace(self):
        #from dateutil.parser import parse
        self.maxDiff = None
        self.assertEquals(self.xmltv_source.generator_info_name,
                          'WWW.EPG.COM.BR')
        self.assertEquals(self.xmltv_source.generator_info_url,
                          'http://epg.com.br')
        self.assertEquals(self.epg_source.numberofElements, 1)

    def setUp(self):
        from tempfile import NamedTemporaryFile
        from django.conf import settings
        import os
        MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
        try:
            os.remove('/tmp/xmltv.xml')
            os.remove('/tmp/xmltv.xml.old')
        except OSError:
            pass
        self.f = NamedTemporaryFile(suffix='.xml', dir=os.path.join(MEDIA_ROOT,
            'epg/'))
        from zipfile import ZipFile
        zipped = ZipFile(self.f.name[:-3] + 'zip', 'w')
        zipped.writestr('xmltv.xml', input_xml_3)
        zipped.close()
        self.epg_source = Epg_Source(filefield=self.f.name[:-3] + 'zip')
        self.epg_source.save()
        self.xmltv_source = XMLTV_Source.objects.create(filefield=self.f.name)
        file_list = Zip_to_XML(self.epg_source.filefield.path)
        for f in file_list.get_all_files():
            XML_Epg_Importer(xml=f,
                epg_source=self.epg_source,
                xmltv_source=self.xmltv_source).import_to_db()

    def tearDown(self):
        self.f.close()

    def test_Models_count(self):
        self.assertEquals(Channel.objects.all().count(), 1)
        self.assertEquals(Programme.objects.all().count(), 1)
        self.assertEquals(Guide.objects.all().count(), 1)


class Two_Zipped_XMLs(Test_XML_to_db, TestCase):

    def setUp(self):
        import os
        from tempfile import NamedTemporaryFile
        from django.conf import settings
        MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
        self.f = NamedTemporaryFile(suffix='.zip', dir=os.path.join(MEDIA_ROOT,
            'epg/'))
        from zipfile import ZipFile
        files = {
            '100': input_xml_1,
            '505': input_xml_2,
        }
        try:
            for f in files.keys():
                os.remove('/tmp/{}.xml.old'.format(f))
                os.remove('/tmp/{}.xml'.format(f))
        except OSError:
            pass
        zipped = ZipFile(self.f, 'w')
        for key, value in files.items():
            zipped.writestr('{}.xml'.format(key), value)
        zipped.close()
        self.epg_source = Epg_Source(filefield=self.f.name)
        self.epg_source.save()
        self.xmltv_source = XMLTV_Source.objects.create(filefield=self.f.name)
        file_list = Zip_to_XML(self.epg_source.filefield.path)
        for f in file_list.get_all_files():
            XML_Epg_Importer(xml=f,
                epg_source=self.epg_source,
                xmltv_source=self.xmltv_source).import_to_db()

    def tearDown(self):
        self.f.close()

    def test_Epg_Source(self):
        #from dateutil.parser import parse
        self.assertEquals(self.xmltv_source.generator_info_name,
                          'WWW.EPG.COM.BR')
        self.assertEquals(self.xmltv_source.generator_info_url,
                          'http://epg.com.br')
        self.assertEquals(int(self.epg_source.numberofElements), 2)
        #self.assertEquals(self.epg_source.minor_start,
        #    parse('20120116000500 +0000'))
        #self.assertEquals(self.epg_source.major_stop,
        #    parse('20120116034500 +0000'))

    def test_Models_count(self):
        self.assertEquals(Channel.objects.all().count(), 2)
        self.assertEquals(Programme.objects.all().count(), 2)
        self.assertEquals(Guide.objects.all().count(), 2)

    def test_Channel_2(self):
        channel = Channel.objects.get(channelid='Band HD')
        self.assertEquals(channel.display_names.values_list('lang__value',
            'value')[0], ('pt', 'Band HD',))
        self.assertEquals(channel.urls.count(), 0)

    def test_Programme_2(self):
        programme = Programme.objects.get(
            guide__channel__display_names__value='Band HD')
        titles = [('pt', 'Três Homens em Conflito'),
                  ('en', 'The Good, The Bad and the Ugly')]
        self.assertItemsEqual(programme.titles.values_list('lang__value',
            'value'), titles)
        descs = (None, 'Durante a Guerra Civil Americana, três aventureiros '\
                       'tentam pôr as mãos numa fortuna.')
        self.assertEquals(programme.descriptions.values_list('lang__value',
            'value')[0], descs)
        self.assertEquals(programme.date, '1966')
        self.assertItemsEqual(programme.categories.values_list('lang__value',
            'value'), [('pt', 'Filme'), ('pt', 'Western')])
        self.assertEquals(programme.video_colour, 'yes')
        self.assertEquals(programme.rating.system, 'Advisory')
        self.assertEquals(programme.rating.value, '14')
        self.assertEquals(programme.country.value, 'Itália/Espanha')
        actors = ((('Clint Eastwood'), ), (('Lee Van Cleef'),),
                  (('Eli Wallach'),), (('Rada Rassimov'),),
                  (('Mario Brega'), ), )
        self.assertItemsEqual(programme.actors.values_list('name'), actors)
        self.assertItemsEqual(programme.directors.values_list('name'),
            ((('Sergio Leone'),), ))
        self.assertItemsEqual(programme.star_ratings.values_list('value'),
            [('5/5',)])


class APITest(TestCase):

    def setUp(self):
        from tempfile import NamedTemporaryFile
        from django.conf import settings
        MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
        self.f = NamedTemporaryFile(suffix='.zip',
            dir=os.path.join(MEDIA_ROOT, 'epg/'))
        from zipfile import ZipFile
        zipped = ZipFile(self.f, 'w')
        files = {
            '100': input_xml_1,
            '505': input_xml_2,
            '101': input_xml_1,
            '506': input_xml_2
        }
        try:
            for f in files.keys():
                os.remove('/tmp/{}.xml.old'.format(f))
                os.remove('/tmp/{}.xml'.format(f))
        except OSError:
            pass
        zipped = ZipFile(self.f, 'w')
        for key, value in files.items():
            zipped.writestr('{}.xml'.format(key), value)
        zipped.close()
        self.epg_source = Epg_Source(filefield=self.f.name)
        self.epg_source.save()
        xmltv_source = XMLTV_Source.objects.create(filefield=self.f.name)
        file_list = Zip_to_XML(self.epg_source.filefield.path)
        for f in file_list.get_all_files():
            #import pdb; pdb.set_trace()
            XML_Epg_Importer(xml=f,
                xmltv_source=xmltv_source,
                epg_source=self.epg_source).import_to_db()

    def tearDown(self):
        self.f.close()

    def test_Channel_REST(self):
        c = Client()
        urlchannel = reverse('epg:api_dispatch_list',
            kwargs={'resource_name': 'channel', 'api_name': 'v1'})
        self.assertEqual(urlchannel, '/tv/api/epg/v1/channel/')
        response = c.get(urlchannel)
        expected = [
            {"channelid": "Concert Channel", "display_name": "Concert Channel",
             "icons": [], "id": 1, "resource_uri": "/tv/api/epg/v1/channel/1/",
             "urls": []},
            {"channelid": "Band HD", "display_name": "Band HD", "icons": [],
            "id": 2, "resource_uri": "/tv/api/epg/v1/channel/2/", "urls": []}
        ]
        self.assertEquals(response.status_code, 200, msg=response.request)
        jobj = json.loads(response.content)
        objects = jobj['objects']
        self.maxDiff = None
        self.assertItemsEqual(objects, expected)
        # More tests
        test_cases = (
            {'expected': expected,
             'requests': (('/tv/api/epg/v1/channel/', {}),
                  ('/tv/api/epg/v1/channel/', {}),
                  ('/tv/api/epg/v1/channel/set/1;2/', {}),
              )
            },
            {'expected': [expected[1]],
              'requests': (('/tv/api/epg/v1/channel/', {'channelid': 'Band HD'}),
              )
            },
        )

        for test in test_cases:
            for request in test['requests']:
                response = c.get(request[0], request[1])
                self.assertEquals(response.status_code, 200,
                    msg=response.request)
                jobj = json.loads(response.content)
                objects = jobj['objects']
                self.assertEquals(objects, test['expected'],
                    msg=response.request)
        # Check for 404 if resource doesn't exists
        response = c.get('/tv/api/epg/v1/channel/3/')
        self.assertEquals(response.status_code, 404)

    def test_Programme_REST(self):
        self.maxDiff = None
        c = Client()
        expected = [{'actors': [],
          'audio_present': None,
          'audio_stereo': None,
          'categories': ['/tv/api/epg/v1/category/1/',
                         '/tv/api/epg/v1/category/2/'],
          'date': '2008',
          'description': 'Uma impressionante atua\xe7\xe3o do The Verve no \
famoso est\xfadio Maida Vale, da BBC. Desfrute desta \xedntima, por\xe9m \
poderosa grava\xe7\xe3o da banda de Richard Ashcroft, que inclui m\xfasicas \
como Bitter Sweet Symphony e Love is Noise.',
          'directors': [],
          'id': '1',
          'length': None,
          'programid': '0000257856',
          'rating': '/tv/api/epg/v1/rating/1/',
          'resource_uri': '/tv/api/epg/v1/programme/1/',
          'secondary_title': None,
          'star_ratings': [],
          'title': 'BBC Sessions: The Verve',
          'video_aspect': None,
          'video_colour': 'yes',
          'video_present': None,
          'video_quality': None},
         {'actors': [{'id': '1',
                      'name': 'Clint Eastwood',
                      'resource_uri': '/tv/api/epg/v1/actor/1/',
                      'role': None},
                     {'id': '2',
                      'name': 'Lee Van Cleef',
                      'resource_uri': '/tv/api/epg/v1/actor/2/',
                      'role': None},
                     {'id': '3',
                      'name': 'Eli Wallach',
                      'resource_uri': '/tv/api/epg/v1/actor/3/',
                      'role': None},
                     {'id': '4',
                      'name': 'Rada Rassimov',
                      'resource_uri': '/tv/api/epg/v1/actor/4/',
                      'role': None},
                     {'id': '5',
                      'name': 'Mario Brega',
                      'resource_uri': '/tv/api/epg/v1/actor/5/',
                      'role': None}],
          'audio_present': None,
          'audio_stereo': None,
          'categories': ['/tv/api/epg/v1/category/3/',
                         '/tv/api/epg/v1/category/4/'],
          'date': '1966',
          'description': 'Durante a Guerra Civil Americana, tr\xeas \
aventureiros tentam p\xf4r as m\xe3os numa fortuna.',
          'directors': [{'id': '1',
                         'name': 'Sergio Leone',
                         'resource_uri': '/tv/api/epg/v1/staff/1/'}],
          'id': '2',
          'length': None,
          'programid': '0000025536',
          'rating': '/tv/api/epg/v1/rating/2/',
          'resource_uri': '/tv/api/epg/v1/programme/2/',
          'secondary_title': None,
          'star_ratings': ['/tv/api/epg/v1/star_rating/1/'],
          'title': 'Tr\xeas Homens em Conflito',
          'video_aspect': None,
          'video_colour': 'yes',
          'video_present': None,
          'video_quality': None}]
        response = c.get('/tv/api/epg/v1/programme/')
        self.assertEquals(response.status_code, 200, msg=response.request)
        # Get by actor name
        response = c.get('/tv/api/epg/v1/programme/',
            {'actors_name': 'Clint Eastwood'})
        #print(response)
        # More tests
        test_cases = (
            {'expected': expected,
             'requests': (('/tv/api/epg/v1/programme/', {}),
                ('/tv/api/epg/v1/programme/', {}),
                ('/tv/api/epg/v1/programme/set/1;2/', {}),
              )
            },
            {'expected': [expected[1]],
              'requests': (('/tv/api/epg/v1/programme/',
                    {'actors_name': 'Clint Eastwood'}),
              )
            },
        )

        for test in test_cases:
            for request in test['requests']:
                response = c.get(request[0], request[1])
                self.assertEquals(response.status_code, 200,
                    'status:%d uri:%s param:%s' % (response.status_code,
                        request[0], request[1]))
                self.assertEquals(
                    json.loads(response.content)['objects'].sort(),
                    test['expected'].sort())
        # Check for 404 if resource doesn't exists
        response = c.get('/tv/api/epg/v1/programme/3/')
        self.assertEquals(response.status_code, 404)

    def test_Guide_Query_Timestamp(self):
        c = Client()
        url = reverse('epg:api_dispatch_list',
            kwargs={'resource_name': 'guide', 'api_name': 'v1'},
            )
        response = c.get(url)
        jobj = json.loads(response.content)
        self.assertEqual(jobj['meta']['total_count'], 2)
        response = c.get(url,
            {'start_timestamp': 1326683100 - 3600 * 3,
             'stop_timestamp': 1326685500 - 3600 * 3})
        jobj = json.loads(response.content)
        self.assertEqual(1, jobj['meta']['total_count'])
        response = c.get(url,
            {'start_timestamp': 1326683100 - 3600 * 3})
        jobj = json.loads(response.content)
        self.assertEqual(1, jobj['meta']['total_count'])
        response = c.get(url,
            {'stop_timestamp': 1326685500 - 3600 * 3})
        response = c.get(url)
        jobj = json.loads(response.content)
        self.assertContains(response, 'Mario Brega')
        self.assertEqual(2, jobj['meta']['total_count'])

    def test_Programme_Schema(self):
        c = Client()
        urlschema = reverse('epg:api_get_schema',
            kwargs={'resource_name': 'programme', 'api_name': 'v1'})
        response = c.get(urlschema)
        self.assertContains(response, 'actors')
        self.assertContains(response, 'audio_present')
        self.assertContains(response, 'audio_stereo')
        self.assertContains(response, 'categories')
        self.assertContains(response, 'date')
        self.assertContains(response, 'description')
        self.assertContains(response, 'directors')
        self.assertContains(response, 'id')
        self.assertContains(response, 'length')
        self.assertContains(response, 'programid')
        self.assertContains(response, 'rating')
        self.assertContains(response, 'resource_uri')
        self.assertContains(response, 'secondary_title')
        self.assertContains(response, 'star_ratings')
        self.assertContains(response, 'title')
        self.assertContains(response, 'video_aspect')
        self.assertContains(response, 'video_colour')
        self.assertContains(response, 'video_present')
        self.assertContains(response, 'video_quality')
        self.assertContains(response, 'filtering')


class ParseRatingTest(TestCase):

    def setUp(self):
        from tempfile import NamedTemporaryFile
        from django.conf import settings
        import os
        MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
        self.f = NamedTemporaryFile(suffix='.zip',
            dir=os.path.join(MEDIA_ROOT, 'epg/'))
        from zipfile import ZipFile
        files = {
            'rat': input_xml_rating
        }
        for f in files.keys():
            try:
                os.remove('/tmp/{}.xml.old'.format(f))
                os.remove('/tmp/{}.xml'.format(f))
            except OSError:
                pass
        zipped = ZipFile(self.f, 'w')
        for key, value in files.items():
            zipped.writestr('{}.xml'.format(key), value)
        zipped.close()
        self.epg_source = Epg_Source(filefield=self.f.name)
        self.epg_source.save()
        xmltv_source = XMLTV_Source.objects.create(filefield=self.f.name)
        file_list = Zip_to_XML(self.epg_source.filefield.path)
        for f in file_list.get_all_files():
            XML_Epg_Importer(xml=f,
                xmltv_source=xmltv_source,
                epg_source=self.epg_source).import_to_db()

    def tearDown(self):
        self.f.close()

    def test_linked_list_guide(self):
        c = Client()
        url = reverse('epg:api_dispatch_list',
            kwargs={'resource_name': 'guide', 'api_name': 'v1'},
            )
        channel = Channel.objects.get()
        response = c.get(url, data={'channel': '{}'.format(channel.id)})
        jobj = json.loads(response.content)
        obj = jobj['objects']
        self.assertEqual(obj[0]['previous'], None)
        self.assertEqual(obj[0]['resource_uri'], obj[1]['previous'])
        self.assertEqual(obj[1]['resource_uri'], obj[2]['previous'])
        self.assertEqual(obj[2]['resource_uri'], obj[3]['previous'])
        self.assertEqual(obj[3]['resource_uri'], obj[4]['previous'])
        self.assertEqual(obj[0]['next'], obj[1]['resource_uri'])
        self.assertEqual(obj[1]['next'], obj[2]['resource_uri'])
        self.assertEqual(obj[2]['next'], obj[3]['resource_uri'])
        self.assertEqual(obj[3]['next'], obj[4]['resource_uri'])
        self.assertEqual(obj[4]['next'], None)

    def test_create_rating(self):
        ratings = Rating.objects.all().order_by('int_value')
        self.assertEqual(5, len(ratings))
        r2 = Rating(system='Advisory',
                   value='Programa impróprio para menores de 12 anos')
        r2.save()
        #import pdb; pdb.set_trace()
        r0n, c = Rating.objects.get_or_create(system='Advisory',
                   value='Programa livre para todas as idades')
        self.assertEqual(r0n.int_value, 0)
        self.assertTrue(c)
        ratings = Rating.objects.all().order_by('int_value')
        self.assertEqual(7, len(ratings))

    def test_get_rating(self):
        rating0 = Rating.objects.get(
            value='0')
        self.assertEqual(0, rating0.int_value)
        rating10 = Rating.objects.get(
            value='10')
        self.assertEqual(10, rating10.int_value)
        rating14 = Rating.objects.get(
            value='14')
        self.assertEqual(14, rating14.int_value)
        rating18, created = Rating.objects.get_or_create(
            system='Advisory',
            value='18')
        self.assertFalse(created)
        self.assertEqual(18, rating18.int_value)
        rating16, created = Rating.objects.get_or_create(
            system='Advisory',
            value='16')
        self.assertFalse(created)
        self.assertEqual(16, rating16.int_value)

    def test_rating_api(self):
        c = Client()
        url = reverse('epg:api_dispatch_list',
            kwargs={'resource_name': 'guide', 'api_name': 'v1'},
            )
        response = c.get(url)
        jobj = json.loads(response.content)
        self.assertEqual(len(jobj['objects']), 5)
        guide = Guide.objects.all()[0]
        urlguide4 = reverse('epg:api_dispatch_detail',
            kwargs={'resource_name': 'guide',
                    'api_name': 'v1', 'pk': '{}'.format(guide.id)},
            )
        self.assertEqual(urlguide4, '/tv/api/epg/v1/guide/{}/'.format(guide.id))
        response = c.get(urlguide4)
        jobj = json.loads(response.content)
        response = c.get(url,
            {'start_timestamp': 1326689100.0 - 3600 * 3,
             'stop_timestamp': 1326696300.0 - 3600 * 3})
        jobj = json.loads(response.content)
        self.assertEqual(jobj['objects'][0]['programme']['rating']
            ['resource_uri'],
            '/tv/api/epg/v1/rating/{}/'.format(guide.programme.rating.id))

    def test_get_rating_limit(self):
        c = Client()
        url = reverse('epg:api_dispatch_list',
            kwargs={'resource_name': 'rating', 'api_name': 'v1'}
            )
        self.assertEqual('/tv/api/epg/v1/rating/', url)
        response = c.get(url + '?limit=0')
        jobj = json.loads(response.content)
        self.assertEqual(jobj['meta']['total_count'], 5)

input_xml_conflict = str('''<?xml version="1.0" encoding="UTF-8"?>
<tv generator-info-name="Revista Eletronica - Unidade Lorenz Ltda" \
generator-info-url="http://xmltv.revistaeletronica.com.br">
<programme start="20130301070000 -0300" stop="20130301080000 -0300" \
channel="10" program_id="1">
    <title lang="pt">Teste 1</title>
</programme>
<programme start="20130301080000 -0300" stop="20130301090000 -0300" \
    channel="10" program_id="2">
    <title lang="pt">Teste 2</title>
</programme>
<programme channel="10" program_id="3" \
start="20130301090000 -0300" \
 stop="20130301100000 -0300" \
>
    <title lang="pt">Teste 3</title>
</programme>
<programme channel="10" program_id="4" \
start="20130301100000 -0300" \
 stop="20130301110000 -0300" \
>
    <title lang="pt">Teste 4</title>
</programme>
<programme channel="10" program_id="5" \
start="20130301110000 -0300" \
 stop="20130301120000 -0300" \
>
    <title lang="pt">Teste 5</title>
</programme>
<programme channel="10" program_id="6" \
start="20130301120000 -0300" \
 stop="20130301130000 -0300" \
>
    <title lang="pt">Teste 6</title>
</programme>
<programme channel="10" program_id="7" \
start="20130301130000 -0300" \
 stop="20130301140000 -0300" \
>
    <title lang="pt">Teste 7</title>
</programme>
</tv>
''')
input_xml_conflict1 = str('''
<programme channel="10" program_id="8" \
start="20130301110000 -0300" \
 stop="20130301120000 -0300" \
>
    <title lang="pt">Conflito 5</title>
</programme>
''')


class GuideConflictTest(TestCase):

    def setUp(self):
        from tempfile import NamedTemporaryFile
        from django.conf import settings
        import os
        try:
            os.remove('/tmp/conflict.xml')
            os.remove('/tmp/conflict.xml.old')
        except OSError:
            pass
        MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
        self.f = NamedTemporaryFile(suffix='.zip',
            dir=os.path.join(MEDIA_ROOT, 'epg/'))
        from zipfile import ZipFile
        zipped = ZipFile(self.f, 'w')
        zipped.writestr('conflict.xml', input_xml_conflict)
        zipped.close()
        self.epg_source = Epg_Source(filefield=self.f.name)
        self.epg_source.save()
        xmltv_source = XMLTV_Source.objects.create(filefield=self.f.name)
        file_list = Zip_to_XML(self.epg_source.filefield.path)
        for f in file_list.get_all_files():
            XML_Epg_Importer(xml=f,
                xmltv_source=xmltv_source,
                epg_source=self.epg_source).import_to_db()

    def tearDown(self):
        self.f.close()

    def test_create(self):
        nch = Channel.objects.all().count()
        self.assertEqual(1, nch)
        prog = Programme.objects.get(titles__value='Teste 1')
        guides = Guide.objects.filter(channel__display_names__value='10')
        self.assertEqual(guides.count(), 7)

    def test_delete_conflict(self):
        from dateutil.parser import parse
        from django.utils.timezone import utc
        from pytz import timezone
        #start="20130301090000 -0300" stop="20130301100000 -0300" \
        start = parse("20130301085900 -0300").astimezone(utc)
        stop = parse("20130301100000 -0300").astimezone(utc)
        lang = Lang.objects.get(value='pt')
        title = Title.objects.create(lang=lang, value='Novo com conflito')
        prog = Programme.objects.create(programid=100)
        prog.titles.add(title)
        ## Before replace
        self.assertEqual(Guide.objects.all().count(), 7)
        #import pdb; pdb.set_trace()
        channel = Channel.objects.get(display_names__value='10')
        G, created = Guide.objects.get_or_create(
            start=start, stop=stop,
            channel_id=channel.id, programme=prog)
        self.assertTrue(created)
        ## After must be only 6 guides
        self.assertEqual(Guide.objects.all().count(), 6)
        self.assertEqual(G.next.programme.titles.all()[0].value,
                         'Teste 4', 'O proximo deveria ser Teste 4')
        self.assertEqual(G.previous.programme.titles.all()[0].value,
                         'Teste 1', 'O anterior deveria ser Teste 11')
        self.assertEqual(G.previous.next, G)
        self.assertEqual(G.next.previous, G)
        g1 = Guide.objects.all()[0]
        self.assertEqual(g1.next, G)

    def test_delete_conflict_start(self):
        from dateutil.parser import parse
        from django.utils.timezone import utc
        from pytz import timezone
        #start="20130301090000 -0300" stop="20130301100000 -0300" \
        start = parse("20130301060000 -0300").astimezone(utc)
        stop = parse("20130301070100 -0300").astimezone(utc)
        self.assertEqual(Guide.objects.all().count(), 7)
        lang = Lang.objects.get(value='pt')
        title = Title.objects.create(lang=lang, value='Novo com conflito')
        prog = Programme.objects.create(programid=100)
        prog.titles.add(title)
        channel = Channel.objects.get(display_names__value='10')
        G, created = Guide.objects.get_or_create(
            start=start, stop=stop,
            channel_id=channel.id, programme=prog)
        self.assertTrue(created)
        self.assertIsNone(G.previous)
        self.assertEqual(Guide.objects.all().count(), 7)
        ## Create new on start
        start = parse("20130301050000 -0300").astimezone(utc)
        stop = parse("20130301060000 -0300").astimezone(utc)
        G, created = Guide.objects.get_or_create(
            start=start, stop=stop,
            channel_id=channel.id, programme=prog)
        guides = Guide.objects.all()
        self.assertEqual(guides.count(), 8)

    def test_delete_conflict_end(self):
        from dateutil.parser import parse
        from django.utils.timezone import utc
        from pytz import timezone
        #start="20130301090000 -0300" stop="20130301100000 -0300" \
        start = parse("20130301133000 -0300").astimezone(utc)
        stop = parse("20130301135000 -0300").astimezone(utc)
        self.assertEqual(Guide.objects.all().count(), 7)
        lang = Lang.objects.get(value='pt')
        title = Title.objects.create(lang=lang, value='Novo com conflito')
        prog = Programme.objects.create(programid=100)
        prog.titles.add(title)
        channel = Channel.objects.get(display_names__value='10')
        G, created = Guide.objects.get_or_create(
            start=start, stop=stop,
            channel_id=channel.id, programme=prog)
        self.assertTrue(created)

