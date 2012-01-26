from django.contrib import admin
from models import Arquivo_Epg
from forms import ArquivoEpgForm

class Arquivo_Epg_admin(admin.ModelAdmin):
	readonly_fields = ('source_info_url','source_info_name','source_data_url','generator_info_name','generator_info_url','minor_start','major_stop','numberofElements','importedElements')
	class Meta:
		form = ArquivoEpgForm
	class Media:
		js = ('jquery/jquery-1.6.2.js','jquery-ui/js/jquery-ui-1.8.17.custom.min.js','epg.js',)
		css = {
			"all": ("jquery-ui/css/smoothness/jquery-ui-1.8.17.custom.css",)
		}

admin.site.register(Arquivo_Epg,Arquivo_Epg_admin)
