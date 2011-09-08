#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import psutil
import subprocess
import os
import sys

## Pacote: python-psutil.x86_64
#import psutil
#for proc in psutil.process_iter():
#    if proc.name == 'multicat':
#        print(proc)
#        print(proc.pid)
#        print(proc.name)
#        proc.kill()


"""
Usage: multicat [-i <RT priority>] [-t <ttl>] [-p <PCR PID>] [-s <chunks>] [-n <chunks>] [-d <time>] [-a] [-S <SSRC IP>] [-u] [-U] [-N] [-m <payload size>] [-R <rotate_time>] [-P <port number>] <input item> <output item>
    item format: <file path | device path | FIFO path | network host>
    host format: [<connect addr>[:<connect port>]][@[<bind addr][:<bind port>]]
    -p: overwrite or create RTP timestamps using PCR PID (MPEG-2/TS)
    -s: skip the first N chunks of payload
    -n: exit after playing N chunks of payload
    -d: exit after definite time (in 27 MHz units)
    -a: append to existing destination file (risky)
    -S: overwrite or create RTP SSRC
    -u: source has no RTP header
    -U: destination has no RTP header
    -m: size of the payload chunk, excluding optional RTP header (default 1316)
    -N: don't remove stuffing (PID 0x1FFF) from stream
    -R: Rotate the output file every <rotate_time> (in seconds)
    -P: Port number to server recovery packets
"""

class Player(object):
    '''
    Player para controle dos servidores de canais
    '''
    _lista = []

    def __init__(self):
        '''
        Constructor
        '''
        from django.conf import settings
        if settings.MULTICAST_APP:
            self._playerapp = settings.MULTICAST_APP
        else:
            self._playerapp = 'multicat'

    def play(self,origem_ip=None,origem_porta=None,destino_ip=None,destino_porta=None,porta_recuperacao=None):
        '''
        Executa o servidor de canal:
        multicat -P porta_recuperacao -u -U @origem_ip:origem_porta destino_ip:destino_porta@ip_bind:port_bind
        multicat -P 10003 -U -u @224.0.1.1:10000 224.0.0.13:11003
        multicat -P 10003 -U -u @224.0.1.1:10000@172.16.0.1 224.0.0.13:11003@192.168.0.1
        '''
        cmd = []
        cmd.append(self._playerapp)
        if porta_recuperacao is not None:
            rec = '-P %d' %porta_recuperacao
            cmd.append(rec)
        cmd.append('-u')
        cmd.append('-U')
        origem = '@%s:%s' %(origem_ip,origem_porta)
        destino = '%s:%s' %(destino_ip,destino_porta)
        cmd.append(origem)
        cmd.append(destino)
        #proc = psutil.Popen(cmd)
        proc = subprocess.Popen(cmd)
        #proc = Popen(cmd)
        return proc
    
    def play_stream(self, stream):
        """
        Inicia um processo de multicat com o fluxo informado
        """
        cmd = []
        cmd.append(self._playerapp)
        if stream.source.is_rtp is False:
            cmd.append('-u')
        if stream.destination.is_rtp is False:
            cmd.append('-U')
        origem = '@%s:%s' %(stream.source.ip,stream.source.port)
        destino = '%s:%s' %(stream.destination.ip,stream.destination.port)
        cmd.append(origem)
        cmd.append(destino)
        
        #cmd.append('&')
        #print('On:Player.play_stream=%s | %s'%(stream,' '.join(cmd)))
        #stdout=subprocess.PIPE, stderr=subprocess.PIPE
        #proc = psutil.Popen(cmd)
        #proc = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE,shell=False)
        
        #print('On:Player.play_stream=%s | %s'%(stream,' '.join(cmd)))
        
        #proc = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE,shell=False)
        #pid = proc.communicate()
        #pid = proc.communicate()[0]
        #pid = proc.stdout.read()
        
        pid = subprocess.check_output(cmd)
        #print('pid:%s'%pid)
        stream.pid = pid
        stream.save()
        #proc.wait()
        return True
        
        #print('Antes p0:%d'%os.getpid())
        #p0 = os.fork()
        #if p0 == 0:
        #    ### Primeiro filho
        #    #print('Antes p1:%d'%os.getpid())
        #    p1 = os.fork()
        #    if p1 == 0:
        #        ### Segundo filho
        #        #proc = subprocess.Popen(cmd,close_fds=True,shell=False,cwd='/tmp')
        #        proc = subprocess.Popen(cmd)
        #        if proc.pid > 0:
        #            stream.pid = proc.pid
        #            stream.save()
        #        proc.wait()
        #        #print('Saindo proc :%d'%os.getpid())
        #        sys.exit(0)
        #        #os._exit(0)
        #    #print('Saindo p0:%d'%os.getpid())
        #    #sys.exit(0)
        #    os._exit(0)
        #print('Continuando:%d'%os.getpid())
        
        #print('Iniciado')
        #print(self._lista)
        #return proc
    
    def stop_stream(self,stream):
        #print(self._lista)
        #for proc in self._lista:
        #    if stream.pid == proc.pid:
        #        proc.kill()
        #        proc.wait()
        #        self._lista.remove(proc)
        #print('parado:%s'%stream)
        #print(self._lista)
                
        #return True
        #print('parado:%s'%stream)
        if stream.pid:
            proc = psutil.Process(stream.pid)
            proc.kill()
            proc = None
            #proc.wait(1)
        return True
        
    
    def is_playing(self,stream):
        #for proc in self._lista:
        #    if stream.pid == proc.pid:
        #        return True
        #return False
        if stream.pid:
            return psutil.pid_exists(stream.pid)
        return False

    def list_running(self):
        #return self._lista
        lista = []
        for proc in psutil.process_iter():
            if proc.name == self._playerapp:
                lista.append(proc)
        return lista

    def kill_all(self):
        #for proc in self._lista:
        #    proc.kill()
        #    proc.wait()
        #    self._lista.remove(proc)
        for proc in psutil.process_iter():
            if proc.name == self._playerapp:
                #print("Proc: %s" %proc)
                #print("Matando: Nome:%s PID: %s" %(proc.name,proc.pid))
                proc.kill()
