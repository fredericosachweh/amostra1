from django.contrib import admin
from models import Arquivo_Epg
from forms import ArquivoEpgForm

class Arquivo_Epg_admin(admin.ModelAdmin):
	readonly_fields = ('source_info_url','source_info_name','source_data_url','generator_info_name','generator_info_url','minor_start','major_stop','numberofElements')
	class Meta:
		form = ArquivoEpgForm

admin.site.register(Arquivo_Epg,Arquivo_Epg_admin)
