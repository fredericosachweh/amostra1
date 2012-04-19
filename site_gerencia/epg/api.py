#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import *

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.api import Api
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from models import *

class MetaDefault:
    authorization = Authorization()
    allowed_methods = ['get']



class LangResource(ModelResource):
    class Meta(MetaDefault):
        queryset = Lang.objects.all()
        

class UrlResource(ModelResource):
    class Meta(MetaDefault):
        queryset = Url.objects.all()

class IconResource(ModelResource):
    class Meta(MetaDefault):
        queryset = Icon.objects.all()

class Display_NameResource(ModelResource):
    lang = fields.ForeignKey(LangResource, 'lang')
    class Meta(MetaDefault):
        queryset = Display_Name.objects.all()

class ChannelResource(ModelResource):
    display_names = fields.ToManyField(Display_NameResource, 'display_names', full=True)
    icons = fields.ToManyField(IconResource, 'icons', full=True)
    urls = fields.ToManyField(UrlResource, 'urls', full=True)
    class Meta(MetaDefault):
        #XXX: Filtrar apenas canais que sejam relacionados com canais da operadora
        queryset = Channel.objects.all()
        filtering = {
            "channelid": ALL
        }

api = Api(api_name='epg')
api.register(ChannelResource())
api.register(LangResource())
api.register(IconResource())
api.register(Display_NameResource())