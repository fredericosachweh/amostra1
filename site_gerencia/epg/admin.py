from django.contrib import admin
from models import Epg_Source, Channel
from forms import Epg_Source_Form


class Epg_Source_admin(admin.ModelAdmin):

    readonly_fields = ('source_info_url', \
        'source_info_name', \
        'source_data_url', \
        'generator_info_name', \
        'generator_info_url', \
        'minor_start', \
        'major_stop', \
        'minor_start_local',
        'major_stop_local',
        'numberofElements', \
        'importedElements', \
        'created', \
        )

    class Meta:
        form = Epg_Source_Form

    class Media:
        js = ('jquery/jquery-1.6.2.js',
              'jquery-ui/js/jquery-ui-1.8.17.custom.min.js',
              'epg.js',)
        css = {
            "all": ("jquery-ui/css/smoothness/jquery-ui-1.8.17.custom.css",)
        }


class ChannelAdmin(admin.ModelAdmin):
    pass

admin.site.register(Epg_Source, Epg_Source_admin)
admin.site.register(Channel, ChannelAdmin)
