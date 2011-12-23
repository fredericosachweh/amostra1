#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

class MediaMulticastSource(models.Model):
    class Meta:
        verbose_name = _(u'Origem de fluxo')
        verbose_name_plural = _(u'Origens de fluxo')
    name = models.CharField(_(u'Nome'),max_length=200)
    ip = models.IPAddressField(_(u'Endereço IP'))
    port = models.PositiveSmallIntegerField(_(u'Porta'))
    is_rtp = models.BooleanField(_(u'RTP'),default=False)
    def __unicode__(self):
        return '%s (%s:%s)' %(self.name,self.ip,self.port)

class MediaMulticastDestination(models.Model):
    class Meta:
        verbose_name = _(u'Destino de fluxo')
        verbose_name_plural = _(u'Destinos de fluxo')
    name = models.CharField(_(u'Nome'),max_length=200)
    ip = models.IPAddressField(_(u'Endereço IP'),blank=True)
    port = models.PositiveSmallIntegerField(_(u'Porta'),blank=True,null=True)
    ip_bind = models.IPAddressField(_(u'Endereço IP de conexão'),blank=True,null=True)
    port_bind = models.PositiveSmallIntegerField(_(u'Porta de conexão'),blank=True,null=True)
    is_rtp = models.BooleanField(_(u'RTP'),default=False)
    recovery_port = models.PositiveSmallIntegerField(_(u'Porta de recuperação de pacotes'),blank=True,null=True)
    def __unicode__(self):
        return '%s (%s:%d)' %(self.name,self.ip,self.port)

class MediaRecord(models.Model):
    class Meta:
        verbose_name = _(u'Destino de gravação')
        verbose_name_plural = _(u'Destino de Gravações')
    name = models.CharField(_(u'Nome'),max_length=200)
    rotate_time = models.PositiveIntegerField(_(u'Tempo de gravação em cada arquivo em segundos'))
    keep_time = models.PositiveSmallIntegerField(_(u'Dias que as gravações estarão disponíveis'))
    filename = models.CharField(_(u'Nome do arquivo'),max_length=200)
    def __unicode__(self):
        return self.name

class Record(models.Model):
    """
    Classe de gravação 
    """
    class Meta:
        verbose_name = _(u'Gravação')
        verbose_name_plural = _(u'Gravações')
    source = models.ForeignKey(MediaMulticastSource)
    filename = models.ForeignKey(MediaRecord)
    def play(self):
        pass
    def stop(self):
        pass

class Stream(models.Model):
    """
    Classe responsável pelo controle de fluxos multicast entre source (origem)
    e destination (destino)
    """
    class Meta:
        verbose_name = _(u'Fluxo')
        verbose_name_plural = _(u'Fluxos')
    source = models.ForeignKey(MediaMulticastSource)
    destination = models.ForeignKey(MediaMulticastDestination, unique=True)
    pid = models.PositiveSmallIntegerField(u'PID',blank=True,null=True)
    def status(self):
        from stream.player import Player
        p = Player()
        if p.is_playing(self) is True:
            url = reverse('stream.views.stop',kwargs={'streamid':self.id})
            return '<a href="%s" id="stream_id_%s" style="color:green;cursor:pointer;" >Rodando</a>' %(url,self.id)
        url = reverse('stream.views.play',kwargs={'streamid':self.id})
        return '<a href="%s" id="stream_id_%s" style="color:red;" >Parado</a>'%(url,self.id)
        #return '%s'%self.id
    status.allow_tags = True
    def __unicode__(self):
        return '%s %s:%d -> %s %s:%d' %(self.source.name,self.source.ip,self.source.port,self.destination.name,self.destination.ip,self.destination.port)
    def play(self):
        'Inicia o fluxo (inicia o processo do multicat)'
        from stream.player import Player
        p = Player()
        pid = p.play_stream(self)
        self.pid = pid
        self.save()
    def stop(self):
        'Para o fluxo (mata o processo do multicat)'
        from stream.player import Player
        p = Player()
        p.stop_stream(self)
        self.pid = None
        self.save()
    def autostart(self):
        if self.pid is not None:
            from stream.player import Player
            p = Player()
            if p.is_playing(self) is False:
                self.play()
        


