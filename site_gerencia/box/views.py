#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""Visualização e entrega de json para SetupBox"""

from __future__       import print_function

from django.http      import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template  import RequestContext

from tv.models        import Channel

from django.conf      import settings
from django.core      import serializers

#usado para converter strings
from django.utils.encoding import smart_str, smart_unicode

def jsonp(json, request):
    if request.GET.get('format') == 'jsonp' and request.GET.get('callback') == None:
        json = 'callback('+json+')'
    if request.GET.get('callback') != None:
        json = request.GET.get('callback')+'('+json+')'
    return json


def index(request):
    """
    Imprime informações no console e exibe requsição do box pro setupbox
    """
    return HttpResponseRedirect('%sfrontend/' % settings.MEDIA_URL)


def setup(request):
    """Ambiente base de setup"""
    return render_to_response(
        'box/setup.html',
        {},
        context_instance=RequestContext(request)
        )


def auth(request, mac=None):
    """Realiza a autenticação do setupbox atravéz de seu endereço MAC"""
    return HttpResponse('{"MAC":"%s"}' % mac)


def remote_log(request):
    """
    Exibe log no console
    """
    return HttpResponse('{"success":"true"}')


def canal_list(request):
    """
    Usado pelo setupbox para pegar a lista de canais
    """
    channels = Channel.objects.filter(enabled=True).order_by('number')
    json = serializers.serialize('json', channels, indent=2,
        use_natural_keys=True)
    return HttpResponse(json, content_type='application/json')


def programme_info(request):
    """
    Usado pelo setupbox para pegar o programa que esta acontecendo
    """
    import datetime
    # TODO: Utilizar timezone
    from django.utils import timezone
    from epg.models import Guide
    from django.utils import simplejson
    from django.utils.timezone import utc
    import time
    
    
    #data-Hora padrao do sistema: 20120117100000 (2012-01-17 10:00:00)
    #Seta uma data passada por GET
    if request.GET.get('now') and len(request.GET.get('now')) >= 14:
        nowStr = request.GET.get('now')
        yyyy = int(nowStr[0:4])
        mm = int(nowStr[4:6])
        dd = int(nowStr[6:8])
        hh = int(nowStr[8:10])
        mi = int(nowStr[10:12])
        ss = int(nowStr[12:14])
        now = datetime.datetime(yyyy, mm, dd, hh, mi, ss)
        #now = datetime.datetime(2012, 1, 17, 10, 00, 00)
    else:
        now = timezone.now()
        
    channel_id = request.GET.get('channel_id')
    guides = Guide.objects.filter(channel__channelid=channel_id,
        start__lte=now, stop__gt=now)
    arr = []

    if len(guides) > 0:
        guide = guides[0]
        pro = guide.programme
        programid = int(guide.programme_id)
        #Inicio / Fim
        startStr = int(time.mktime(guide.start.timetuple()))
        stopStr  = int(time.mktime(guide.stop.timetuple()))
        
        #Titulos
        titlesStr = ""
        titles = pro.titles.all().values()
        for title in titles:
            titlesStr += smart_str(title['value']) + " - "
        titlesStr = titlesStr[0:-3]
        titlesStr = smart_unicode(titlesStr).upper()
        #Segundo titulos
        secondaryTitlesStr = ""
        secondaryTitles = pro.secondary_titles.all().values()
        for secondary_title in secondaryTitles:
            secondaryTitlesStr += smart_str(secondary_title['value']) + " - "
        secondaryTitlesStr = secondaryTitlesStr[0:-3]
        rating = smart_str(pro.rating.value)
        #Descricao
        descriptions = ""
        descriptions = smart_str(pro.descriptions.get().value)

        arr = {
            'programid':        programid,
            'rating':           [rating],
            'start':            [startStr],
            'stop':             [stopStr],
            'titles':           [titlesStr],
            'secondary_titles': [secondaryTitlesStr],
            'descriptions':     [descriptions]
        }
    else:
        print('SEM PROGRAMACAO')
        arr = {
            'programid':        0,
            'rating':           [" "],
            'start':            [0],
            'stop':             [0],
            'titles':           ["Sem programação"],
            'secondary_titles': [" "],
            'descriptions':     ["Programação indisponível"]
        }

    arrMeta = {
        'meta': {
            "limit": 0,
            "next": "",
            "offset": 0,
            "previous": '',
            "total_count": 0
        },
        "objects": [arr]
    }

    json = simplejson.dumps(arrMeta)
    json = jsonp(json, request)
    # Chama o canal e pega a listagem do aplicativo canal
    return HttpResponse(json, content_type='application/json')


