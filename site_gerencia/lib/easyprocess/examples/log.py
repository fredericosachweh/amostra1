import os,sys
sys.path.append(os.path.abspath('../../'))

from .. import EasyProcess
import logging

# turn on logging
logging.basicConfig(level=logging.DEBUG)

EasyProcess('python --version').call()
EasyProcess('ping localhost').start().sleep(1).stop()
EasyProcess('python --version').check()
try:
    EasyProcess('bad_command').check()
except Exception, detail:
    print  detail

try:
    EasyProcess('sh -c bad_command').check()
except Exception, detail:
    print  detail
