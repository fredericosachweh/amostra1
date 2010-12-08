#!/usr/bin/env python
#coding:utf8

from django.db import models
from fields import MACAddressField
from django.utils.translation import ugettext as _






class SetupBox(models.Model):
    class Meta:
        verbose_name_plural = "SetupBox"
    mac = MACAddressField(_(u'Endereço MAC'),blank=False)




class Pessoa(models.Model):
    nome = models.CharField(_('Nome'),max_length=200)