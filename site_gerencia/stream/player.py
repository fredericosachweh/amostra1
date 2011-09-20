#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import subprocess
import os
import sys
import signal

"""
Usage: multicat [-i <RT priority>] [-t <ttl>] [-X] [-f] [-p <PCR PID>] [-s <chunks>] [-n <chunks>] [-k <start time>] [-d <duration>] [-a] [-r <file duration>] [-S <SSRC IP>] [-u] [-U] [-m <payload size>] [-c <remote socket>] [-N] <input item> <output item>
    item format: <file path | device path | FIFO path | directory path | network host>
    host format: [<connect addr>[:<connect port>]][@[<bind addr][:<bind port>]]
    -X: also pass-through all packets to stdout
    -f: output packets as fast as possible
    -p: overwrite or create RTP timestamps using PCR PID (MPEG-2/TS)
    -s: skip the first N chunks of payload [deprecated]
    -n: exit after playing N chunks of payload [deprecated]
    -k: start at the given position (in 27 MHz units, negative = from the end)
    -d: exit after definite time (in 27 MHz units)
    -a: append to existing destination file (risky)
    -r: in directory mode, rotate file after this duration (default: 97200000000 ticks = 1 hour)
    -S: overwrite or create RTP SSRC
    -u: source has no RTP header
    -U: destination has no RTP header
    -m: size of the payload chunk, excluding optional RTP header (default 1316)
    -c: unix local socket file to control the stream flow
    -N: don't remove stuffing (PID 0x1FFF) from stream
"""

def list_procs():
    # ps -eo pid,comm,args
    proc = subprocess.Popen(['ps','-eo','pid,comm,args'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout = proc.communicate()[0]
    ret = []
    for line in stdout.splitlines()[1:]:
        cmd = line.split()
        ret.append(
            {'pid':int(cmd[0]),'name':cmd[1],'command':' '.join(cmd[2:])}
            )
    return ret


class Player(object):
    '''
    Player para controle dos servidores de canais.
    Camada do servidor para controle dos processos de multicat
    '''

    def __init__(self):
        '''
        Constructor
        '''
        from django.conf import settings
        if settings.MULTICAST_APP:
            self._playerapp = settings.MULTICAST_COMMAND
        else:
            self._playerapp = 'multicat'
        self._player_name = settings.MULTICAST_APP
        

    def play_stream(self, stream):
        """
        Inicia um processo de multicat com o fluxo (stream)
        retorna pid
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
        # Retorna o pid na saída padrão
        #pid = int(subprocess.check_output(cmd))
        #
        #print(cmd)
        proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout,stderr = proc.communicate() 
        pid = int(stdout.strip())
        proc.stdout.close()
        proc.stderr.close()
        
        return pid
        
    def stop_stream(self,stream):
        if stream.pid:
            os.kill(stream.pid,signal.SIGKILL)
        return True
        
    
    def is_playing(self,stream):
        if stream.pid:
            for p in list_procs():
                if p['pid'] == stream.pid:
                    return True
            #return psutil.pid_exists(stream.pid)
        return False

    def list_running(self):
        lista = []
        for proc in list_procs():
            if proc['name'] == self._player_name:
                lista.append(proc)
        return lista

    def kill_all(self):
        for proc in self.list_running():
            #print('kill_all:: Matando:%d'%proc['pid'])
            os.kill(proc['pid'],signal.SIGKILL)



import re
r = re.compile('[0-9]{1,}')

def parse_dvb(stdout,debug=False):
    linhas = stdout.splitlines()
    res = []
    for linha in linhas:
        index = linha.find('* program number=')
        if index >= 0:
            prog, pid = r.findall(linha)
            res.append({'program':prog,'pid':pid}) 
        
        if debug: print ('L:%s'%linha);
    return res


class DVB(object):
    
    def scan_channels(self, dvbsource):
        """
        Inicia um processo de dvblast com o fluxo (stream)
        retorna pid
        """
        cmd = []
        dvb = '/usr/local/bin/dvblast'
        #dvb = '/usr/local/bin/fake_dvblast'
        cmd.append(dvb)
        cmd.append(u'-c /etc/dvblast/channels.d/%s.conf' %dvbsource.id)
        device = '%s'%dvbsource.device
        cmd.append(device)
        scmd = ' '.join(cmd)
        from easyprocess import Proc
        proc = Proc(scmd).call(timeout=8)
        #stdout=proc.stdout
        stdout=proc.stderr
        ret = parse_dvb(stdout,debug=True)
        if proc.is_alive():
            proc.stop()
        return ret
    
    def play_source(self,dvbsource):
        cmd = []
        dvb = '/usr/local/bin/dvblast'
        #dvb = '/usr/local/bin/fake_dvblast'
        cmd.append(dvb)
        cmd.append(u'-c /etc/dvblast/channels.d/%s.conf' %dvbsource.id)
        device = '%s'%dvbsource.device
        cmd.append(device)
        scmd = ' '.join(cmd)
        print(scmd)
        from easyprocess import Proc
        proc = Proc(scmd).start()
        pid_ret = proc.pid
        pid = os.fork()
        if pid == 0:
            proc.wait()
            #sys.exit(0)
        return pid_ret

    def stop_dvb(self,dvbsource):
        if dvbsource.pid:
            os.kill(dvbsource.pid,signal.SIGKILL)
        return True
         
        
    

