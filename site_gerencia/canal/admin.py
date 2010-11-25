#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.contrib import admin
from models import Canal,Genero,Programa

class CanalAdmin(admin.ModelAdmin):
    fields = ('numero','nome','descricao','logo','sigla','ip','porta',)#
    list_display = ('numero','nome','imagem_thum',)
    #inlines = ('imagem_thum',)

admin.site.register(Canal,CanalAdmin)
admin.site.register(Genero)
admin.site.register(Programa)