def guide_programmes(request):
    """
    Usado pelo setupbox para pegar o programa que esta acontecendo
    """
    import datetime
    from datetime import timedelta
    from epg.models import Guide
    from django.utils import simplejson
    from django.utils import timezone
    #data-Hora padrao do sistema: 20120117100000 (2012-01-17 10:00:00)
    #Seta uma data passada por GET
    if request.GET.get('now') and len(request.GET.get('now')) == 14:
        nowStr = request.GET.get('now')
        yyyy = int(nowStr[0:4])
        mm = int(nowStr[4:6])
        dd = int(nowStr[6:8])
        hh = int(nowStr[8:10])
        mi = int(nowStr[10:12])
        ss = int(nowStr[12:14])
        now = datetime.datetime(yyyy, mm, dd, hh, mi, ss)
        #now = datetime.datetime(2012, 1, 17, 10, 00, 00)
    else:
        now = timezone.now()

    rangeTimeStart = now - timedelta(hours=12)
    rangeTimeStop = now + timedelta(hours=12)
    channel_id = request.GET.get('channel_id')
    #BUSCAR OS CANAIS LISTADOS NA TELA
    guides = Guide.objects.filter(channel__channelid=channel_id,
        start__gte=rangeTimeStart, stop__lte=rangeTimeStop)
    if len(guides) > 0:
        arr = []
        for guide in guides:
            pro = guide.programme
            programid = int(guide.programme_id)
            #Inicio / Fim
            start_yyymmddhhmm = '{:%Y%m%d%H%M}'.format(guide.start)
            startStr = '{:%H:%M}'.format(guide.start)
            stopStr = '{:%H:%M}'.format(guide.stop)
            duracao = guide.stop - guide.start
            #Titulos
            titlesStr = ""
            titles = pro.titles.all().values()
            for title in titles:
                titlesStr += smart_str(title['value']) + " - "
            titlesStr = titlesStr[0:-3]
            titlesStr = smart_unicode(titlesStr).upper()
            #Segundo titulos
            secondaryTitlesStr = ""
            secondaryTitles = pro.secondary_titles.all().values()
            for secondary_title in secondaryTitles:
                secondaryTitlesStr += smart_str(secondary_title['value']) +\
                    " - "
            secondaryTitlesStr = secondaryTitlesStr[0:-3]
            rating = pro.rating.value
            #Descricao
            descriptions = ""
            if(smart_str(pro.descriptions.get().value)):
                descriptions = smart_str(pro.descriptions.get().value)
            arr.append({
                'programid': programid,
                'duracao': int(duracao.total_seconds()),
                'start_yyymmddhhmm': start_yyymmddhhmm,
                'start': startStr,
                'stop': stopStr,
                'titles': titlesStr,
                'secondary_titles': secondaryTitlesStr,
                'descriptions': descriptions,
                'rating': rating
                })
    else:
        print('SEM PROGRAMACAO')
        arr = []
        arr.append({
            'programid': 0,
            'duracao': "1",
            'start_yyymmddhhmm': "00000000000000",
            'start': "00:00",
            'stop': "00:00",
            'titles': "Sem programação",
            'secondary_titles': " ",
            'descriptions': "Programação indisponível",
            'rating': ""
            })
    arrMeta = {
      'meta': {
               "limit": 0,
               "next": "",
               "offset": 0,
               "previous": '',
               "total_count": 0
        },
      "objects": arr
    }
    json = simplejson.dumps(arrMeta)
    json = jsonp(json, request)
    # Chama o canal e pega a listagem do aplicativo canal
    return HttpResponse(json, content_type='application/json')

