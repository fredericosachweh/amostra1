from django.conf import settings
from django.http import HttpResponseRedirect
import re

class RequireLoginMiddleware(object):
    def __init__(self):
        self.urls = tuple([re.compile(url) for url in settings.LOGIN_REQUIRED_URLS])
    
    def process_request(self, request):
        for url in self.urls:
            if url.match(request.path) and request.user.is_anonymous():
                return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL,
                    request.path))


class APIKeyLoginMiddleware(object):

    def process_request(self, request):
        from tastypie.models import ApiKey
        #log.debug('GET:%s', request.GET)
        #for i in request.META:
        #    log.debug('H:%s=%s', i, request.META.get(i))
        api_key = request.GET.get('api_key', None) or \
            request.POST.get('api_key', None) or \
            request.META.get('HTTP_API_KEY', None)
        if api_key is not None:
            log.debug('api_key:%s', api_key)
            log.debug('META:%s', request.META.get('HTTP_API_KEY', None))
            log.debug('POST:%s', request.POST.get('api_key', None))
            log.debug('GET:%s', request.GET.get('api_key', None))
        else:
            return
        api = ApiKey.objects.get(key=api_key)
        user = api.user
        #login(request, api.user)
        if user is not None:
            if user.is_active:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth.login(request, user)
            request.user = user
            #auth.login(request, user)
        return

