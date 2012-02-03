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
		#importer.delete_from_db()
		#importer.import_channel_elements()
		#importer.delete_from_db()
		#importer.import_channel_elements_fast()
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
	
def get_channels_list(request):
	resp = list()
	for c in Channel.objects.only('channelid'):
		resp.append({ 'pk' : c.id, 'channelid' : c.channelid })
	import simplejson
	enc = simplejson.encoder.JSONEncoder()
	response = enc.encode(resp)
	return HttpResponse(response,mimetype='application/javascript')
	
def get_channel_info(request,channel_id=None):
	channel = get_object_or_404(Channel,id=channel_id)
	resp = { 'channelid' : channel.channelid, 'icon' : channel.icon_src }
	resp['display-names'] = list()
	for c in channel.displays.values('lang__value', 'value'):
		resp['display-names'].append({ 'lang' : c['lang__value'], 'value' : c['value'] })
	import simplejson
	enc = simplejson.encoder.JSONEncoder()
	response = enc.encode(resp)
	return HttpResponse(response,mimetype='application/javascript')

def get_channel_programmes(request,channel_id=None):
	channel = get_object_or_404(Channel,id=channel_id)
	if request.method == 'GET':
		from datetime import datetime,timedelta
		start = request.GET.get('start', datetime.now())
		stop = request.GET.get('stop', datetime.now() + timedelta(hours=1))
		if start > stop:
			return HttpResponseBadRequest('Stop cannot be higher that start time')
		
		time_range = (start,stop)
		resp = list()
		for g in Guide.objects.filter(channel=channel,start__range=time_range,stop__range=time_range):
			resp.append({ 'pk' : g.programme.pk, 'programid' : g.programme.programid, 'start' : str(g.start), 'stop' : str(g.stop) })
			
		import simplejson
		enc = simplejson.encoder.JSONEncoder()
		response = enc.encode(resp)
		return HttpResponse(response,mimetype='application/javascript')
	else:
		return HttpResponseBadRequest('Only GET method is supported')

def get_programme_info(request,programme_id=None):
	p = get_object_or_404(Programme,id=programme_id)
	if request.method == 'GET':
		resp = { 'programid' : p.programid, 'desc' : p.desc, 'date' : str(p.date) }
		resp['country'] = p.country
		resp['video'] = p.video
		resp['rating'] = p.rating
		resp['titles'] = list()
		for t in p.titles.values_list('lang__value', 'value'):
			resp['titles'].append({ 'lang' : t[0], 'value' : t[1] })
		resp['sub_titles'] = list()
		for st in p.sub_titles.values_list('lang__value', 'value'):
			resp['secondary-titles'].append({ 'lang' : t[0], 'value' : t[1] })
		resp['categories'] = list()
		for ca in p.categories.values_list('lang__value', 'value'):
			resp['categories'].append({ 'lang' : ca[0], 'value' : ca[1] })
		resp['episode_numbers'] = list()
		for ep in p.episode_numbers.values_list('system', 'value'):
			resp['episode_numbers'].append({ 'system' : ep[0], 'value' : ep[1] })
		resp['directors'] = list()
		for d in p.directors.values_list('name'):
			resp['directors'].append({ 'name' : d[0] })
		resp['actors'] = list()
		for a in p.actors.values_list('name'):
			resp['actors'].append({ 'name' : a[0] })
		import simplejson
		enc = simplejson.encoder.JSONEncoder()
		response = enc.encode(resp)
		return HttpResponse(response,mimetype='application/javascript')
	else:
		return HttpResponseBadRequest('Only GET method is supported')


