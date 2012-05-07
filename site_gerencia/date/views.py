from django.http import HttpResponse
from datetime import datetime

def index(request):
    return HttpResponse(datetime.now())