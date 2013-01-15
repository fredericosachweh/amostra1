# -*- coding: utf-8 -*-

from django.core.management import BaseCommand
from dvbinfo.models import PhysicalChannel
from dvbinfo.models import VirtualChannel
from dvbinfo.models import State
from dvbinfo.models import City
from BeautifulSoup import BeautifulSoup
import urllib2
import logging


class Command(BaseCommand):

    base_url = 'http://pt.wikipedia.org/wiki/Anexo:\
Lista_de_canais_da_televis%C3%A3o_digital_brasileira'
    help = 'Automatically fetch and import brazillian digital tv tunning info\
 from:\n  %s' % base_url

    def _get_soup(self, url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        request = urllib2.Request(url, None, headers)
        fd = urllib2.urlopen(request)
        html = fd.read()
        return BeautifulSoup(html)

    def handle(self, *args, **kwargs):
        # Get list of satellites in index page
        self.stdout.write('Getting index page...\n')
        soup = self._get_soup(self.base_url)

        for e in soup.findAll(['h3', 'h4', 'table']):
            if e.name == 'h3' and e.text:
                try:
                    # State
                    state = e.find('span', attrs={'class': 'mw-headline'}).text
                    self.stdout.write('   %s\n' % state)
                    S, created = State.objects.get_or_create(name=state)
                except AttributeError:
                    pass
                except:
                    pass
            elif e.name == 'h4' and e.text:
                try:
                    # City
                    city = e.find('span', attrs={'class': 'mw-headline'}).text
                    self.stdout.write('      %s\n' % city)
                    C, created = City.objects.get_or_create(name=city, state=S)
                except AttributeError:
                    pass
                except:
                    pass
            elif e.name == 'table':
                # Channel
                attrs = dict(e.attrs)
                if attrs.get('class') and attrs['class'] == 'wikitable sortable':
                    for tr in e.findAll('tr'):
                        dados = [td for td in tr.findAll('td')]
                        if len(dados):
                            epg = False
                            ginga = False
                            if len(dados) == 5:
                                p, v, n, f, e = dados
                                # EPG flag
                                if e.text == u'Sim':
                                    epg = True
                            elif len(dados) == 7:
                                p, v, n, f, e, i, l = dados
                                # EPG flag
                                if e.text == u'Sim':
                                    epg = True
                                # Interactivity
                                if i.text == u'Sim':
                                    ginga = True
                            elif len(dados) == 4:
                                p, v, n, f = dados
                            # Remove '*' from name
                            name = n.text.replace('*', '')
                            self.stdout.write('         %s|%s|%s\n' % (name,
                                p.text, C))
                            try:
                                number = int(p.text)
                                P, created = PhysicalChannel.objects.get_or_create(
                                    number=number, city=C)
                                float(v.text)
                                V, created = VirtualChannel.objects.get_or_create(
                                    number=v.text, name=name, epg=epg,
                                    physical_channel=P)
                            except:
                                pass
