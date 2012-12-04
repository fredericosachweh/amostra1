import os,sys
sys.path.append(os.path.abspath('../../'))

from .. import EasyProcess

v = EasyProcess('python --version').call().stderr
print 'your python version:', v

