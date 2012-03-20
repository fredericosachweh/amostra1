from django.core import serializers
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from models import *

def get_transponders(request):
    if request.method == 'GET':
        base = Transponder.objects
        if request.GET.has_key('fta') and request.GET['fta']:
            base = base.filter(dvbschannel__crypto__iexact='FTA')
        if request.GET.has_key('sat'):
            transponders = base.filter(satellite__id=request.GET['sat'])
            if len(transponders):
                json = serializers.serialize('json',
                    transponders,
                    indent=2,
                    use_natural_keys=True
                    )
                return HttpResponse(json, content_type='application/json')
        elif request.GET.has_key('trans'):
            transponder = base.filter(pk=request.GET['trans'])
            if len(transponder):
                json = serializers.serialize('json',
                    transponder,
                    indent=2,
                    use_natural_keys=True
                    )
                return HttpResponse(json, content_type='application/json')
        elif request.GET.has_key('chan'):
            transponder = base.filter(dvbschannel__id=request.GET['chan'])
            if len(transponder):
                json = serializers.serialize('json',
                    transponder,
                    indent=2,
                    use_natural_keys=True
                    )
                return HttpResponse(json, content_type='application/json')
        else:
            return HttpResponseNotFound()
    return HttpResponseBadRequest()

def get_channels(request):
    if request.method == 'GET':
        base = DvbsChannel.objects
        if request.GET.has_key('fta') and request.GET['fta']:
            base = base.filter(crypto__iexact='FTA')
        if request.GET.has_key('trans'):
            channels = base.filter(transponder__id=request.GET['trans'])
            if len(channels):
                json = serializers.serialize('json',
                    channels,
                    indent=2,
                    use_natural_keys=True
                    )
                return HttpResponse(json, content_type='application/json')
        elif request.GET.has_key('sat'):
            channels = base.filter(transponder__satellite__id=request.GET['sat'])
            if len(channels):
                json = serializers.serialize('json',
                    channels,
                    indent=2,
                    use_natural_keys=True
                    )
                return HttpResponse(json, content_type='application/json')
        else:
                return HttpResponseNotFound()
    return HttpResponseBadRequest()