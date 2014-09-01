#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from lxml import etree
from datetime import datetime
from datetime import timedelta
from datetime import time
import sys
import getopt

def programmeXML(start, stop, channel, rate):
    # create XML - Programme
    programme = etree.Element('programme')
    programme.attrib['start'] = start
    programme.attrib['stop'] = stop
    programme.attrib['channel'] = 'static_' + channel.decode("utf-8")

    # create XML - Title
    title_pt = etree.Element('title')
    title_pt.attrib['lang'] = 'pt'
    if channel.decode("utf-8") == u'Áudio':
        title_pt.text = u'Programação de ' + channel.decode("utf-8")
    else:
        title_pt.text = u'Programação ' + channel.decode("utf-8")
    programme.append(title_pt)

    # create XML - Credits
    credits = etree.Element('credits')
    actor = etree.Element('actor')
    actor.text = 'CIANET'
    credits.append(actor)
    programme.append(credits)

    # create XML - Date
    date = etree.Element('date')
    date.text = '2014'
    programme.append(date)

    # create XML - Category
    category = etree.Element('category')
    category.attrib['lang'] = 'pt'
    category.text = 'Fake'
    programme.append(category)

    # create XML - Country
    country = etree.Element('country')
    country.text = 'Brasil'
    programme.append(country)

    # create XML - Video
    video = etree.Element('video')
    colour = etree.Element('colour')
    colour.text = 'yes'
    video.append(colour)
    programme.append(video)

    # create XML - Rating
    rating = etree.Element('rating')
    rating.attrib['system'] = 'Advisory'
    value = etree.Element('value')
    value.text = rate
    rating.append(value)
    programme.append(rating)
    return programme


def main(argv):
    time_zone = '-0300'
    current_date = datetime.now()
    programme_interval = 60
    guide_days = 30
    guide_offset = (guide_days / 2) * 24
    initial_time = current_date - timedelta(hours=guide_offset)
    final_time = current_date + timedelta(hours=guide_offset)
    rate = '0'
    channel = []

    try:
        opts, args = getopt.getopt(argv, "hc:i:r:f:")
    except getopt.GetoptError:
        print 'fake_guide.py -c "channel;interval" -r <rating do programa> or -f <lista de canais em arquivo>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'fake_guide.py -c "channel;interval" -r <rating do programa> or -f <lista de canais em arquivo>'
            sys.exit()
        elif opt in ("-c"):
            splited_line = arg.split(';')
            elem = (splited_line[0].replace('\n', '').replace('\r', ''), int(splited_line[1].replace('\n', '').replace('\r', '')))
            channel.append(elem)
        elif opt in ("-f"):
            try:
                channel = []
                fp = open(arg, 'r')
                for line in fp:
                    splited_line = line.split(';')
                    elem = (splited_line[0].replace('\n', '').replace('\r', ''), int(splited_line[1].replace('\n', '').replace('\r', '')))
                    channel.append(elem)
            except ValueError:
                print 'arquivo invalido'
                sys.exit()
        elif opt in ("-r"):
            rate = arg
    # create XML - TV
    tv = etree.Element('tv')
    tv.attrib['generator-info-name'] = 'CIANET'
    tv.attrib['generator-info-url'] = 'www.cianet.ind.br'
    for ch in channel:
        initial_aux = initial_time
        programme_interval = ch[1]
        while (initial_aux < final_time):
            start = initial_aux
            stop = initial_aux + timedelta(minutes=programme_interval)
            initial_aux = stop
            tv.append(programmeXML(start.strftime("%Y%m%d%H%M%S") + ' ' + time_zone,
                                   stop.strftime("%Y%m%d%H%M%S") + ' ' + time_zone,
                                   ch[0], rate))

    # pretty string
    xml_guide = etree.tostring(tv, pretty_print=True, xml_declaration=True, encoding='iso-8859-1')

    # Save to XML file
    fakexml = open('fake_guide.xml', 'w')
    fakexml.write(xml_guide)

if __name__ == "__main__":
    main(sys.argv[1:])
