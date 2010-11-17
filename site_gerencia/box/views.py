#from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
#from django.core.paginator import Paginator, InvalidPage, EmptyPage
#from django.shortcuts import get_object_or_404
#from django.core.urlresolvers import reverse



def index(request):
    return render_to_response(
                              'box/index.html',
                              { 'info':'info' },
                              context_instance=RequestContext(request)
                              )
