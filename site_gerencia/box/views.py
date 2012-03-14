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
    # .select_related('source')
    canais = Canal.objects.filter(enabled=True).order_by('numero')
    json = serializers.serialize('json', canais, indent=2,use_natural_keys=True)
    return HttpResponse(json,content_type='application/json')

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
        
        programid = int( guide.programme_id )
        
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
        json = simplejson.dumps( [{ 
                                   'programid'       :0,
                                   'rating'          :[" "],
                                   'start'           :["00:00"],
                                   'stop'            :["00:00"],
                                   'titles'          :["Sem programação"],
                                   'secondary_titles':[" "],
                                   'descriptions'    :["Programação indisponível"],
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
        
    # Chama o canal e pega a listagem do aplicativo canal
    return HttpResponse(json,content_type='application/json')

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
        
        #now = datetime.datetime(2012, 1, 17, 10, 00, 00)
    else:
        now = datetime.datetime.now()
        
    rangeTimeStart=now-timedelta(hours=12)
    rangeTimeStop=now+timedelta(hours=12)
    
    channel_id = request.GET.get('channel_id')
    
    #BUSCAR OS CANAIS LISTADOS NA TELA
    
    guides = Guide.objects.filter(channel=channel_id,start__gte=rangeTimeStart,stop__lte=rangeTimeStop).order_by('start')
    
    if len(guides) > 0:
        
        arr = []
        for guide in guides:
            pro = guide.programme
            
            programid = int( pro.programid )
            
            #Inicio / Fim
            start_yyymmddhhmm = '{:%Y%m%d%H%M}'.format(guide.start)
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
                        'start_yyymmddhhmm':start_yyymmddhhmm,
                        'start':startStr,
                        'stop':stopStr,
                        'titles':titlesStr,
                        'secondary_titles':secondaryTitlesStr,
                        'descriptions':descriptions,
                        'rating':rating
                        })
        
    else:
        print('SEM PROGRAMACAO')
        arr = []
        arr.append({
            'programid':0,
            'duracao':"1",
            'start_yyymmddhhmm':"00000000000000",
            'start':"00:00",
            'stop':"00:00",
            'titles':"Sem programação",
            'secondary_titles':" ",
            'descriptions':"Programação indisponível",
            'rating':""
            })
        
    json = simplejson.dumps(arr)
        
    # Chama o canal e pega a listagem do aplicativo canal
    return HttpResponse(json,content_type='application/json')


def guide_programmes_list(request):
    """
    Usado pelo setupbox para mostrar a guia de programacao completa
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
        
        #now = datetime.datetime(2012, 1, 17, 10, 00, 00)
    else:
        now = datetime.datetime.now()

    hoursRangeStart = request.GET.get('r_start')
    hoursRangeStop = request.GET.get('r_stop')
    
    if hoursRangeStart > 1 and hoursRangeStop > hoursRangeStart:
        rangeTimeStart = now-timedelta(hours=int(hoursRangeStart) )
        rangeTimeStop  = now+timedelta(hours=int(hoursRangeStop))
    else:
        rangeTimeStart = now-timedelta(hours=3)
        rangeTimeStop  = now+timedelta(hours=12)

    channelEpgRunNow = request.GET.get('c')
    programmeIdRunNow = int( request.GET.get('p') )
    
    channelList = request.GET.get('channel_list')[0:-1].split(',')
    
    if len(channelList) > 0 and channelEpgRunNow > 0 and programmeIdRunNow > 0: 
    
        #Canal atual
        arrGuide = []
        for id in channelList:
            #BUSCAR OS CANAIS LISTADOS NA TELA
            guides = Guide.objects.filter(channel=id,start__gte=rangeTimeStart,stop__lte=rangeTimeStop).distinct('start')
            
            arrProgramme = []
            for guide in guides:
                pro = guide.programme
                
                programid = int( pro.programid )
                
                #Inicio / Fim
                start_yyymmddhhmm = '{:%Y%m%d%H%M}'.format(guide.start)
                startStr = '{:%H:%M}'.format(guide.start)
                stopStr  =  '{:%H:%M}'.format(guide.stop)
                
                #Verifica se o programa que esta sendo exibido no canal está dentro de horario. 
                #Utilizado para programas que repetem ao longo do dia.
                is_run_now_programme = 0
                if( ( programmeIdRunNow == programid ) and ( guide.start <= now and now <= guide.stop ) ):
                    is_run_now_programme = 1
                
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
               
                arrProgramme.append({
                        'pid':programid,
                        'pnow':is_run_now_programme,
                        'dur': int((int(duracao.total_seconds()) / 60 )),
                        'sfo':start_yyymmddhhmm,
                        'start':startStr,
                        'stop':stopStr,
                        'titles':titlesStr,
                        'st':secondaryTitlesStr,
                        'desc':descriptions,
                        'rat':rating
                    })
                    
            is_run_now_channel = 0
            if( channelEpgRunNow == id ):
                is_run_now_channel = 1
                    
            arrGuide.append({
                'n':guides[0].channel.display_names.get().value,
                'epg':id,
                'enow':is_run_now_channel,
                'program':arrProgramme
                })
        
    else:
        print('SEM PROGRAMACAO')
        arrGuide = []
        arrProgramme = []
        arrProgramme.append({
                'pid':0,
                'pnow':0,
                'dur': 0,
                'sfo':"00000000000000",
                'start':"00:00",
                'stop':"00:00",
                'titles':"Sem programação",
                'st':" ",
                'desc':"Programação insdisponível",
                'rat':" "
            })

        arrGuide.append({
            'n':"Indisponível",
            'epg':"0",
            'enow':"0",
            'program':arrProgramme
            })

    json = simplejson.dumps(arrGuide)
        
    # Chama o canal e pega a listagem do aplicativo canal
    return HttpResponse(json,content_type='application/json')



def channel_programme_info(request):
    """
    Usado pelo setupbox para mostrar a INFO do programa
    """
    from epg.models import Guide
    from django.utils import simplejson
    
    RunNowChannelEpg = int( request.GET.get('c') )
    RunNowProgrammeId = int( request.GET.get('p') )

    if(RunNowChannelEpg and RunNowProgrammeId):
        guides = Guide.objects.filter(channel=RunNowChannelEpg,programme=RunNowProgrammeId)
        if len(guides) > 0:
            guide = guides[0]
                    
            cha   = guide.channel
            pro   = guide.programme
            start = guide.start
            stop  = guide.stop
            
            #Titles
            titlesStr = ""
            titles = pro.titles.all().values()
            for title in titles:
                titlesStr += title['value'] + " - "
            titlesStr = titlesStr[0:-3]
            
            #Segundo titulos
            secondaryTitlesStr = ""
            secondaryTitles = pro.secondary_titles.all().values()
            for secondary_title in secondaryTitles:
                secondaryTitlesStr += secondary_title['value'] + " - "
            secondaryTitlesStr = secondaryTitlesStr[0:-3]
            
            #Actors
            actorsStr = ""
            actors = pro.actors.all().values()
            for actor in actors:
                actorsStr += actor['name'] + ", "
            actorsStr = actorsStr[0:-2]
    
            #Categoria
            categoriesStr = ""
            categories = pro.categories.all().values()
            for categorie in categories:
                categoriesStr += categorie['value'] + ", "
            categoriesStr = categoriesStr[0:-2]

            #Diretores
            directorsStr = ""
            directors = pro.directors.all().values()
            for director in directors:
                directorsStr += director['name'] + ", "
            directorsStr = directorsStr[0:-2]
            
            ratingStr = ""
            if(pro.rating):
                ratingStr = pro.rating.system + ':' + pro.rating.value
                
            descriptionsStr = ""
            if(pro.descriptions.get()):
                descriptionsStr = pro.descriptions.get().value

            countryStr = ""
            if(pro.country):
                countryStr = pro.country.value
            
            
            audio_stereoStr = ""
            if(pro.audio_stereo):
                audio_stereoStr = pro.audio_stereo

            lengthStr = ""
            if(pro.length):
                lengthStr = pro.length

            dateStr = ""
            if(pro.date):
                dateStr = pro.date

            video_aspectStr = ""
            if(pro.video_aspect):
                video_aspectStr = pro.video_aspect

            video_colourStr = ""
            if(pro.video_colour):
                video_colourStr = pro.video_colour

            video_presentStr = ""
            if(pro.video_present):
                video_presentStr = pro.video_present

            video_qualityStr = ""
            if(pro.video_quality):
                video_qualityStr = pro.video_quality

            audio_presentStr = ""
            if(pro.audio_present):
                audio_presentStr = pro.audio_present
            
            arrChannel = {
                'channelepg'   :RunNowChannelEpg,
                'channelid'    :cha.channelid,
                'display_names':cha.display_names.get().value,
                'icons'        :cha.icons.all().values('src')[0].get('src')
            }
            
            arrProgramme = {
                'id'              :int( RunNowProgrammeId ),
                'programid'       :int( pro.programid ),
                'rating'          :( ratingStr.strip() or "Indisponível"),
                'titles'          :( titlesStr.strip() or "Indisponível"),
                'secondary_titles':( secondaryTitlesStr.strip() or "Indisponível"),
                'descriptions'    :( descriptionsStr.strip() or "Indisponível"),
                'actors'          :( actorsStr.strip() or "Indisponível"),                
                'categories'      :( categoriesStr.strip() or "Indisponível"),
                'directors'       :( directorsStr.strip() or "Indisponível"),
                'country'         :( countryStr.strip() or "Indisponível"),
                'length'          :( lengthStr.strip() or "Indisponível"),
                'date'            :( dateStr.strip() or "Indisponível"),
                'video_aspect'    :( video_aspectStr.strip() or "Indisponível"),
                'video_colour'    :( video_colourStr.strip() or "Indisponível"),
                'video_present'   :( video_presentStr.strip() or "Indisponível"),
                'video_quality'   :( video_qualityStr.strip() or "Indisponível"),
                'audio_present'   :( audio_presentStr.strip() or "Indisponível"),
                'audio_stereo'    :( audio_stereoStr.strip() or "Indisponível")
            }
            
            arr = {
               'start':'{:%H:%M}'.format(start),
               'stop':'{:%H:%M}'.format(stop),
               'channel':arrChannel,
               'programme':arrProgramme
            }
            
        else:
            arrChannel = {
                'channelepg'   :RunNowChannelEpg,
                'channelid'    :0,
                'display_names':"Indisponível.",
                'icons'        :""
            }
            
            arrProgramme = {
                'id'              :int( RunNowProgrammeId ),
                'programid'       :"Indisponível.",
                'rating'          :"Indisponível.",
                'titles'          :"Indisponível.",
                'secondary_titles':"Indisponível.",
                'descriptions'    :"Indisponível.",
                'actors'          :"Indisponível.",              
                'categories'      :"Indisponível.",
                'directors'       :"Indisponível.",
                'country'         :"Indisponível.",
                'length'          :"Indisponível.",
                'date'            :"Indisponível.",
                'video_aspect'    :"Indisponível.",
                'video_colour'    :"Indisponível.",
                'video_present'   :"Indisponível.",
                'video_quality'   :"Indisponível.",
                'audio_present'   :"Indisponível.",
                'audio_stereo'    :"Indisponível."
            }
            
            arr = {
               'start':"00:00",
               'stop':"00:00",
               'channel':arrChannel,
               'programme':arrProgramme
            }
    else:
        print("INEXISTENTE")
            
    json = simplejson.dumps(arr)
    
    # Chama o canal e pega a listagem do aplicativo canal
    return HttpResponse(json,content_type='application/json')



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






