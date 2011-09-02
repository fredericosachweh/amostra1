#!/usr/bin/env python
#coding:utf8

from django.db                import models
from fields                   import MACAddressField
from django.utils.translation import ugettext as _

from lib.pushstream.pushstream import PushStream

import urllib2

class Pessoa(models.Model):
    """ Modelo que define a pessoa responsável por um setup box? """
    nome = models.CharField(_('Nome'), 
                            max_length = 200)

################################################################################
# PushServer                                                                   #
################################################################################

class PushServer(models.Model):
    """ Modelo que persiste dados do Http-Push-Stream server """
    schema = models.CharField(_(u'Protocolo'), 
                              max_length = 5, 
                              default = 'http', 
                              blank = False)
    address = models.CharField(_(u'Endereço do servidor'), 
                               max_length = 255, 
                               unique = True)
    port = models.IntegerField(_(u'Porta'), 
                               default = 80)
    broadcast_channel = models.CharField(_(u'Canal de Broadcast'), 
                                         default = 'broadcast', 
                                         max_length = 40, 
                                         blank = False)
    hostname = models.CharField(_(u'Nome do servidor'), 
                                max_length = 255, 
                                editable = False)
    publisher_link = models.CharField(_(u'Link do Publicador'), 
                                      max_length = 20, 
                                      default = '/pub?id=', 
                                      blank = False)
    subscriber_link = models.CharField(_(u'Link de Inscrição'), 
                                       max_length = 20, 
                                       default = '/sub', 
                                       blank = False)
    #time = models.DateTimeField(_('Time'))
    channels = models.IntegerField(_(u'Canais'), 
                                   default = 0, 
                                   editable = False)
    broadcast_channels = models.IntegerField(_(u'Broadcast Channels'), 
                                             default = 0, 
                                             editable = False)
    subscribers = models.IntegerField(_(u'Subscribers'), 
                                      default = 0, 
                                      editable = False)
    published_messages = models.IntegerField(_(u'Published Messages'), 
                                             default = 0, 
                                             editable = False)
    online = models.BooleanField(_(u'Online'), 
                                 default = False, 
                                 editable = False)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)
    updated = models.DateTimeField(_(u"Atualizado em"), 
                                   auto_now = True, 
                                   editable = False)
    def __unicode__(self):
        return u'%s://%s:%d (%s) [%d/%d/%d/%d]' % (self.schema, 
                                                   self.address, 
                                                   self.port, 
                                                   self.hostname, 
                                                   self.channels, 
                                                   self.broadcast_channels, 
                                                   self.subscribers, 
                                                   self.published_messages)
    def url(self, *args):
        if args[0] == 'pub':
            return u'%s://%s:%d%s' % (self.schema, 
                                      self.address, 
                                      self.port, 
                                      self.publisher_link)
        if args[0] == 'sub':
            return u'%s://%s:%d%s' % (self.schema, 
                                      self.address, 
                                      self.port, 
                                      self.subscriber_link)
        return u'%s://%s:%d' % (self.schema, self.address, self.port)
    def setupboxes(self):
        setupboxes = SetupBox.objects.filter(pushserver = self.pk).count()
        return setupboxes
    class Meta:
        verbose_name        = _(u"Push Server")
        verbose_name_plural = _(u"Push Servers")
        ordering            = ['-channels', '-subscribers']
    
    @staticmethod
    def _post_init(signal, instance, sender, **kwargs):
        """ Adiciona lista de SetupBox ao PushServer, verificando pelo json do 
        push_stream """
        if not instance.pk or not instance.port or not instance.address: return
        pushserver = PushStream()
        try:
            pushserver.connect(port = instance.port, hostname = instance.address)
            instance.broadcast_channels = pushserver.data.broadcast_channels
            instance.channels           = pushserver.data.channels
            instance.hostname           = pushserver.data.hostname
            instance.published_messages = pushserver.data.published_messages
            instance.stored_messages    = pushserver.data.stored_messages
            instance.subscribers        = pushserver.data.subscribers
            instance.online             = True
            for channel in pushserver.data.channels_list:
                try:
                    #instance.setupbox_set.create(mac = channel)
                    setupbox = SetupBox(
                        pushserver = instance,
                        mac = channel)
                    setupbox.clean_fields()
                    setupbox.save()
                except: print "Falhou ao criar (provavelmente já existe): "+channel
        except: 
            instance.online = False
        instance.save()
        print "PushServer post_init signal executed."

models.signals.post_init.connect(PushServer._post_init, 
    sender = PushServer,
    dispatch_uid = "PushServer._post_init")

class PushServerCommands(models.Model):
    """ Modelo que armazena comandos enviados para canal de broadcast de um
    PushServer (deverá ser enviado a todos setupbox que estiverem online) """
    pushserver = models.ForeignKey(PushServer)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)
    updated = models.DateTimeField(_(u"Atualizado em"), 
                                   auto_now = True, 
                                   editable = False)
    command = models.TextField(_(u"Comando"), 
                               blank = False)
    response = models.TextField(_(u"Resposta"), 
                                blank = True,
                                editable = False)
    sended = models.BooleanField(_(u"Enviado"), 
                                 default = False,
                                 editable = False)
    ping = models.BooleanField(_(u"Solicitar retorno (ping)"), 
                               default = False)

