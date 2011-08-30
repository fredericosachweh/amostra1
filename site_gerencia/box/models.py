#!/usr/bin/env python
#coding:utf8

from django.db                import models
from fields                   import MACAddressField
from django.utils.translation import ugettext as _

from lib.pushstream.pushstream import PushStream
from dbus.decorators import signal

class Pessoa(models.Model):
    """
    Modelo que define a pessoa responsável por um setup box?
    """
    nome = models.CharField(_('Nome'), max_length = 200)


class PushServer(models.Model):
    """ Modelo que persiste dados do Http-Push-Stream server """
    schema = models.CharField(_(u'Protocolo'), max_length = 5, default = 'http', blank = False)
    address = models.CharField(_(u'Endereço do servidor'), max_length = 255, unique = True)
    port = models.IntegerField(_(u'Porta'), default  = 80)
    hostname = models.CharField(_(u'Nome do servidor'), max_length = 255, editable = False)
    #time = models.DateTimeField(_('Time'))
    channels = models.IntegerField(_(u'Canais'), default  = 0, editable = False)
    broadcast_channels = models.IntegerField(_(u'Broadcast Channels'), default  = 0, editable = False)
    subscribers = models.IntegerField(_(u'Subscribers'), default  = 0, editable = False)
    published_messages = models.IntegerField(_(u'Published Messages'), default  = 0, editable = False)
    online = models.BooleanField(_(u'Online'), default = False, editable = False)
    created = models.DateTimeField(_(u"Criado em"), auto_now_add = True, editable = False )
    updated = models.DateTimeField(_(u"Atualizado em"), auto_now = True, editable = False)
    def __unicode__(self):
        return u'%s://%s:%d (%s) [%d/%d/%d/%d]' % (self.schema, self.address, self.port, self.hostname, self.channels, self.broadcast_channels, self.subscribers, self.published_messages)
    def url(self):
        return u'%s://%s:%d' % (self.schema, self.address, self.port)
    def setupboxes(self):
        setupboxes = SetupBox.objects.filter(pushserver = self.pk).count()
        return setupboxes
    # TODO: Sobrescrever método de leitura, para que ele leia o JSON e salve na base, 
    # caso não seja possível, tem que apenas ler o último registro
    class Meta:
        verbose_name        = _(u"Push Server")
        verbose_name_plural = _(u"Push Servers")
        ordering            = ['-channels', '-subscribers']
    
    @staticmethod
    def _post_init(signal, instance, sender, **kwargs):
        """
        Adiciona lista de SetupBox ao PushServer, verificando pelo json do push_stream
        """
        if not instance.pk and not instance.port and not instance.address: return
        pushserver = PushStream()
        try:
            pushserver.connect(port = instance.port, hostname = instance.address) # TODO puxar dados do model pai
            instance.broadcast_channels = pushserver.data.broadcast_channels
            instance.channels = pushserver.data.channels
            instance.hostname = pushserver.data.hostname
            instance.published_messages = pushserver.data.published_messages
            instance.stored_messages = pushserver.data.stored_messages
            instance.subscribers = pushserver.data.subscribers
            instance.online = True
            for channel in pushserver.data.channels_list:
                try:
                    instance.setupbox_set.create(mac = channel)
                except: print "Falhou ao criar (provavelmente já existe): "+channel
        except: 
            instance.online = False
        instance.save()
        print "PushServer post_init signal executed."


models.signals.post_init.connect(PushServer._post_init, 
    sender = PushServer,
    dispatch_uid = "PushServer._post_init")

class SetupBox(models.Model):
    """
    Modelo do SetupBox, filho do PushServer
    """
    pushserver  = models.ForeignKey(PushServer)
    mac         = MACAddressField(_(u'MAC Address'),   blank    = False, unique   = True)
    connected   = models.BooleanField(_(u'Connected'), default  = False, editable = False)
    enabled     = models.BooleanField(_(u'Enabled'),   default  = False)
    def __unicode__(self):
        return self.mac
    class Meta:
        verbose_name        = _("SetupBox")
        verbose_name_plural = _("SetupBoxes")
        ordering            = ['-enabled', '-connected', 'mac']
        
    @staticmethod
    def _post_init(signal, instance, sender, **kwargs):
        """
        Atualiza status de conexão do setupbox na instancia, se for diferefente o status ele salva
        """
        if not instance.mac: return
        pushserver = PushStream()
        try:
            pushserver.connect(port=8080) # TODO puxar dados do model pai
            instance.connected = bool(pushserver.data.channels_list[instance.mac])
        except:
            instance.connected = False
        instance.save()
        
        print "SetupBox post_init signal executed."
models.signals.post_init.connect(SetupBox._post_init, 
    sender = SetupBox,
    dispatch_uid = "SetupBox._post_init")




