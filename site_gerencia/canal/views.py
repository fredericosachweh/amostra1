from base import *
from django.utils.translation import ugettext as _
from canal import models, forms

def index(request):
    lista =  models.Canal.objects.all()
    paginator = Paginator(lista, 2)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        canallist_ = paginator.page(page)
    except (EmptyPage, InvalidPage):
        canallist_ = paginator.page(paginator.num_pages)
    return render_to_response('canal/canais.html', { 'canais': lista , 'lista':canallist_},
                                context_instance=RequestContext(request))


def add(request):
    """
    Adiciona novo canal.
    """
    if request.method == 'POST':
        # Adiciona novo canal
        form = forms.CanalForm(request.POST,request.FILES)
        if form.is_valid():
            newnode = models.Canal()
            fnode = forms.CanalForm(request.POST,request.FILES,instance=newnode)
            fnode.save()
            #request.user.message_set.create(message=_("Canal registrado com sucesso"))
            return HttpResponseRedirect(reverse('canal_get'))
        else:
            return render_to_response('canal/canaladd.html', {'form': form},
                                        context_instance=RequestContext(request))
    else:
        form = forms.CanalForm()
        return render_to_response('canal/canaladd.html', {'form': form},
                                            context_instance=RequestContext(request))

def edit(request,id):
    """
    Edita um canal.
    """
    canal = get_object_or_404(models.Canal,pk=id)
    form = forms.CanalForm(instance=canal)
    return render_to_response('canal/canaladd.html', {'form': form},
                                        context_instance=RequestContext(request))


