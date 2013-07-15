from django.conf import settings
from django.http import HttpResponseRedirect
#from django.db.models.loading import get_model
#from django.utils.importlib import import_module
from django.middleware.csrf import get_token
from django.contrib import auth
import re
import logging
log = logging.getLogger('api')


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
        api_key = request.GET.get('api_key', None)
        #log.debug('KEY:%s', api_key)
        if api_key is None:
            #log.debug('Saindo')
            return
        api = ApiKey.objects.get(key=api_key)
        #log.debug('API:%s', api)
        user = api.user
        #login(request, api.user)
        if user is not None:
            if user.is_active:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth.login(request, user)
            request.user = user
            #auth.login(request, user)
        return

    #def process_response(self, request, response):
    #    return response
