#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import *

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.api import Api

from models import *

# Exemplo de foreignKey
from stream import api as stream_api

class ChannelResource(ModelResource):
    # Exemplo de foreignKey
    #source_data = fields.ForeignKey(stream_api.SourceResource, 'source', full=True)
    source = fields.CharField(blank=True)
    class Meta:
        queryset = Channel.objects.filter(enabled=True, source__isnull=False)
        authorization = Authorization()
        excludes = ['enabled']
        allowed_methods = ['get']
    def dehydrate_source(self, bundle):
        return bundle.obj.source

api = Api(api_name='tv')
api.register(ChannelResource())
