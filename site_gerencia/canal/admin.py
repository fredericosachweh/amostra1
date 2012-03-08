#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.contrib import admin
from models         import Canal
from forms          import CanalForm
from django.db      import models

from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring      import mark_safe

from django.conf.urls.defaults import url, patterns
from django.utils.functional import update_wrapper
from canal.admin_views import create_canal_wizard

class AdminImageWidget(AdminFileWidget):
    """
    Formata renderização de imagem no HTML
    """
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            output.append(
                u'<a href="%s" target="_blank"><img src="%s" alt="%s" /></a>%s'
                %(
                    image_url,
                    image_url.replace('original', 'thumb'),
                    file_name,
                    ('Change:')
                )
            )
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))



class CanalAdmin(admin.ModelAdmin):
    """
    Define modelo administrativo do Canal
    """
    fieldsets = ((None, {
        'fields':( ('numero', 'nome', 'sigla', 'enabled'),'descricao', 'logo', ('source'), 'epg',),
        }), )
    #readonly_fields = ('thumb',)
    #filter_horizontal = ('programa',)
    #fields = ('numero','nome','descricao','logo','sigla','source', )
    list_display  = ('imagem_thum', 'numero', 'nome', 'source', 'enabled', )
    list_display_links = ('imagem_thum', )
    list_editable = ('numero', 'source', 'nome', )
    #inline        = (Programa,)
    save_as       = True
    list_per_page = 10
    search_fields = ['nome', 'source']
    formfield_overrides = {models.ImageField: {'widget': AdminImageWidget}}
    ## Colocando imegem dentro do formulario
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'logo':
            request          = kwargs.pop("request", None)
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        return super(CanalAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    class Meta:
        form = CanalForm
        
    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwds):
                kwds['admin'] = self   # Use a closure to pass this admin instance to our wizard
                return self.admin_site.admin_view(view)(*args, **kwds)
            return update_wrapper(wrapper, view)

        urlpatterns = patterns('',
            url(r'^wizard/$',
                wrap(create_canal_wizard),
                name='canal_wizard_add')
        )
        urlpatterns += super(CanalAdmin, self).get_urls()
        return urlpatterns

admin.site.register(Canal, CanalAdmin)

