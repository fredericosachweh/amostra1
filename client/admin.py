# -*- encoding:utf-8 -*-


from django.contrib.admin import site, ModelAdmin
import models


class SetTopBoxConfigAdmin(ModelAdmin):
    search_fields = ('settopbox__mac', 'settopbox__serial_number', )
    list_display = ('settopbox', 'key', 'value', )
    list_filter = ('settopbox', )


class SetTopBoxChannelAdmin(ModelAdmin):
    search_fields = ('settopbox__mac', 'settopbox__serial_number', )
    list_display = ('settopbox', 'channel', )
    list_filter = ('settopbox', )


site.register(models.SetTopBox)
site.register(models.SetTopBoxParameter)
site.register(models.SetTopBoxChannel, SetTopBoxChannelAdmin)
site.register(models.SetTopBoxConfig, SetTopBoxConfigAdmin)
