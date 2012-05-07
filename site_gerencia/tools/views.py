from django.http import HttpResponse
from django.views.decorators.cache import never_cache

def log(request):
    from pprint import pprint
    pprint((
        'Log enviado pelo stdout do Settopbox', 
        request.META.get('REMOTE_ADDR'), 
        request.META.get('HTTP_COOKIE'), 
        request.META.get('HTTP_USER_AGENT'), 
        request.POST, 
    ))
    print('');
    #print(request)
    return HttpResponse('')

@never_cache
def date(request):
    from datetime import datetime
    return HttpResponse(datetime.now())
    #return HttpResponse('2012-01-01 13:00:00.702043')