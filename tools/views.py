from django.http import HttpResponse
from django.views.decorators.cache import never_cache
import logging


@never_cache
def log(request):
    log = logging.getLogger('stblog')
    log.debug('ADDR:%s COOKIE:%s USER_AGENT:%s POST:%s GET:%s',
        request.META.get('REMOTE_ADDR'),
        request.META.get('HTTP_COOKIE'),
        request.META.get('HTTP_USER_AGENT'),
        request.POST,
        request.GET,
    )
    from pprint import pprint
    pprint((
        'Log enviado pelo stdout do Settopbox',
        request.META.get('REMOTE_ADDR'),
        request.META.get('HTTP_COOKIE'),
        request.META.get('HTTP_USER_AGENT'),
        request.POST,
        request.GET,
    ))
    print('')
    #print(request)
    return HttpResponse('')


@never_cache
def date(request):
    #from datetime import datetime
    import time

    #FORCE DATE
    #now = datetime(2012, 7, 18, 12, 15, 00)
    #timestamp = int(time.mktime(now.timetuple()))

    #timestamp = time.mktime(now.timetuple())
    #timestamp = now.strftime("%s")
    #timestamp = time.mktime(time.gmtime())

    timestamp = time.strftime("%s")
    #TODO: tornar dinamico ativar/desativar horario de verao
    #FIXME: o -3600 corrige o horario de verao...
    timezone = time.timezone - 3600
    response = '{"timestamp": %s, "timezone": %d}' % (timestamp, timezone)
    return HttpResponse(response)
    #return HttpResponse('2012-05-15 17:14:55.702043')


@never_cache
def network(request):
    import re

    def DottedIPToInt(dotted_ip):
        exp = 3
        intip = 0
        for quad in dotted_ip.split('.'):
                intip = intip + (int(quad) * (256 ** exp))
                exp = exp - 1
        return(intip)

    ip = request.META['REMOTE_ADDR']

    ipAsInt = DottedIPToInt(ip)
    formatedMac = re.sub("(.{2})", "\\1:", ('FF%010d' % ipAsInt), re.DOTALL)
    mac = formatedMac[0:-1]
    response = '{"mac": "%s", "ip": "%s"}' % (mac, ip)
    return HttpResponse(response)
