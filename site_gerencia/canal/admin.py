#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.contrib import admin
from models import Canal,Genero,Programa

class CanalAdmin(admin.ModelAdmin):
    fields = ('numero','nome','descricao','logo','sigla','ip','porta',)
    list_display = ('imagem_thum','numero','nome',)
    inline = (Programa,)

class ProgramaAdmin(admin.ModelAdmin):
    list_filter = ('canal','genero',)

admin.site.register(Canal,CanalAdmin)
admin.site.register(Genero)
admin.site.register(Programa,ProgramaAdmin)


