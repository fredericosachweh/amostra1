#!/usr/bin/env python
# -*- encoding:utf8 -*-


from tastypie.authorization import DjangoAuthorization
from tastypie.api import NamespacedApi
from tastypie.resources import NamespacedModelResource
from tastypie import fields
import models


class SetTopBoxResource(NamespacedModelResource):

    class Meta:
        queryset = models.SetTopBox.objects.all()
        resource_name = 'settopbox'
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'


class SetTopBoxParameterResource(NamespacedModelResource):

    settopbox = fields.ForeignKey(SetTopBoxResource, 'settopbox', null=False)

    class Meta:
        queryset = models.SetTopBoxParameter.objects.all()
        resource_name = 'parameter'
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'


api = NamespacedApi(api_name='v1', urlconf_namespace='client')
api.register(SetTopBoxResource())
api.register(SetTopBoxParameterResource())
