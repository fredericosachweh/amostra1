from django.apps import apps
from django.contrib import admin


class ChannelAdmin(admin.ModelAdmin):

    search_fields = ('display_names__value', )
    list_display = ('channelid', '__unicode__', )


class GuideAdmin(admin.ModelAdmin):

    search_fields = ('programme__titles__value',
        'channel__display_names__value', )
    list_display = ('channel', 'start', 'stop', 'programme', )
    list_filter = ('channel', )
    date_hierarchy = 'start'
    ordering = ('start', )
    readonly_fields = ('programme', 'channel', )


admin.site.register(apps.get_model('epg', 'Channel'), ChannelAdmin)
admin.site.register(apps.get_model('epg', 'Guide'), GuideAdmin)