class DVBSource(models.Model):
    ### alter table stream_dvbsource add hardware_id varchar (200);
    class Meta:
        verbose_name = _(u'Origem de fluxo DVB')
        verbose_name_plural = _(u'Origem de fluxo DVB')
    name = models.CharField(_(u'Nome'),max_length=200)
    #frequency = models.PositiveIntegerField(u'Frequencia de MHz')
    #symbol_rate = models.PositiveIntegerField(u'Taxa de Simbolos')
    device = models.CharField(u'Dispositivo',max_length=250,help_text='Ex.: -D @239.0.1.10:10000 | -f 3870000 -s 1280000')
    pid = models.PositiveSmallIntegerField(u'PID',blank=True,null=True)
    hardware_id = models.CharField(u'Identificação de hardware(MAC)',max_length=200,blank=True,null=True)
    def get_adapter_list(self):
        "Retorna a lista de adaptadores encontrados no SO"
        import os
        adapters = []
        if not os.path.exists('/dev/dvb'):
            return adapters
        for f in os.listdir('/dev/dvb'):
            if f.endswith('.mac'):
                adapter = int(f[7:-4])
                macfile = open('/dev/dvb/%s'%f,'r')
                mac = macfile.readline().strip()
                adapters.append((adapter,mac))
                macfile.close()
        #print(adapters)
        return adapters
    def get_adapter(self):
        "Retorna o numero do adaptador que coicide com o endereço mac cadastrado, caso contrario retorna -1"
        for adapter in self.get_adapter_list():
            if adapter[1] == self.hardware_id:
                return adapter[0]
        return -1
    def __unicode__(self):
        return '%s->%s' %(self.name,self.hardware_id)
    def status(self):
        from stream.player import Player
        p = Player()
        if p.is_playing(self) is True:
            url = reverse('stream.views.dvb_stop',kwargs={'streamid':self.id})
            return '<a href="%s" id="stream_id_%s" style="color:green;cursor:pointer;" >Rodando</a>' %(url,self.id)
        url = reverse('stream.views.dvb_play',kwargs={'streamid':self.id})
        return '<a href="%s" id="stream_id_%s" style="color:red;" >Parado</a>'%(url,self.id)
    status.allow_tags = True
    def record_config(self):
        dst = DVBDestination.objects.filter(source=self)
        # 224.0.0.17:10000/udp 1 1
        template = '%s:%d/udp 1 %d\n'
        cfg_file = '/etc/dvblast/channels.d/%s.conf' %self.id
        config = open(cfg_file,'w')
        cfg = []
        for destination in dst:
            linha = template%(destination.ip,destination.port,destination.channel_program)
            config.write(linha)
            cfg.append(linha)
        config.close()
        return True
    def scan_channels(self):
        from player import DVB
        d = DVB()
        return d.scan_channels(self)
    def play(self):
        from player import DVB
        d = DVB()
        pid = d.play_source(self)
        self.pid = pid
        self.save()
    def stop(self):
        from player import DVB
        d = DVB()
        d.stop_dvb(self)
        self.pid = None
        self.save()
    def autostart(self):
        if self.pid is not None:
            from player import DVB
            d = DVB()
            if d.is_playing(self) is False:
                self.play()


class DVBDestination(models.Model):
    class Meta:
        verbose_name = _(u'Destino de fluxo DVB')
        verbose_name_plural = _(u'Destinos de fluxo DVB')
    name = models.CharField(_(u'Nome'),max_length=200)
    ip = models.IPAddressField(_(u'Endereço IP'),blank=True)
    port = models.PositiveSmallIntegerField(_(u'Porta'),blank=True,null=True)
    channel_program = models.PositiveSmallIntegerField(u'Programa')
    channel_pid = models.PositiveSmallIntegerField(u'PID (Packet ID)')
    source = models.ForeignKey(DVBSource,related_name='origem')
    def __unicode__(self):
        return self.name




