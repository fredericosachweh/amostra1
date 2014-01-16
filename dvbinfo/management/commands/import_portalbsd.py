# -*- coding: utf-8 -*-

from django.core.management import BaseCommand
from dvbinfo.models import Satellite
from dvbinfo.models import Transponder
from dvbinfo.models import DvbsChannel
#from optparse import make_option
from datetime import date
from BeautifulSoup import BeautifulSoup
import urllib2
import re


class Command(BaseCommand):

    base_url = 'http://www.brasilsatdigital.com.br/novo/'
    help = 'Automatically fetch and import tunning info data from PortalBSD\'s\
 website'

    def _get_soup(self, url):
        request = urllib2.Request(url)
        fd = urllib2.urlopen(request)
        html = fd.read()
        return BeautifulSoup(html)

    def _create_satellite(self, sat_soup, sat_name, sat_location):
        detailed = sat_soup.find('div', attrs={'class': 'contentDetalhes'})
        if detailed is not None:
            sat_logo = self.base_url + detailed.find('img')['src']
            info = detailed.findAll('div')[2].text
        else:
            return
        res = re.findall(
            u'(Bandas:.*)(Polarização:.*)(Capacidade:.*)(Lançamento:.*)\
(Vida Útil:.*)', info)
        if len(res) > 0:
            sat_info = "%s\n%s\n%s\n%s\n%s" % (res[0][0], res[0][1], res[0][2],
                res[0][3], res[0][4])
        else:
            sat_info = ''
        # Separate location degrees and direction
        ((degrees, direction),) = re.findall(u'^-?(\d+\.?\d*) °([EWSNewsn])$',
            sat_location)
        # Create Satellite object
        satellite, created = Satellite.objects.get_or_create(name=sat_name,
            azimuth_degrees=degrees, azimuth_direction=direction,
            info=sat_info, logo=sat_logo)
        return satellite

    def _create_transponder(self, tr, band, satellite):
        td = tr.findAll('td', {'class': None})
        # Get tunning info
        res = re.findall('^([0-9]*) (.)([0-9]*) \| (\?|[0-9]/[0-9])(.*)$',
            td[0].text)
        if len(res):
            freq = res[0][0]
            pol = res[0][1]
            sr = res[0][2]
            fec = res[0][3]
            domain = res[0][4]
        else:
            return None  # Invalid transponder data
        self.stdout.write('      %s %s %s\n' % (freq, pol, sr))
        # Logo
        logo = self.base_url + td[1].find('img')['src']
        # Name
        name = td[3].find('a')['title']
        if not name.lower().startswith('mux'):
            name = ''
        # Modulation
        res = re.findall('^(IP/DVB|DVB-S2|DVB-S)(QPSK|8PSK)?$', td[6].text)
        if len(res):
            system = res[0][0]
            modulation = res[0][1]
        else:
            system = None
            modulation = None
        # Create the Transponder object
        transponder, created = Transponder.objects.get_or_create(name=name,
            band=band, frequency=freq, symbol_rate=sr, polarization=pol,
            fec=fec, system=system, modulation=modulation, logo=logo,
            satellite=satellite)
        return transponder

    def _create_channel(self, tr, transponder):
        td = tr.findAll('td', {'class': None})
        # Name
        name = td[3].find('a')['title']
        if name.lower().startswith('mux'):
            return
        self.stdout.write('        %s\n' % name)
        # Idiom and Category
        res = re.findall('(.*) \| (.*)', td[3].find('span').text)
        idiom = ''
        category = ''
        if len(res):
            if res[0][0]:
                idiom = res[0][0]
            if res[0][1]:
                category = res[0][1]
        # Logo
        logo = self.base_url + td[1].find('img')['src']
        # Definition
        d = td[5].find('img')['title']
        if d == u'SD 4:3 - Definição Padrão':
            definition = 'SD'
        elif d == u'HD 16:9 - Alta Definição 1920x1080':
            definition = 'HD'
        elif d == u'Canal 3D':
            definition = '3D'
        elif d == u'SD - Definição Padrão':
            definition = 'SD'
        elif d == u'HD - Alta Definição':
            definition = 'HD'
        else:
            raise Exception('Unknown definition: %s' % d)
        # Codec and Crypto
        codec = td[7].contents[0] if len(td[7].contents) >= 1 else None
        crypto = td[7].contents[2] if len(td[7].contents) >= 3 else None
        if codec == u'- ':
            codec = None
        if crypto == u'-':
            crypto = None
        # Last info
        last_info = None
        last_update = None
        c = td[11].contents
        if len(c) is 5:
            last_info = u'%s\n%s' % (c[0], c[4])
            try:
                res = re.findall('([0-9]*)/([0-9]*)/([0-9]*)', c[2].text)
                last_update = date(int(res[0][2]), int(res[0][1]),
                    int(res[0][0]))
            except Exception as inst:
                last_update = None
                raise inst

        channel, created = DvbsChannel.objects.get_or_create(name=name,
            idiom=idiom, category=category, logo=logo, definition=definition,
            transponder=transponder)
        channel.codec = codec
        channel.crypto = crypto
        channel.last_info = last_info
        channel.last_update = last_update
        channel.save()

    def handle(self, *args, **kwargs):
        # Get list of satellites in index page
        self.stdout.write('Getting index page...\n')
        soup = self._get_soup(self.base_url + 'index.php')

        # name kw is already used by BeautifulSoup
        for sat in soup.find('select', attrs={'name': 'canal'}).findAll(
            'option'):
            if sat['value']:
                results = re.findall('(.*) - (.*)', sat.string)
                sat_location = results[0][0]
                sat_name = results[0][1]

                # Input arguments: if satellites are provided as args
                # we only import them
                if len(args):
                    res = re.findall('([0-9]*) .([A-Z])', sat_location)
                    sl = res[0][0] + res[0][1]
                    # Identify satellites by they location. Ex: 10E 70W
                    if sl not in args:
                        continue

                # Fetch satellite page HTML
                self.stdout.write('Fetching %s - %s\n' % (sat_location,
                    sat_name))
                sat_url = re.findall('parent\.location\.href=\'(.*)\';',
                    sat['value'])
                sat_soup = self._get_soup(self.base_url + sat_url[0])

                # Create Satellite object
                satellite = self._create_satellite(sat_soup, sat_name,
                    sat_location)

                # Get transponders and channels
                tables = sat_soup.findAll('table', width='960')
                # Browse all tables in the page
                for index in range(0, len(tables), 2):
                    # Get band
                    text = tables[index].find('tr').find('td',
                        attrs={'class': None}).text
                    if text.startswith(u'Canais do satélite'):
                        res = re.findall(
                            u'^Canais do satélite .* - Banda (.*)$', text)
                        band = res[0]
                        self.stdout.write('  %s band\n' % band)
                    else:
                        raise Exception('Error obtaining Band')

                    # Transponders table
                    tt = tables[index + 1]
                    rows = tt.findAll('tr')[1:]  # Skip header
                    i = 0
                    #for i in range(0, len(rows)):
                    while i < len(rows):
                        td = rows[i].findAll('td', {'class': None})

                        # Case 1: Mux with PAC link - follow link and skip
                        # channels above if any
                        if td[4].find('img', alt='Ver pacote de canais'):
                            url_mux = self.base_url + 'satelite_canais.php' +\
                                td[4].find('img',
                                    alt='Ver pacote de canais').parent['href']
                            # Fetch Mux
                            self.stdout.write('    Fetching Mux: %s\n' % \
                                td[3].find('a')['title'])
                            mux_soup = self._get_soup(url_mux)
                            mux_tables = mux_soup.findAll('table', width='960')
                            if len(mux_tables) is not 2:
                                continue
                            # Skip tables's header
                            mux_rows = mux_tables[1].findAll('tr')[1:]
                            # Create the transponder
                            tp = self._create_transponder(mux_rows[0], band,
                                satellite)
                            if not isinstance(tp, Transponder):
                                continue
                            # Create the channels
                            [self._create_channel(row, tp) for row in mux_rows\
                                if isinstance(tp, Transponder)]

                            # Forward to next transponder
                            while (i + 1) < len(rows) and len(rows[i + 1\
                                ].findAll('td', {'class': None})[0].text) is 0:
                                i = i + 1
                        # Case 2: Transponder with one (or multiple) channels
                        # Get all channels
                        else:
                            # Create the transponder
                            tp = self._create_transponder(rows[i], band,
                                satellite)
                            # Create the channels
                            if isinstance(tp, Transponder):
                                self._create_channel(rows[i], tp)
                            while (i + 1) < len(rows) and len(rows[i + 1\
                                    ].findAll('td', {'class': None})[0].text\
                                    ) is 0:
                                i = i + 1
                                if isinstance(tp, Transponder):
                                    self._create_channel(rows[i], tp)

                        # Increment
                        i = i + 1
