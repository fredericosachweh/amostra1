#!/usr/bin/env python
# -*- encoding:utf8 -*-
import xml.etree.ElementTree as ET
from lxml import etree
from datetime import timedelta
from dateutil.parser import parse
from lxml.etree import XMLSyntaxError


class xmlVerification:

    linkxml = None

    def xml_validation(self, filename):
        try:
            with open(filename) as f:
                doc = etree.parse(f)
            print "This document is valid to verification"
        except XMLSyntaxError as e:
            print "This documment have some problems:"
            print e
            exit(1)

    def insert_unavailable(self, channel, start, stop, rating):
        self.linkxml.write(u'<programme start="%s" stop="%s" channel="%s">'.encode('ascii', 'xmlcharrefreplace') % (start, stop, channel))
        self.linkxml.write(u'<title lang="pt">Programação Indisponível</title>'.encode('ascii', 'xmlcharrefreplace'))
        self.linkxml.write(u'<category lang="pt">Categoria Indisponível</category>'.encode('ascii', 'xmlcharrefreplace'))
        self.linkxml.write(u'<country>País Indisponível</country>'.encode('ascii', 'xmlcharrefreplace'))
        self.linkxml.write("<video>")
        self.linkxml.write("<colour>yes</colour>")
        self.linkxml.write("</video>")
        self.linkxml.write("<rating system=\"Advisory\">")
        self.linkxml.write("<value>%s</value>" % rating)
        self.linkxml.write("</rating>")
        self.linkxml.write("</programme>")

    def xml_verification(self, filename):
        xml = filename
        current_channel = None

        # create XML - TV
        self.linkxml = open('link_guide.xml', 'w')

        head = "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>"
        tv_info = "<tv generator-info-name=\"WWW.EPG.COM.BR\" generator-info-url=\"http://epg.com.br\">"
        self.linkxml.write(head)
        self.linkxml.write(tv_info)
        past_elem = None

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

            # if elem.find('title') is not None:
            #    title = elem.find('title').text

            # Get time and convert it to UTC
            start = parse(elem.get('start'))
            stop = parse(elem.get('stop'))

            if (current_channel is None) or (current_channel != channel):
                current_channel = channel
                aux_stop = parse(elem.get('stop'))
                aux_start = parse(elem.get('start'))
                past_elem = elem
            else:
                if start > stop:
                    # print channel
                    # print title
                    # print start
                    # print stop
                    print 'programa com problema: start > stop'
                elif aux_start > start:
                    # print channel
                    # print title
                    # print start
                    # print stop
                    print 'programa com problema: start do atual < start do anterior'
                elif start > aux_stop:
                    print 'intervalo vazio'
                    if (start - aux_stop) > timedelta(minutes=5):
                        print 'intervalo maior que 5 min'
                        self.linkxml.write(ET.tostring(past_elem))
                        insert = True
                        while insert:
                            if (start - aux_stop) <= timedelta(minutes=60):
                                self.insert_unavailable(channel, aux_stop, start, rating)
                                insert = False
                            else:
                                self.insert_unavailable(channel, aux_stop, aux_stop + timedelta(minutes=60), rating)
                                aux_stop += timedelta(minutes=60)

                        aux_stop = parse(elem.get('stop'))
                        aux_start = parse(elem.get('start'))
                        past_elem = elem
                    else:
                        print 'intervalo menor que 5 min'
                        past_elem.set('stop', elem.get('start'))
                        aux_stop = parse(elem.get('stop'))
                        aux_start = parse(elem.get('start'))
                        self.linkxml.write(ET.tostring(past_elem))
                        past_elem = elem
                elif start < aux_stop:
                    print 'intercessão'
                    past_elem.set('stop', elem.get('start'))
                    aux_stop = parse(elem.get('stop'))
                    aux_start = parse(elem.get('start'))
                    self.linkxml.write(ET.tostring(past_elem))
                    past_elem = elem
                elif start == aux_stop:
                    aux_stop = parse(elem.get('stop'))
                    aux_start = parse(elem.get('start'))
                    self.linkxml.write(ET.tostring(past_elem))
                    past_elem = elem

        self.linkxml.write(ET.tostring(past_elem))
        tv_end = "</tv>"
        self.linkxml.write(tv_end)

xml = 'arquivo.xml'
verif = xmlVerification()
verif.xml_validation(xml)
verif.xml_verification(xml)
