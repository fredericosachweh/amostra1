# Create your views here.

from django.http import HttpResponse

def home(request):
    return HttpResponse('Na raiz do sistema')

def process_list(request):
    from lib.player import Player
    p = Player()
    p.list_running()
    return HttpResponse('Listagem')
