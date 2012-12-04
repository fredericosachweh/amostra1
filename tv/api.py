#!/usr/bin/env python
# -*- encoding:utf8 -*-

#from django.conf.urls.defaults import *

from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.api import NamespacedApi
from tastypie.resources import NamespacedModelResource

import models


class ChannelResource(NamespacedModelResource):
    source = fields.CharField(blank=True)

    class Meta:
        queryset = models.Channel.objects.filter(enabled=True,
            source__isnull=False)
        authorization = DjangoAuthorization()
        excludes = ['enabled']
        allowed_methods = ['get']
        urlconf_namespace = 'tv'

    def dehydrate_source(self, bundle):
        return '%s:%d' % (bundle.obj.source.ip, bundle.obj.source.port)


api = NamespacedApi(api_name='v1', urlconf_namespace='tv')
api.register(ChannelResource())
