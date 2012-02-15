"""Friendly Python SSH2 interface."""

import os
import tempfile
import paramiko

class Connection(object):
    """Connects and logs into the specified hostname. 
    Arguments that are not given are guessed from the environment.""" 

    def __init__(self,
                 host,
                 username = None,
                 private_key = None,
                 password = None,
                 port = 22,
                 ):
        self._sftp_live = False
        self._sftp = None
        self._transport_live = False
        if not username:
            username = os.environ['LOGNAME']

        # Log to a temporary file.
        templog = tempfile.mkstemp('.txt', 'ssh-')[1]
        paramiko.util.log_to_file(templog)

        # Begin the SSH transport.
        self._transport = paramiko.Transport((host, port))
        #self._transport.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._transport_live = True
        # Authenticate the transport.
        if password:
            # Using Password.
            self._transport.connect(username = username, password = password )
        else:
            # Use Private Key.
            if not private_key:
                # Try to use default key.
                if os.path.exists(os.path.expanduser('~/.ssh/id_rsa')):
                    private_key = '~/.ssh/id_rsa'
                elif os.path.exists(os.path.expanduser('~/.ssh/id_dsa')):
                    private_key = '~/.ssh/id_dsa'
                else:
                    raise TypeError, "You have not specified a password or key."
            private_key_file = os.path.expanduser(private_key)
            rsa_key = paramiko.RSAKey.from_private_key_file(private_key_file)
            self._transport.connect(username = username, pkey = rsa_key)#password=password, 
    
    def _sftp_connect(self):
        """Establish the SFTP connection."""
        if not self._sftp_live:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            self._sftp_live = True

    def get(self, remotepath, localpath = None):
        """Copies a file between the remote host and the local host."""
        if not localpath:
            localpath = os.path.split(remotepath)[1]
        self._sftp_connect()
        self._sftp.get(remotepath, localpath)

    def put(self, localpath, remotepath = None):
        """Copies a file between the local host and the remote host."""
        if not remotepath:
            remotepath = os.path.split(localpath)[1]
        self._sftp_connect()
        self._sftp.put(localpath, remotepath)

    def execute(self, command):
        """Execute the given commands on a remote machine."""
        channel = self._transport.open_session()
        channel.exec_command(command)
        output = channel.makefile('rb', -1).readlines()
        if output:
            return output
        else:
            return channel.makefile_stderr('rb', -1).readlines()
    
    def new_execute(self,command):
        import sys
        import socket
        channel = self._transport.open_session()
        channel.settimeout(2)
        channel.exec_command(command)
        stderr = channel.makefile_stderr()
        resp = ''
        for t in range(200):
            #sys.stdout.write(stderr.read(1))
            try:
                ## Neste ponto ocorre erro na rede ou timeout
                linha = stderr.readlines(1)
            except socket.timeout:
                sys.stdout.write('ERROR: >>>%s\n' %t)
                sys.stdout.write('ERROR: timeout? >>>%s\n' %socket.timeout)
                sys.stdout.flush()
                channel.send_exit_status(9)
                channel.close()
                return resp
            if linha:
                resp += linha[0]
                #sys.stdout.write('>>>%s\n' %linha)
            #sys.stdout.write('O[%s]' %channel.recv(1))
            if t == 200:
                sys.stdout.write('Saindo com 9')
                channel.send_exit_status(9)
                channel.close()
            sys.stdout.flush()
            #print(channel.recv(1))
        return resp
        

    def close(self):
        """Closes the connection and cleans up."""
        # Close SFTP Connection.
        if self._sftp_live:
            self._sftp.close()
            self._sftp_live = False
        # Close the SSH Transport.
        if self._transport_live:
            self._transport.close()
            self._transport_live = False

    def __del__(self):
        """Attempt to clean up if not explicitly closed."""
        self.close()
    
    def genKey(self):
        return paramiko.RSAKey.generate(2048)
    

def main():
    """Little test when called directly."""
    # Set these to your own details.
    myssh = Connection('example.com')
    myssh.put('ssh.py')
    myssh.close()

# start the ball rolling.
if __name__ == "__main__":
    main()