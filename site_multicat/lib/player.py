#!/usr/bin/env python
# -*- encoding:utf-8 -*-

#import subprocess
from subprocess import Popen


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
    _running = []

    def __init__(self):
        '''
        Constructor
        '''
        pass

    def play(self,origem_ip=None,origem_porta=None,destino_ip=None,destino_porta=None,porta_recuperacao=None):
        '''
        Executa o servidor de canal:
        multicat -P porta_recuperacao @origem_ip:origem_porta destino_ip:destino_porta@ip_interface_destino
        multicat -P 10003 -U -u @224.0.1.1:10000 224.0.0.13:11003
        multicat -P 10003 -U -u @224.0.1.1:10000 224.0.0.13:11003@192.168.0.1
        '''
        cmd = ['multicat']
        if porta_recuperacao is not None:
            rec = '-P %d' %porta_recuperacao
            cmd.append(rec)
        cmd.append('-u')
        cmd.append('-U')
        origem = '@%s:%s' %(origem_ip,origem_porta)
        destino = '%s:%s' %(destino_ip,destino_porta)
        cmd.append(origem)
        cmd.append(destino)
        proc = Popen(cmd)
        self._running.append(proc)
        return proc

    def list_running(self):
        for proc in self._running:
            print("PID:%d",proc.pid)

    def kill_all(self):
        for proc in self._running:
            print("KILL PID:%d",proc.pid)
            proc.kill()
