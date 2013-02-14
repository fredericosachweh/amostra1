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
        if ok is False:
            log = logging.getLogger('api')
            log.debug('Method:%s', request.method)
            log.debug('User:%s', request.user)
            log.debug('OK:%s', ok)
        return ok


class SetTopBoxResource(NamespacedModelResource):

    class Meta:
        queryset = models.SetTopBox.objects.all()
        resource_name = 'settopbox'
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'
        authorization = MyAuthorization()
        validation = Validation()
        authentication = MultiAuthentication(
            BasicAuthentication(realm='cianet-middleware'),
            Authentication(),
            ApiKeyAuthentication())

    def obj_create(self, bundle, request=None, **kwargs):
        log = logging.getLogger('api')
        log.debug('New STB=%s', bundle.data.get('serial_number'))
        try:
            bundle = super(SetTopBoxResource, self).obj_create(bundle,
                **kwargs)
        except IntegrityError:
            log.error('Duplicate entry for settopbox.serial_number=%s',
                bundle.data.get('serial_number'))
            raise BadRequest('Duplicate entry for settopbox.serial_number')
        return bundle

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
        log = logging.getLogger('api')
        log.debug('Update STB=%s', bundle.data.get('serial_number'))
        try:
            bundle = super(SetTopBoxResource, self).obj_update(bundle,
                request=request, **kwargs)
        except IntegrityError:
            log.error('Duplicate entry for settopbox.serial_number=%s',
                bundle.data.get('serial_number'))
            raise BadRequest('Duplicate entry for settopbox.serial_number')
        return bundle


class SetTopBoxParameterResource(NamespacedModelResource):

    settopbox = fields.ForeignKey(SetTopBoxResource, 'settopbox', null=False)

    class Meta:
        queryset = models.SetTopBoxParameter.objects.all()
        resource_name = 'settopboxparameter'
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'
        always_return_data = True
        filtering = {
            "settopbox": ALL,  # ALL_WITH_RELATIONS
            "key": ALL,
            "value": ALL
        }
        validation = Validation()
        authorization = MyAuthorization()
        authentication = MultiAuthentication(
            BasicAuthentication(realm='cianet-middleware'),
            Authentication(),
            ApiKeyAuthentication())


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
        always_return_data = True
        filtering = {
            "settopbox": ALL,
            "channel": ALL
        }
        validation = Validation()
        authorization = MyAuthorization()
        authentication = MultiAuthentication(
            BasicAuthentication(realm='cianet-middleware'),
            Authentication(),
            ApiKeyAuthentication())

    def obj_create(self, bundle, request=None, **kwargs):
        try:
            bundle = super(SetTopBoxChannelResource, self).obj_create(bundle,
                **kwargs)
        except IntegrityError:
            raise BadRequest('Duplicate entry for settopbox channel')
        return bundle

api = NamespacedApi(api_name='v1', urlconf_namespace='client')
api.register(SetTopBoxResource())
api.register(SetTopBoxParameterResource())
api.register(ChannelResource())
api.register(SetTopBoxChannelResource())
