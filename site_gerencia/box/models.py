#!/usr/bin/env python
#coding:utf8

from django.db                import models
from fields                   import MACAddressField
from django.utils.translation import ugettext as _



class SetupBox(models.Model):
    """
    Modelo que define campos, propriedades e comportamento do SetupBox
    """
    mac = MACAddressField(_(u'Endereço MAC'), blank = False, unique = True)
    status = models.SmallIntegerField(blank    = True, 
                                      default  = 0, 
                                      editable = False)
    enabled = models.BooleanField(default = False)
    def status_name(self):
        """
        Exibe texto referente ao ID do status atual
        """
        if self.status == 0:
            return "Inoperante"
        else:
            return "Positivo e operante"
    def __unicode__(self):
        return self.mac
    class Meta:
        verbose_name        = "SetupBox"
        verbose_name_plural = "SetupBoxes"
        ordering            = ['-enabled', '-status', 'mac']


class Pessoa(models.Model):
    """
    Modelo que define a pessoa responsável por um setup box?
    """
    nome = models.CharField(_('Nome'), max_length = 200)




