from django.contrib import admin
from models import Channel
from models import Guide
#from models import Programme


class ChannelAdmin(admin.ModelAdmin):

    search_fields = ('display_names__value', )


class GuideAdmin(admin.ModelAdmin):

    search_fields = ('programme__titles__value',
        'channel__display_names__value', )
    list_display = ('channel', 'start', 'stop', 'programme', )
    list_filter = ('channel', )
    date_hierarchy = 'start'
    ordering = ('start', )
    readonly_fields = ('programme', 'channel', )

admin.site.register(Channel, ChannelAdmin)
admin.site.register(Guide, GuideAdmin)
#admin.site.register(Programme)
