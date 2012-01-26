#!/usr/bin/env python
# -*- encoding:utf-8 -*-

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
	arquivo.importedElements = 0
	arquivo.save()
	file_list = Zip_to_XML(arquivo.filefield.path)
	for f in file_list.get_all_files():
		importer = XML_Epg_Importer(f,arquivo_epg_instance=arquivo)
		importer.parse()
		f.close()
	enc = simplejson.encoder.JSONEncoder()
	response = enc.encode("Fim do processo de importação")
	return HttpResponse(response,mimetype='application/javascript')

def get_import_current_status(request,arquivo_epg_id=None):
	arquivo = get_object_or_404(Arquivo_Epg,id=arquivo_epg_id)
	import simplejson
	enc = simplejson.encoder.JSONEncoder()
	percent = (arquivo.importedElements*100) / arquivo.numberofElements
	response = enc.encode(percent)
	return HttpResponse(response,mimetype='application/javascript')

