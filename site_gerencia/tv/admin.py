#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.contrib import admin
from models         import Channel
from django.db      import models

from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring      import mark_safe

from django.conf.urls.defaults import url, patterns
from django.utils.functional import update_wrapper
from tv.admin_views import create_canal_wizard

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
                % (
                    image_url,
                    image_url.replace('original', 'thumb'),
                    file_name,
                    ('Change:')
                )
            )
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class ChannelAdmin(admin.ModelAdmin):
    """
    Define modelo administrativo do Canal
    """
    fieldsets = ((None, {
        'fields':(
            ('number', 'name', 'channelid', 'enabled'),
            'description', 'image',
                ('source'),
            ),
        }),)
    #readonly_fields = ('thumb',)
    #filter_horizontal = ('programa',)
    #fields = ('numero','nome','descricao','logo','sigla','source', )
    list_display = ('image_thum', 'number', 'name', 'channelid', 'source', 'enabled', 'switch_link')
    list_display_links = ('image_thum',)
    list_editable = ('number', 'source', 'name', 'channelid', 'enabled')
    #inline        = (Programa,)
    save_as = True
    list_per_page = 10
    search_fields = ['name', 'channelid', 'source']
    formfield_overrides = {models.ImageField: {'widget': AdminImageWidget}}
    ## Colocando imegem dentro do formulario
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'image':
            request = kwargs.pop("request", None)
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        return super(ChannelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
#    class Meta:
#        form = CanalForm
#
    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwds):
                kwds['admin'] = self
                return self.admin_site.admin_view(view)(*args, **kwds)
            return update_wrapper(wrapper, view)

        urlpatterns = patterns('',
            url(r'^wizard/$',
                wrap(create_canal_wizard),
                name='channel_wizard_add')
        )
        urlpatterns += super(ChannelAdmin, self).get_urls()
        return urlpatterns


admin.site.register(Channel, ChannelAdmin)
