from django.http import HttpResponse
from pprint import pprint

def index(request):
    pprint(('Log', request.POST, request.META, ))
    #print(request)
    return HttpResponse('')