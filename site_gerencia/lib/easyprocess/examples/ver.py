import os,sys
sys.path.append(os.path.abspath('../../'))

from easyprocess import EasyProcess

v = EasyProcess('python --version').call().stderr
print 'your python version:', v