################################################################################
# SetupBox                                                                     #
################################################################################

class SetupBox(models.Model):
    """ Modelo do SetupBox, filho do PushServer """
    pushserver = models.ForeignKey(PushServer)
    mac = MACAddressField(_(u'MAC Address'),
                          blank = False,
                          unique = True)
    connected = models.BooleanField(_(u'Connected'),
                                    default = False,
                                    editable = False)
    enabled = models.BooleanField(_(u'Enabled'),
                                  default  = False)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)
    updated = models.DateTimeField(_(u"Atualizado em"), 
                                   auto_now = True, 
                                   editable = False)
    def __unicode__(self):
        return self.mac
    class Meta:
        verbose_name        = _("SetupBox")
        verbose_name_plural = _("SetupBoxes")
        ordering            = ['-enabled', '-connected', 'mac']
        
    @staticmethod
    def _post_init(signal, instance, sender, **kwargs):
        """ Atualiza status de conexão do setupbox na instancia, se for 
        diferefente o status ele salva """
        if not instance.mac: return
        pushserver = PushStream()
        try:
            pushserver.connect(port = instance.pushserver.port, 
                               hostname = instance.pushserver.address)
            channel = pushserver.data.channels_list[instance.mac]
            instance.connected = bool(channel.subscribers) 
        except:
            instance.connected = False
        try:
            instance.clean_fields()
            instance.save()
        except: pass
        
        print "SetupBox post_init signal executed."
models.signals.post_init.connect(SetupBox._post_init, 
    sender = SetupBox,
    dispatch_uid = "SetupBox._post_init")

class SetupBoxCommands(models.Model):
    """ Modelo que armazena comandos enviados para cada setupbox """
    setupbox = models.ForeignKey(SetupBox)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)
    command = models.TextField(_(u"Comando"), 
                               blank = False)
    response = models.TextField(_(u"Resposta"), 
                                blank = True,
                                editable = False)
    sended = models.BooleanField(_(u"Enviado"), 
                                  default = False,
                                  editable = False)
    ping = models.BooleanField(_(u"Solicitar retorno (ping)"), 
                               default = False)

class SetupBoxCommandsResponse(models.Model):
    """ Modelo que armazena respostas do setupbox quando habilitado ping no
    modelo SetupBoxCommands. """
    setupboxcommands = models.ForeignKey(SetupBoxCommands)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)
    server_release = models.DateTimeField(_(u"Momento que servidor disparou"),
                                          editable = False)
    response_message = models.TextField(_(u"Mensagem na resposta"), 
                                        blank = True,
                                        editable = False)
    def server_delay(self):
        return (self.server_release - self.setupboxcommands.created)
    
    def setupbox_delay(self):
        return (self.created - self.server_release)
    
    def total_delay(self):
        return (self.setupboxcommands.created - self.created)

################################################################################
# PushServer + SetupBox                                                        #
################################################################################

class PushServerCommandsSetupBox(models.Model):
    """ Modelo que armazena referencia dos setupboxes que estavam conectados na
    hora do envio de um comando em broadcast pelo PushServer """
    pushservercommands = models.ForeignKey(PushServerCommands)
    setupbox = models.ForeignKey(SetupBox)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)

class PushServerCommandsResponse(models.Model):
    """ Modelo que armazena respostas do setupbox quando habilitado ping no
    modelo PushServerCommands. """
    pushservercommands = models.ForeignKey(PushServerCommands)
    setupbox = models.ForeignKey(SetupBox)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)
    server_release = models.DateTimeField(_(u"Momento que servidor disparou"),
                                          editable = False)
    response_message = models.TextField(_(u"Mensagem na resposta"), 
                                        blank = True,
                                        editable = False)
    def server_delay(self):
        return (self.server_release - self.setupboxcommands.created)
    
    def setupbox_delay(self):
        return (self.created - self.server_release)
    
    def total_delay(self):
        return (self.setupboxcommands.created - self.created)

def _pre_save_push_server_command(signal, instance, sender, **kwargs):
    """ Antes de salvar na base de dados, executa requisição na URL de
    publicação do PushServer referente ao setupbox"""
    if isinstance(instance, SetupBoxCommands):
        url = instance.setupbox.pushserver.url('pub')
        channel = instance.setupbox.mac
    else:
        url = instance.pushserver.url('pub')
        channel = instance.pushserver.broadcast_channel
        for setupbox in SetupBox.objects.filter(pushserver = instance.pushserver,
                                                connected = True):
            online = PushServerCommandsSetupBox(pushservercommands = instance.pushserver,
                                                setupbox = setupbox)
            online.save()
    url += channel
    
    command = ''
    if isinstance(instance, SetupBoxCommands) and instance.ping:
        command += "r();"
    command += instance.command
    
    try:
        request  = urllib2.Request(url, command)
        response = urllib2.urlopen(request)
        instance.sended = True
        content  = response.read()
        instance.response = content
        print u"Enviado comando pro canal [%s]: \n" \
            "Request: \n" \
            "%s \n" \
            "==========================================\n" \
            "Response Content:\n" \
            "%s" % (
              channel, command, content)
    except:
        instance.sended = False

models.signals.pre_save.connect(_pre_save_push_server_command, 
    sender = SetupBoxCommands)
models.signals.pre_save.connect(_pre_save_push_server_command, 
    sender = PushServerCommands)