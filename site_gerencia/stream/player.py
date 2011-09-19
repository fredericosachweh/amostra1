#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import subprocess
import os
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
    print(res)
    return res


#def timeout_command(command, timeout):
#    """call shell-command and either return its output or kill it
#    if it doesn't normally exit within timeout seconds and return None"""
#    import subprocess, datetime, os, time, signal
#    #cmd = command.split(" ")
#    cmd = command
#    start = datetime.datetime.now()
#    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    while process.poll() is None:
#        time.sleep(0.1)
#        now = datetime.datetime.now()
#        if (now - start).seconds > timeout:
#            os.kill(process.pid, signal.SIGKILL)
#            os.waitpid(-1, os.WNOHANG)
#            return None
#    return process.stdout.read()

class TimeoutInterrupt(Exception):
    pass

def timeout_command(cmdline, timeout=60):
    """
    Execute cmdline, limit execution time to 'timeout' seconds.
    Uses the subprocess module and subprocess.PIPE.
    
    Raises TimeoutInterrupt
    """
    import time
    bufsize = -1
    
    p = subprocess.Popen(
        cmdline,
        bufsize = bufsize,
        shell   = False,
        stdout  = subprocess.PIPE,
        stderr  = subprocess.PIPE
    )
    
    t_begin         = time.time()                         # Monitor execution time
    seconds_passed  = 0  
    
    out = ''
    err = ''
    
    while p.poll() is None and seconds_passed < timeout:  # Monitor process
        time.sleep(0.01)                                     # Wait a little
        #print('lendo')
        seconds_passed = time.time() - t_begin
        out += p.stdout.flush()
        out += p.stdout.read()
        #err += p.stderr.read(10)
    
        if seconds_passed >= timeout:
            try:
                p.stdout.close()  # If they are not closed the fds will hang around until
                p.stderr.close()  # os.fdlimit is exceeded and cause a nasty exception
                p.terminate()     # Important to close the fds prior to terminating the process!
                # NOTE: Are there any other "non-freed" resources?
            except:
                pass
            
            raise TimeoutInterrupt('Erro')
    
    returncode  = p.returncode
    
    return (returncode, err, out)




class DVB(object):
    
    def scan_channels(self, dvbsource):
        """
        Inicia um processo de dvblast com o fluxo (stream)
        retorna pid
        """
        import time
        import sys
        #import psutil
        cmd = []
        cmd.append('/usr/local/bin/fake_dvblast')
        cmd.append('-c /etc/dvblast/channels.d/1.conf')
        device = '%s'%dvbsource.device
        cmd.append(device)
        print('Comando:%s' %' '.join(cmd))
        #ret = timeout_command(cmd,2)
        #res = ret[2]
        
        proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        #proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
        t = 0
        l = ''
        res = ''
        while t<100:
            l = proc.stdout.readline()
            if l == '' and proc.poll() != None:
                break
            #if l.find('end NIT') >0:
            #    t=100
            #sys.stdout.flush()
            time.sleep(0.01)
            #print(t)
            t += 1
            res += l
        #print('Leu')
        #if proc.pid:
        proc.kill()
        ret = parse_dvb(res,debug=True)
        proc.stdout.close()
        proc.stderr.close()
        return ret



