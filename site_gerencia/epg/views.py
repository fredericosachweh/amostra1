#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from data_importer import XML_Epg_Importer,Zip_to_XML
from models import Epg_Source,Channel,Programme,Guide

def import_to_db(request,epg_source_id=None):
	epg_source = get_object_or_404(Epg_Source,id=epg_source_id)
	import simplejson
	# TODO: put this inside a transaction
	epg_source.importedElements = 0
	epg_source.save()
	file_list = Zip_to_XML(epg_source.filefield.path)
	for f in file_list.get_all_files():
		importer = XML_Epg_Importer(f,epg_source_instance=epg_source)
		importer.import_to_db()
		f.close()
	enc = simplejson.encoder.JSONEncoder()
	response = enc.encode("Fim do processo de importação")
	return HttpResponse(response,mimetype='application/javascript')

def get_import_current_status(request,epg_source_id=None):
	epg_source = get_object_or_404(Epg_Source,id=epg_source_id)
	import simplejson
	enc = simplejson.encoder.JSONEncoder()
	percent = (epg_source.importedElements*100) / epg_source.numberofElements
	response = enc.encode(percent)
	return HttpResponse(response,mimetype='application/javascript')

# Remove all entries from this Epg_Source
def delete_from_db(request,epg_source_id=None):
	epg_source = get_object_or_404(Epg_Source,id=epg_source_id)
	Guide.objects.filter(source=epg_source).delete()
	Programme.objects.filter(source=epg_source).delete()
	Channel.objects.filter(source=epg_source).delete()
	import simplejson
	enc = simplejson.encoder.JSONEncoder()
	response = enc.encode('Elementos deletados do epg source %d' % epg_source.id)
	return HttpResponse(response,mimetype='application/javascript')

