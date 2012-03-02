#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""Visualização e entrega de json para SetupBox"""

from __future__       import print_function
import sys

from django.http      import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template  import RequestContext

from canal.models     import Canal

from django.conf      import settings
from django.core      import serializers

def index(request):
    """
    Imprime informações no console e exibe requsição do box pro setupbox
    """
    #print(request.COOKIES)
    #print(dir(request.META))
    #print(' | '.join(request.META))
    #print('---->IP:',request.META['REMOTE_ADDR'],end='|',sep='=')
    stress = request.GET.get('stress')
    #print('IP=%s'%request.META['REMOTE_ADDR'])
    #print('IP: %s %s' %(request.REMOTE_ADDR,request.REMOTE_HOST))
    #return render_to_response(
    #                          'box/index.html',
    #                          { 'stress':stress },
    #                          context_instance=RequestContext(request)
    #                          )
    return HttpResponseRedirect('%sfrontend/'%settings.MEDIA_URL)

def setup(request):
    """Ambiente base de setup"""
    return render_to_response(
                              'box/setup.html',
                              {},
                              context_instance=RequestContext(request)
                              )


def auth(request, mac = None):
    """Realiza a autenticação do setupbox atravéz de seu endereço MAC"""
    #print('MAC=%s'%mac)
    return HttpResponse('{"MAC":"%s"}'%mac)

def remote_log(request):
    """
    Exibe log no console
    """
    #print(dir(request))
    #print('----->ERROR IP: %s' %request.META.get('REMOTE_ADDR'))
    #print('message',request.POST.get('body'))
    #print('stack',request.POST.get('stack'))
    return HttpResponse('{"success":"true"}')

def canal_list(request):
    """
    Usado pelo setupbox para pegar a lista de canais
    """
    canais = Canal.objects.all().order_by('numero')
    # Chama o canal e pega a listagem do aplicativo canal
    json = serializers.serialize('json', canais, indent=2, use_natural_keys = True)
    return HttpResponse(json)

def programme_info(request):
    """
    Usado pelo setupbox para pegar o programa que esta acontecendo
    """
    import datetime
    from epg.models import Guide
    from django.utils import simplejson
    
    #data-Hora padrao do sistema: 20120117100000 (2012-01-17 10:00:00)
    #Seta uma data passada por GET
    if request.GET.get('now') and len(request.GET.get('now')) == 14:
        nowStr = request.GET.get('now') 
        yyyy = int(nowStr[0:4])
        mm   = int(nowStr[4:6])
        dd   = int(nowStr[6:8])
        hh   = int(nowStr[8:10])
        mi   = int(nowStr[10:12])
        ss   = int(nowStr[12:14])
        now = datetime.datetime(yyyy, mm, dd, hh, mi, ss)
        #now = datetime.datetime(2012, 1, 17, 10, 00, 00)
    else:
        now = datetime.datetime.now()
    
    channel_id = request.GET.get('channel_id')
    
    guides = Guide.objects.filter(channel=channel_id,start__lte=now,stop__gt=now).order_by('start')
    
    if len(guides) > 0:
        guide = guides[0]
        pro = guide.programme
        
        programid = int( pro.programid )
        
        #Inicio / Fim
        startStr = '{:%H:%M}'.format(guide.start)
        stopStr  =  '{:%H:%M}'.format(guide.stop)
        
        #Titulos
        titlesStr = ""
        titles = pro.titles.all().values()
        for title in titles:
            titlesStr += title['value'] + " - "
        titlesStr = titlesStr[0:-3]
        titlesStr = titlesStr.upper()
        
        #Segundo titulos
        secondaryTitlesStr = ""
        secondaryTitles = pro.secondary_titles.all().values()
        for secondary_title in secondaryTitles:
            secondaryTitlesStr += secondary_title['value'] + " - "
        
        secondaryTitlesStr = secondaryTitlesStr[0:-3]
        rating = pro.rating.system + ':' + pro.rating.value
        
        #Descricao
        descriptions = ""
        descriptions = pro.descriptions.get().value
        
        json = simplejson.dumps( [{ 
                                   'programid'       :programid,
                                   'rating'          :[rating],
                                   'start'           :[startStr],
                                   'stop'            :[stopStr],
                                   'titles'          :[titlesStr],
                                   'secondary_titles':[secondaryTitlesStr],
                                   'descriptions'    :[descriptions],
                                   'actors'          :[],
                                   'length'          :[],
                                   'adapters'        :[],
                                   'audio_present'   :[],
                                   'audio_stereo'    :[],
                                   'categories'      :[],
                                   'commentators'    :[],
                                   'composers'       :[],
                                   'country'         :[],
                                   'date'            :[],
                                   'directors'       :[],
                                   'editors'         :[],
                                   'episode_numbers' :[],
                                   'guests'          :[],
                                   'length'          :[],
                                   'presenters'      :[],
                                   'producers'       :[],
                                   'subtitles'       :[],
                                   'video_aspect'    :[],
                                   'video_colour'    :[],
                                   'video_present'   :[],
                                   'video_quality'   :[],
                                   'writers'         :[]
                                   }])
        
    else:
        print('SEM PROGRAMACAO')
        json = simplejson.dumps([])
        
    # Chama o canal e pega a listagem do aplicativo canal
    return HttpResponse(json)

