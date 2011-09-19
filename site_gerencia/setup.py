from setuptools import setup

setup(
    name='IPTV Site Gerência',
    version='0.1',
    description='Gerenciador de recursos e setupboxes',
    author='Helber Maciel Guerra, Gabriel Reitz Giannattasio',
    author_email='helber@cianet.ind.br, gartz@cianet.ind.br',
    url='http://cianet.ind.br',
    
    scripts = ['manager.py'],
    
    install_requires = ['enum>=0.4.4',
                        'simplejson'
                        'django>=1.3'
                        'debug_toolbar'],
)