def guide_mount_line_of_programe(request):
    """
    Usado pelo setupbox para mostrar a guia de programacao completa
    """
    import datetime
    from datetime import timedelta
    from epg.models import Guide
    from django.utils import simplejson
    from django.utils import timezone
    from django.utils.timezone import utc
    import time

    #data-Hora padrao do sistema: 20120117100000 (2012-01-17 10:00:00)
    #Seta uma data passada por GET
    if request.GET.get('now') and len(request.GET.get('now')) >= 14:
        nowStr = request.GET.get('now') 
        yyyy = int(nowStr[0:4])
        mm   = int(nowStr[4:6])
        dd   = int(nowStr[6:8])
        hh   = int(nowStr[8:10])
        mi   = int(nowStr[10:12])
        ss   = int(nowStr[12:14])
        now = datetime.datetime(yyyy, mm, dd, hh, mi, ss).replace(tzinfo=utc)
    else:
        now = timezone.now()

    countX = 0
    
    #buscando um range de tempo para a busca
    hoursRangeStart = request.GET.get('r_start')
    hoursRangeStop = request.GET.get('r_stop')
    #Usado para posicionar o campo dentro da div gerada
    divCodePosition = request.GET.get('dcode')
    if hoursRangeStart > 0 and hoursRangeStop >= hoursRangeStart:
        print("RANGE PESONALIZADO")
        rangeTimeStart = now - timedelta(hours=int(hoursRangeStart))
        rangeTimeStop = now + timedelta(hours=int(hoursRangeStop))
    else:
        print("RANGE PADRAO: 3 a 12")
        rangeTimeStart = now - timedelta(hours=3)
        rangeTimeStop = now + timedelta(hours=12)

    #canal
    channelEpgRunNow = request.GET.get('c')
    #canal Number
    channelNumber = request.GET.get('ch')
    #Y na lista de canais
    countY = int(request.GET.get('y'))
    guides = Guide.objects.filter(channel__channelid=channelEpgRunNow,
        start__gte=rangeTimeStart, stop__lte=rangeTimeStop).order_by('start')
    arrGuideLine = []
    if(len(guides) > 0):
        countX = 0
        for guide in guides:
            pro = guide.programme
            programid = int(guide.programme_id)
            duracao = guide.stop - guide.start
            start_yyymmddhhmm = '{:%Y%m%d%H%M}'.format(guide.start)
            start_tm   = int(time.mktime(guide.start.timetuple()))
            
            startStr = '{:%H:%M}'.format(guide.start)
            stopStr  =  '{:%H:%M}'.format(guide.stop)
            
            stop_tm   = int(time.mktime(guide.stop.timetuple()))
            
            is_run_now_programme = 0
            if(guide.start <= now and now <= guide.stop):
                is_run_now_programme = 1
            #Titulos
            titlesStr = ""
            titles = pro.titles.all().values()
            titlesStr = smart_unicode(titles[0]['value']).upper()
            arrGuideLine.append({
                'ch':channelNumber,
                'c':channelEpgRunNow,
                'p':programid,
                'rn':is_run_now_programme,
                'sf':start_yyymmddhhmm,
                'sf_tm':start_tm,
                'st':startStr,
                'st_tm':start_tm,
                'sp':stopStr,
                'sp_tm':stop_tm,
                't':titlesStr,
                'dcode':divCodePosition,
                'd': int((int(duracao.total_seconds()) / 60 )),
                'x':countX,
                'y':countY
                })
            countX += 1
    else:
        print("SEM PROGRAMACAO")
        tTotalStart = int(hoursRangeStart)
        tTotalStop = int(hoursRangeStop)
        tTotal = tTotalStart + tTotalStop
        countHours = 0
        staTime = rangeTimeStart
        stoTime = rangeTimeStart + timedelta(hours=1)
        
        start_tm   = int(time.mktime(staTime.timetuple()))
        stop_tm   = int(time.mktime(stoTime.timetuple()))
        
        while countHours < tTotal:
            arrGuideLine.append({
                    'ch': channelNumber,
                    'c': channelEpgRunNow,
                    'p': '-1',
                    'rn': 0,
                    'sf': '{:%Y%m%d%H%M}'.format(staTime),
                    'sf_tm':start_tm,
                    'st': '{:%H:%M}'.format(staTime),
                    'st_tm':start_tm,
                    'sp': '{:%H:%M}'.format(stoTime),
                    'sp_tm':stop_tm,
                    't': '',
                    'dcode': divCodePosition,
                    'd': 60,
                    'x': countHours,
                    'y': countY
                    })
            countHours += 1
            staTime = staTime + timedelta(hours=1)
            stoTime = staTime + timedelta(hours=1)
            
            start_tm   = int(time.mktime(staTime.timetuple()))
            stop_tm   = int(time.mktime(stoTime.timetuple()))

    arrGuideLineMeta = {
      'meta': {
               "limit": 0,
               "next": "",
               "offset": 0,
               "previous": '',
               "total_count": countX
        },
      "objects": arrGuideLine
     }

    json = simplejson.dumps(arrGuideLineMeta)
    json = jsonp(json, request)
    # Chama o canal e pega a listagem do aplicativo canal
    return HttpResponse(json, content_type='application/json')


def ping(request):
    """ Responde true """
    if settings.DEBUG == True:
        print('--> Ping from %s' % (request.META['REMOTE_ADDR']))
    try:
        import Image
    except:
        try:
            from PIL import Image
        except:
            pass
    image = Image.new("RGB", (1, 1), "black")
    response = HttpResponse(mimetype='image/png')
    image.save(response, "PNG")
    return response
