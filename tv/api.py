#!/usr/bin/env python
# -*- encoding:utf8 -*-

#from django.conf.urls.defaults import *

from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.authentication import BasicAuthentication
from tastypie.authentication import Authentication
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authentication import MultiAuthentication

from tastypie.api import NamespacedApi
from tastypie.resources import NamespacedModelResource

from client.models import SetTopBox

import models
import logging


class ChannelResource(NamespacedModelResource):
    source = fields.CharField(blank=True)

    class Meta:
        queryset = models.Channel.objects.filter(enabled=True,
            source__isnull=False)
        authorization = ReadOnlyAuthorization()
        excludes = ['enabled']
        allowed_methods = ['get']
        urlconf_namespace = 'tv'
        authentication = MultiAuthentication(
            BasicAuthentication(realm='cianet-middleware'),
            Authentication(),
            ApiKeyAuthentication())

    def dehydrate_source(self, bundle):
        return '%s:%d' % (bundle.obj.source.ip, bundle.obj.source.port)

    def apply_authorization_limits(self, request, object_list):
        log = logging.getLogger('api')
        log.info('ChannelResource User=%s', request.user)
        object_list = super(ChannelResource, self).apply_authorization_limits(
            request, object_list)
        stb = SetTopBox.objects.get(serial_number=request.user.username)
        channels = stb.get_channels()
        log.info('Filter for STB=%s, channels=%s', stb, channels)
        return channels


api = NamespacedApi(api_name='v1', urlconf_namespace='tv')
api.register(ChannelResource())
