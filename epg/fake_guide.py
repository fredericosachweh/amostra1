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
    now = datetime.now()
    current_date = datetime(now.year, now.month, now.day,
                            now.hour, 0, 0, 0)
    programme_interval = 60
    guide_days = 30
    guide_offset = (guide_days / 2) * 24
    initial_time = current_date - timedelta(hours=guide_offset)
    final_time = current_date + timedelta(hours=guide_offset)
    rate = '0'
    channel = []

    try:
        opts, args = getopt.getopt(argv, "hc:r:f:p:")
    except getopt.GetoptError:
        print 'fake_guide.py -c "channel;interval;rating,channel2;interval2;rating2" or -f <lista de canais em arquivo> or -p <canal para teste parental>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'fake_guide.py -c "channel;interval;rating,channel2;interval2;rating2" or -f <lista de canais em arquivo> or -p <canal para teste parental>'
            sys.exit()
        elif opt in ("-c"):
            tmp = []
            tmp = arg.split(',')
            for t in tmp:
                splited_line = t.split(';')
                elem = (splited_line[0].replace('\n', '').replace('\r', ''), int(splited_line[1].replace('\n', '').replace('\r', '')), splited_line[2].replace('\n', '').replace('\r', ''))
                channel.append(elem)
        elif opt in ("-f"):
            try:
                channel = []
                fp = open(arg, 'r')
                for line in fp:
                    splited_line = line.split(';')
                    if len(splited_line) == 3:
                        elem = (splited_line[0].replace('\n', '').replace('\r', ''), int(splited_line[1].replace('\n', '').replace('\r', '')), splited_line[2].replace('\n', '').replace('\r', ''))
                        channel.append(elem)
            except ValueError:
                print 'arquivo invalido'
                sys.exit()
        elif opt in ("-p"):
            try:
                parental_list = []
                parental_list.append('0')
                parental_list.append('10')
                parental_list.append('12')
                parental_list.append('16')
                parental_list.append('18')
                head = '<?xml version=\'1.0\' encoding=\'iso-8859-1\'?>\n'
                head += '<tv generator-info-name="CIANET" generator-info-url="www.cianet.ind.br">'
                fakexml = open('fake_guide.xml', 'w')
                fakexml.write(head)
                elem = (arg, 5)
                channel.append(elem)
                for ch in channel:
                    initial_aux = initial_time
                    programme_interval = ch[1]
                    parental_index = 0
                    while (initial_aux < final_time):
                        start = initial_aux
                        stop = initial_aux + timedelta(minutes=programme_interval)
                        initial_aux = stop
                        programme = programmeXML(start.strftime("%Y%m%d%H%M%S") + ' ' + time_zone,
                                   stop.strftime("%Y%m%d%H%M%S") + ' ' + time_zone,
                                   ch[0], parental_list[parental_index])
                        prog = etree.tostring(programme, pretty_print=True, xml_declaration=False)
                        fakexml.write(prog)
                        fakexml.flush()
                        if parental_index > 3:
                            parental_index = 0
                        else:
                            parental_index += 1
                foot = '</tv>'
                fakexml.write(foot)
                fakexml.close()
                sys.exit()
            except ValueError:
                print 'arquivo invalido'
                sys.exit()
        elif opt in ("-r"):
            rate = arg
    # create XML - TV
    head = '<?xml version=\'1.0\' encoding=\'iso-8859-1\'?>\n'
    head += '<tv generator-info-name="CIANET" generator-info-url="www.cianet.ind.br">'
    fakexml = open('fake_guide.xml', 'w')
    fakexml.write(head)
    for ch in channel:
        initial_aux = initial_time
        programme_interval = ch[1]
        while (initial_aux < final_time):
            start = initial_aux
            stop = initial_aux + timedelta(minutes=programme_interval)
            initial_aux = stop
            programme = programmeXML(start.strftime("%Y%m%d%H%M%S") + ' ' + time_zone,
                                   stop.strftime("%Y%m%d%H%M%S") + ' ' + time_zone,
                                   ch[0], ch[2])
            prog = etree.tostring(programme, pretty_print=True, xml_declaration=False)
            fakexml.write(prog)
            fakexml.flush()
    foot = '</tv>'
    # Save to XML file
    fakexml.write(foot)
    fakexml.close()

if __name__ == "__main__":
    main(sys.argv[1:])
