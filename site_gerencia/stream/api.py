#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import *

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.api import Api

from stream.models import UniqueIP

class SourceResource(ModelResource):
    class Meta:
        queryset = UniqueIP.objects.all()
        authorization = Authorization()
        allowed_methods = ['get']

api = Api(api_name='stream')
api.register(SourceResource())
