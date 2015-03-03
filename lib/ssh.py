#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""Friendly Python SSH2 interface."""
from __future__ import unicode_literals
import os
import logging
import paramiko
import time
import subprocess
import shlex
import re


def connect(host,
            username=None,
            private_key=None,
            password=None,
            port=22,
            ):
        log = logging.getLogger('device.remotecall')
        if not username:
            username = os.environ['LOGNAME']
        cmd = "ssh %s@%s -p %s" % (username, host, port)

        # Complete command according to variables received
        if password:
            # Using Password.
            log.info('Connection using password')
            cmd += ' -P %s' % (password)
        elif private_key:
            # Use Private Key.
            log.info('Connection using rsa key')
            cmd += ' -i %s' % (private_key)
        else:
            log.error('Need password or key to connect')
            raise "You have not specified a password or key."

        # Spawn new connection
        log.debug('Connecting ssh using %s', cmd)
        try:
            null = open('/dev/null', 'w')
            subprocess.call(shlex.split(cmd), stdin=subprocess.PIPE, stdout=null, stderr=null)
            null.close()
        except Exception as e:
            log.debug('Disconneting ssh from %s, cause=', cmd, e)

def get(host, username, remotepath, localpath=None, port=22):
        """Copies a file between the remote host and the local host."""
        log = logging.getLogger('device.remotecall')
        log.info('geting file from remote:%s -> %s', remotepath, localpath)
        if not localpath:
            localpath = os.path.split(remotepath)[1]
        cmd = 'scp -P '+str(port)+' '+username+'@'+host+':'+remotepath+' '+localpath
        try:
            null = open('/dev/null', 'w')        
            subprocess.call(shlex.split(cmd), stdin=subprocess.PIPE, stdout=null, stderr=null)
            null.close()
        except Exception as e:
            log.debug('Could not retrieve %s file from %s: Error %s', remotepath, host, e)

def put(host, username, localpath, remotepath=None, port=22):
        """Copies a file between the local host and the remote host."""
        log = logging.getLogger('device.remotecall')
        log.info('sending file from local:%s -> %s', localpath, remotepath)
        if not remotepath:
            remotepath = os.path.split(localpath)[1]
        cmd = 'scp -P '+str(port)+' '+localpath+' '+username+'@'+host+':'+remotepath
        try:
            null = open('/dev/null', 'w')
            subprocess.call(shlex.split(cmd), stdin=subprocess.PIPE, stdout=null, stderr=null)
            null.close()
        except Exception as e:
            log.debug('Could not send %s file to %s: Error %s', localpath, host, e)

def execute(host, username, command, port=22):
        """Execute the given commands on a remote machine."""
        log = logging.getLogger('device.remotecall')
        ret = {}
        """Executar comando com a opcao de echo $? no final para
           descobrir o valor do retorno da execucao do comando"""
        cmd = 'ssh -p '+str(port)+' '+username+'@'+host+' \"'+command+'\" \; echo $?'
        log.info('COMMAND=%s', cmd)
        try:
            out = subprocess.check_output(shlex.split(cmd))
            """Necessario separar as linhas em lista, por causa
               da compatilidade com a implementacao ssh anterior"""
            out = out.splitlines(True)
            """Descartar ultima linha por causa da quebra de linha
               do valor de retorno"""
            ret['output'] = out[:-1]
            ret['exit_code'] = int(out[-1])
        except subprocess.CalledProcessError as e:
            ret['output'] = e.output
            ret['exit_code'] = int(e.returncode)
        """Forcar codificacao da string"""
        ret['output'] = map(lambda x: unicode(x, 'utf-8'), ret['output'])           
        log.info('Return status [%s] command:%s', ret['exit_code'], command)

        return ret

def execute_daemon(host, username, command, log_path=None, port=22):
        """
        Executa o comando em daemon e retorna o pid do processo
        Ex.:
            /usr/sbin/daemonize -p
            /home/helber/vlc.pid -o
            /home/helber/vlc.o -e
            /home/helber/vlc.e
            /usr/bin/cvlc -I dummy -v -R
            /home/videos/Novos/red_ridding_hood_4M.ts
            --sout "#std{access=udp,mux=ts,dst=192.168.0.244:5000}"
        """
        log = logging.getLogger('device.remotecall')
        ret = execute(host, username, '/bin/mktemp')
        pidfile_path = ret['output'][0].strip()
        fullcommand = '/usr/sbin/daemonize -p %s ' % pidfile_path
        if log_path:
            fullcommand += '-o %s.out -e %s.err ' % (log_path, log_path)
        fullcommand += '%s' % command.strip()
        ret = execute(host, username, fullcommand)
        pidcommand = "/bin/cat %s" % pidfile_path
        ## Buscando o pid
        output = execute(host, username, pidcommand)
        ## unlink pidfile
        unlink_cmd = '/usr/bin/unlink %s' % pidfile_path
        log.debug('Clean pid file:%s', unlink_cmd)
        execute(host, username, unlink_cmd, port=port)
        if len(output['output']):
            pid = int(output['output'][0].strip())
            log.info('Daemon started with pid [%d] command:%s', pid,
                fullcommand)
            ret['pid'] = pid
        return ret

def close(self):
        """Closes the connection and cleans up."""
        if logging is not None:
            log = logging.getLogger('device.remotecall')
        # Close SFTP Connection.
        #if self._sftp_live:
        #    self._sftp.close()
        #    self._sftp_live = False
        #    if logging is not None:
        #        log.debug('close sftp')
        # Close the SSH Transport.
        #if self._transport_live:
        #    self._transport.close()
        #    self._transport_live = False
        #    if logging is not None:
        #        log.debug('close ssh')

def __del__(self):
        """Attempt to clean up if not explicitly closed."""
        if logging is not None:
            pass
            #log = logging.getLogger('device.remotecall')
            #log.debug('__DEL__:%s', self)
        self.close()

def genKey(self):
        log = logging.getLogger('device.remotecall')
        log.debug('genKey')
        return paramiko.RSAKey.generate(2048)


def main():
    """Little test when called directly."""
    # Set these to your own details.
    myssh = connect('example.com')
    myssh.put('ssh.py')
    myssh.close()

# start the ball rolling.
if __name__ == "__main__":
    main()
