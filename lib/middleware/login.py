from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import auth
import re
import logging
log = logging.getLogger('debug')


class RequireLoginMiddleware(object):

    def __init__(self):
        self.urls = tuple([re.compile(url) for url in settings.LOGIN_REQUIRED_URLS])

    def process_request(self, request):
        for url in self.urls:
            if url.match(request.path) and request.user.is_anonymous():
                return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, request.path))


def extract_headers(request):
    import re
    regex_http_ = re.compile(r'^HTTP_.+$')
    regex_content_type = re.compile(r'^CONTENT_TYPE$')
    regex_content_length = re.compile(r'^CONTENT_LENGTH$')
    request_headers = {}
    for header in request.META:
        if regex_http_.match(header) or regex_content_type.match(header)\
                or regex_content_length.match(header):
            request_headers[header] = request.META[header]
    return request_headers


class APIKeyLoginMiddleware(object):

    def process_request(self, request):
        from tastypie.models import ApiKey
        from tastypie.authentication import ApiKeyAuthentication
        log.debug('request_headers=%s', extract_headers(request))
        # ApiKey from header
        apikeyauth = ApiKeyAuthentication()
        username, api_key = apikeyauth.extract_credentials(request)
        if api_key is not None:
            log.debug('api_key:%s', api_key)
        else:
            return
        api = ApiKey.objects.filter(key=api_key)
        if api.count() == 0:
            return
        user = api[0].user
        log.debug('User from api=%s', user)
        # login(request, api.user)
        if user is not None:
            if user.is_active:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth.login(request, user)
            request.user = user
            # auth.login(request, user)
        return

