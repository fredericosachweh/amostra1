from django.http import HttpResponse
from pprint import pprint

def index(request):
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