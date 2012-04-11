#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import *

from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.api import Api

from models import *

class ChannelResource(ModelResource):
    class Meta:
        queryset = Channel.objects.all()
        authorization = Authorization()

api = Api(api_name='tv')
api.register(ChannelResource())
