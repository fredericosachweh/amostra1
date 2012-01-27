#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from data_importer import XML_Epg_Importer,Zip_to_XML
from models import Epg_Source,Channel,Programme

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
	f = open(epg_source.filefield.path)
	importer = XML_Epg_Importer(f,epg_source_instance=epg_source)
	deletedElements = importer.delete_from_db()
	f.close()
	import simplejson
	enc = simplejson.encoder.JSONEncoder()
	response = enc.encode(deletedElements)
	return HttpResponse(response,mimetype='application/javascript')
	
def get_channel_debug(request,epg_source_id=None):
	epg_source = get_object_or_404(Epg_Source,id=epg_source_id)
	res = []
	for c in Channel.objects.filter(source=epg_source):
		start = 0
		stop = 0
		for p in Programme.objects.filter(channel=c):
			if start == 0 or start > p.start:
				start = p.start
			if stop == 0 or stop < p.stop:
				stop = p.stop
		res[c.channelid]["start"] = start
		res[c.channelid]["stop"] = stop
	import simplejson
	enc = simplejson.encoder.JSONEncoder()
	response = enc.encode(res)
	return HttpResponse(response,mimetype='application/javascript')
	
	
