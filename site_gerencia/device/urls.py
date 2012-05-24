#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls.defaults import patterns, include
from django.db.models.loading import get_model

# List of models witch should have a switch_link field on the admin
models = ['dvbtuner', 'isdbtuner', 'unicastinput', 'multicastinput',
        'fileinput', 'demuxedservice', 'multicastoutput', 'streamrecorder']
urls = []
for model in models:
    view = 'deviceserver_switchlink'
    klass = get_model('device', model)
    # Start
    urls.append(
        (r'^%s/start/(?P<pk>\d+)/$' % model, view,
        {'action' : 'start', 'klass' : klass},
         '%s_start' % model),
    )
    # Stop
    urls.append(
        (r'^%s/stop/(?P<pk>\d+)/$' % model, view,
        {'action' : 'stop', 'klass' : klass},
         '%s_stop' % model),
    )
    # Recover from undefined state, needed usually when the process crashed
    urls.append(
        (r'^%s/recover/(?P<pk>\d+)/$' % model, view,
        {'action' : 'recover', 'klass' : klass},
         '%s_recover' % model),
    )
deviceserver_patterns = patterns('device.views', *urls)

urlpatterns = patterns('',
    (r'^$','device.views.home'),
    (r'^server/status/(?P<pk>\d+)/$','device.views.server_status'),
    (r'^server/interfaces/$','device.views.server_list_interfaces'),
    (r'^server/(?P<pk>\d+)/adapter/add/$','device.views.server_update_adapter',
     {'action' : 'add'}, 'server_adapter_add'),
    (r'^server/(?P<pk>\d+)/adapter/remove/$','device.views.server_update_adapter',
     {'action' : 'remove'}, 'server_adapter_remove'),
    (r'^server/dvbtuners/$','device.views.server_list_dvbadapters'),
    (r'^server/isdbtuners/$','device.views.server_available_isdbtuners'),
    (r'^server/fileinput/scanfolder/$',
     'device.views.server_fileinput_scanfolder'),
    (r'^server/(?P<pk>\d+)/coldstart/$','device.views.server_coldstart'),
    # DeviceServer subclasses controls
    (r'^deviceserver/', include(deviceserver_patterns)),
    
    (r'^inputmodel/scan/$', 'device.views.inputmodel_scan'),
    (r'^file/start/(?P<pk>\d+)/$', 'device.views.file_start'),
    (r'^file/stop/(?P<pk>\d+)/$', 'device.views.file_stop'),
    (r'^multicat/start/(?P<pk>\d+)/$','device.views.multicat_start'),
    (r'^multicat/stop/(?P<pk>\d+)/$','device.views.multicat_stop'),
    (r'^multicatredirect/start/(?P<pk>\d+)/$','device.views.multicat_redirect_start'),
    (r'^multicatredirect/stop/(?P<pk>\d+)/$','device.views.multicat_redirect_stop'),
    (r'^autofilltuner/(?P<ttype>[a-z]+)/$',
        'device.views.auto_fill_tuner_form'),
)
