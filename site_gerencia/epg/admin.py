from django.contrib import admin
from models import Channel
from forms import Epg_Source_Form


class Epg_Source_admin(admin.ModelAdmin):

    class Meta:
        form = Epg_Source_Form


class ChannelAdmin(admin.ModelAdmin):

    search_fields = ('display_names__value', )

#admin.site.register(Epg_Source, Epg_Source_admin)
admin.site.register(Channel, ChannelAdmin)