def guide_programmes(request):
    """
    Usado pelo setupbox para pegar o programa que esta acontecendo
    """
    import datetime
    from datetime import timedelta
    from epg.models import Guide
    from django.utils import simplejson
    
    
    
    #data-Hora padrao do sistema: 20120117100000 (2012-01-17 10:00:00)
    #Seta uma data passada por GET
    if request.GET.get('now') and len(request.GET.get('now')) == 14:
        nowStr = request.GET.get('now') 
        yyyy = int(nowStr[0:4])
        mm   = int(nowStr[4:6])
        dd   = int(nowStr[6:8])
        hh   = int(nowStr[8:10])
        mi   = int(nowStr[10:12])
        ss   = int(nowStr[12:14])
        now = datetime.datetime(yyyy, mm, dd, hh, mi, ss)
        
        rangeTimeStart = now-timedelta(hours=3)
        rangeTimeStop = now+timedelta(hours=12)
        
        print('--------------')
        print(rangeTimeStart)
        print(rangeTimeStop)
        print('--------------')
        
        #now = datetime.datetime(2012, 1, 17, 10, 00, 00)
    else:
        now = datetime.datetime.now()
        
        rangeTimeStart=now-timedelta(hours=3)
        rangeTimeStop=now+timedelta(hours=12)
    
    channel_id = request.GET.get('channel_id')
    
    #BUSCAR OS CANAIS LISTADOS NA TELA
    
    guides = Guide.objects.filter(channel=channel_id,start__gte=rangeTimeStart,stop__lte=rangeTimeStop).order_by('start')
    
    print(len(guides))
    
    if len(guides) > 0:
        
        arr = []
        for guide in guides:
            pro = guide.programme
            
            programid = int( pro.programid )
            
            #Inicio / Fim
            startStr = '{:%H:%M}'.format(guide.start)
            stopStr  =  '{:%H:%M}'.format(guide.stop)
            
            duracao = guide.stop-guide.start
            
            #Titulos
            titlesStr = ""
            
            titles = pro.titles.all().values()
            for title in titles:
                titlesStr += title['value'] + " - "
            titlesStr = titlesStr[0:-3]
            titlesStr = titlesStr.upper()
            
            #Segundo titulos
            secondaryTitlesStr = ""
            secondaryTitles = pro.secondary_titles.all().values()
            for secondary_title in secondaryTitles:
                secondaryTitlesStr += secondary_title['value'] + " - "
            
            secondaryTitlesStr = secondaryTitlesStr[0:-3]
             
            rating = pro.rating.system + ':' + pro.rating.value
            
            #Descricao
            descriptions = ""
            if(pro.descriptions.get().value):
                descriptions = pro.descriptions.get().value
                
            arr.append({
                        'programid':programid,
                        'duracao':int(duracao.total_seconds()),
                        'start':startStr,
                        'stop':stopStr,
                        'titles':titlesStr,
                        'secondary_titles':secondaryTitlesStr,
                        'descriptions':descriptions,
                        'rating':rating
                        })
        
        json = simplejson.dumps(arr)
    else:
        print('SEM PROGRAMACAO')
        json = simplejson.dumps([])
        
    # Chama o canal e pega a listagem do aplicativo canal
    return HttpResponse(json)

def canal_update(request):
    """Retorna a data de atualização mais recente da lista de canais"""
    #print('---->IP:',request.META['REMOTE_ADDR'],end=' ')
    #sys.stdout.flush()
    #print('META',' | '.join(request.META))
    atual = Canal.objects.all().order_by('-atualizado')[0]
    #return HttpResponse('{"atualizado":"%s"}'%(atual.atualizado.strftime('%Y-%m-%dT%H:%M:%S')))
    #return HttpResponse('{"atualizado":"%s"}'%(atual.atualizado.isoformat()))
    return HttpResponse('{"atualizado":"%s"}'%(atual.atualizado.ctime()))

def ping(request):
    """ Responde true """
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
    #return HttpResponse() # Remova o comentário para emular servidor sem conexão
    return response






