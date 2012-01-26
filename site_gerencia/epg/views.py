from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from models import Arquivo_Epg,XML_Epg_Importer,Zip_to_XML

#def import(request,arquivo_epg_id=None):
#	print 'Chamou import na view'

def debug(request):
	print request

def import_to_db(request,arquivo_epg_id=None):
	arquivo = get_object_or_404(Arquivo_Epg,id=arquivo_epg_id)
	import simplejson
	import mimetypes
	file_list = Zip_to_XML(arquivo.filefield.path)
	for f in file_list.get_all_files():
		importer = XML_Epg_Importer(f)
		importer.parse()
		f.close()
#	canais = dvb.scan_channels()
	enc = simplejson.encoder.JSONEncoder()
	resposta = enc.encode("Eduardo is the best")
	print(resposta)
	return HttpResponse(resposta,mimetype='application/javascript')

