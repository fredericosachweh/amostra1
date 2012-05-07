from django.http import HttpResponse

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
    
def date(request):
    from datetime import datetime
    return HttpResponse(datetime.now())
    #return HttpResponse('2012-01-07 13:17:45.702043')