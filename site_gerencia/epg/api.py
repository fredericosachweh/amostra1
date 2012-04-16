#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import *

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.api import Api
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from models import *

class UrlResource(ModelResource):
    class Meta:
        queryset = Url.objects.all()
        authorization = Authorization()
        allowed_methods = []
        include_resource_uri = False

class IconResource(ModelResource):
    class Meta:
        queryset = Icon.objects.all()
        authorization = Authorization()
        allowed_methods = []
        include_resource_uri = False

class Display_NameResource(ModelResource):
    class Meta:
        queryset = Display_Name.objects.all()
        authorization = Authorization()
        allowed_methods = []
        include_resource_uri = False

class ChannelResource(ModelResource):
    display_names = fields.ToManyField(Display_NameResource, 'display_names', full=True)
    icons = fields.ToManyField(IconResource, 'icons', full=True)
    urls = fields.ToManyField(UrlResource, 'urls', full=True)
    class Meta:
        #XXX: Filtrar apenas canais que sejam relacionados com canais da operadora
        queryset = Channel.objects.all()
        authorization = Authorization()
        allowed_methods = ['get']
        filtering = {
            "channelid": ALL
        }

api = Api(api_name='epg')
api.register(Display_NameResource())
api.register(ChannelResource())