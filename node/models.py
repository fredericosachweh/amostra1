# -*- encoding:utf-8 -*-

from django.db import models
from django.conf import settings
from device.models import DeviceServer


class Node(DeviceServer):
    bind_addr = models.CharField(max_length=100, blank=True, null=True)
    config_file = models.CharField(max_length=100, blank=True, null=True)
    middleware_addr = models.CharField(max_length=100, blank=True, null=True) 
   
    class Meta:
        verbose_name = (u'Aplicativo NodeJS')
        verbose_name_plural = (u'Aplicativos NodeJS')
    
    def start(self, *args, **kwargs):
        cmd = '/usr/local/bin/node %s ' % settings.NODE_COMMAND
        
        if (self.bind_addr):
            cmd + '--bind %s ' % self.bind_addr
        
        if (self.config_file):
            cmd + '--config %s ' % self.config_file
            
        if (self.middleware_addr):
            cmd + '--middleware %s ' % self.middleware_addr

        self.server.execute_daemon(cmd, settings.NODE_LOGS_DIR)