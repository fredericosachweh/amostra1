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
    programme.attrib['channel'] = channel

    # create XML - Title
    title_pt = etree.Element('title')
    title_pt.attrib['lang'] = 'pt'
    title_pt.text = channel
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
    programme_interval = 1
    guide_days = 14
    guide_offset = (guide_days / 2) * 24
    initial_time = current_date - timedelta(hours=guide_offset)
    final_time = current_date + timedelta(hours=guide_offset)
    rate = '0'
    channel = 'CIANET CHANNEL'

    try:
        opts, args = getopt.getopt(argv, "hc:i:r:")
    except getopt.GetoptError:
        print 'fake_guide.py -c <nome do canal> -i <intervalo de cada programa> -r <rating do programa>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'fake_guide.py -c <nome do canal> -i <intervalo de cada programa> -r <rating do programa>'
            sys.exit()
        elif opt in ("-c"):
            channel = arg
        elif opt in ("-i"):
            try:
                programme_interval = int(arg)
            except ValueError:
                print 'interval deve ser um numero'
                sys.exit()
        elif opt in ("-r"):
            rate = arg

    # create XML - TV
    tv = etree.Element('tv')
    tv.attrib['generator-info-name'] = 'CIANET'
    tv.attrib['generator-info-url'] = 'www.cianet.ind.br'

    while (initial_time < final_time):
        start = initial_time
        stop = initial_time + timedelta(hours=programme_interval)
        initial_time = stop
        tv.append(programmeXML(start.strftime("%Y%m%d%H%M%S") + ' ' + time_zone,
                               stop.strftime("%Y%m%d%H%M%S") + ' ' + time_zone,
                               channel, rate))

    # pretty string
    xml_guide = etree.tostring(tv, pretty_print=True, xml_declaration=True, encoding='iso-8859-1')
    
    # Save to XML file
    fakexml = open('fakexml.xml', 'w')
    fakexml.write(xml_guide)

if __name__ == "__main__":
    main(sys.argv[1:])
