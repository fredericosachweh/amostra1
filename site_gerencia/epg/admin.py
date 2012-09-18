from django.contrib import admin
from models import Epg_Source, Channel
from forms import Epg_Source_Form


class Epg_Source_admin(admin.ModelAdmin):

    #readonly_fields = ('source_info_url', \
    #    'source_info_name', \
    #    'source_data_url', \
    #    'generator_info_name', \
    #    'generator_info_url', \
    #    'minor_start', \
    #    'major_stop', \
    #    'minor_start_local',
    #    'major_stop_local',
    #    'numberofElements', \
    #    'importedElements', \
    #    'created', \
    #    )

    class Meta:
        form = Epg_Source_Form


class ChannelAdmin(admin.ModelAdmin):

    search_fields = ('display_names__value', )

#admin.site.register(Epg_Source, Epg_Source_admin)
admin.site.register(Channel, ChannelAdmin)
