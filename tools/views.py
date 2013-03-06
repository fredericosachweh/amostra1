from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import logging


@never_cache
@csrf_exempt
def log(request):
    log = logging.getLogger('stblog')
    log.debug('ADDR:%s COOKIE:%s USER_AGENT:%s POST:%s GET:%s',
        request.META.get('REMOTE_ADDR'),
        request.META.get('HTTP_COOKIE'),
        request.META.get('HTTP_USER_AGENT'),
        request.POST,
        request.GET,
    )
    return HttpResponse('')


@never_cache
def date(request):
    import time
    ts = time.strftime("%s")
    #tz = time.timezone - 3600
    g, l = time.gmtime(), time.localtime()
    tz = (g.tm_hour - l.tm_hour) * 3600
    ltz = 0
    response = '{"timestamp": %s, "timezone": %d, "localtimezone": %d}' % (ts,
        tz, ltz)
    return HttpResponse(response, content_type='application/json')


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
    return HttpResponse(response, content_type='application/json')
