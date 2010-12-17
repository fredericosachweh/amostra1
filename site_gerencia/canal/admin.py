#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.contrib import admin
from models import Canal,Genero,Programa
from forms import CanalForm
from django.db import models

from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name=str(value)
            output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" /></a> %s ' % \
                (image_url, image_url.replace('original','thumb'), file_name, ('Change:')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))



class CanalAdmin(admin.ModelAdmin):
    class Meta:
        form = CanalForm
    fieldsets = ((None,{
        'fields':( ('numero','nome','sigla'),'descricao','logo',('ip','porta'),),
        }),)
    #readonly_fields = ('thumb',)
    #filter_horizontal = ('programa',)
    #fields = ('numero','nome','descricao','logo','sigla','ip','porta', )
    list_display = ('imagem_thum','numero','nome','ip','porta',)
    list_display_links = ('numero','imagem_thum',)
    list_editable = ('ip','porta','nome',)
    #inline = (Programa,)
    save_as = True
    list_per_page = 10
    search_fields = ['nome','ip','porta']
    formfield_overrides = {models.ImageField: {'widget': AdminImageWidget}}
    ## Colocando imegem dentro do formulario
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'logo':
            request = kwargs.pop("request", None)
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        return super(CanalAdmin,self).formfield_for_dbfield(db_field, **kwargs)

class ProgramaAdmin(admin.ModelAdmin):
    list_filter = ('canal','genero',)
    date_hierarchy = 'hora_inicial'

admin.site.register(Canal,CanalAdmin)
admin.site.register(Genero)
admin.site.register(Programa,ProgramaAdmin)


