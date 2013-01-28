#!/usr/bin/env python
# -*- encoding:utf8 -*-
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import BasicAuthentication
from tastypie.authentication import Authentication
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authentication import MultiAuthentication
from tastypie.api import NamespacedApi
from tastypie.resources import NamespacedModelResource
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.validation import Validation
from tastypie.exceptions import BadRequest
from django.db import IntegrityError
import models
from tv.models import Channel
import logging

## Validation:
#http://stackoverflow.com/questions/7435986/how-do-i-configure-tastypie-to-treat-a-field-as-unique


class MyAuthorization(DjangoAuthorization):

    def is_authorized(self, request, object=None):
        ok = super(MyAuthorization, self).is_authorized(request, object)
        if ok is False and False:
            log = logging.getLogger('debug')
            log.debug('Method:%s', request.method)
            log.debug('User:%s', request.user)
            log.debug('OK:%s', ok)
        return ok


class SetTopBoxResource(NamespacedModelResource):

    class Meta:
        queryset = models.SetTopBox.objects.all()
        resource_name = 'settopbox'
        authorization = MyAuthorization()
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'
        validation = Validation()
        authentication = MultiAuthentication(
            Authentication(),
            BasicAuthentication(),
            ApiKeyAuthentication())

    def obj_create(self, bundle, request=None, **kwargs):
        log = logging.getLogger('debug')
        log.debug(bundle)
        try:
            bundle = super(SetTopBoxResource, self).obj_create(bundle,
                request, **kwargs)
        except IntegrityError:
            raise BadRequest('Duplicate entry for settopbox.serial_number')
        return bundle


class SetTopBoxParameterResource(NamespacedModelResource):

    settopbox = fields.ForeignKey(SetTopBoxResource, 'settopbox', null=False)

    class Meta:
        queryset = models.SetTopBoxParameter.objects.all()
        resource_name = 'settopboxparameter'
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'
        always_return_data = True
        validation = Validation()
        authentication = Authentication()
        filtering = {
            "settopbox": ALL_WITH_RELATIONS,
            "key": ALL,
            "value": ALL
        }


class ChannelResource(NamespacedModelResource):

    number = fields.CharField(attribute='number', unique=True)

    class Meta:
        queryset = Channel.objects.all()
        resource_name = 'channel'
        authorization = Authorization()


class SetTopBoxChannelResource(NamespacedModelResource):

    settopbox = fields.ForeignKey(SetTopBoxResource, 'settopbox', null=False)
    channel = fields.ForeignKey(ChannelResource, 'channel', null=False)

    class Meta:
        queryset = models.SetTopBoxChannel.objects.all()
        resource_name = 'settopboxchannel'
        authorization = DjangoAuthorization()
        always_return_data = True
        validation = Validation()
        authentication = Authentication()
        filtering = {
            "settopbox": ALL,
            "channel": ALL
        }

    def obj_create(self, bundle, request=None, **kwargs):
        try:
            bundle = super(SetTopBoxChannelResource, self).obj_create(bundle,
                request, **kwargs)
        except IntegrityError:
            raise BadRequest('Duplicate entry for settopbox channel')
        return bundle

api = NamespacedApi(api_name='v1', urlconf_namespace='client')
api.register(SetTopBoxResource())
api.register(SetTopBoxParameterResource())
api.register(ChannelResource())
api.register(SetTopBoxChannelResource())
