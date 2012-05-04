#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import *

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.api import Api

from models import *

class ChannelResource(ModelResource):
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
