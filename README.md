Site_gerencia
=============

Este documento contém as intruções necessárias para instalar e executar o site gerencia.

Projeto de aplicação de controle do IPTV, isso é, um middleware que comunica-se diretamento
com setupbox e outros servidores, a fins de intermediar a comunicação e controlar ela.

Armazena configurações e gerencia dados de cada setupbox na rede, faz sua validação.


Iniciando aplicação em Django
-----------------------------

Para iniciar em `modo de desenvolvimento standalone` para todos IPs na `porta 8000`
    ./manage.py runserver 0.0.0.0:8000

Para iniciar FastCGI para uso integrado com nginx, existem duas maneiras.

Desenvolvedor:

    python ./manage.py runfcgi daemonize=false socket=/tmp/site_gerencia.sock maxrequests=1 debug=true --verbosity=2 --traceback

Esta maneira ele vai iniciar, porém vai ficar atrelado ao bash, de forma que fica mais fácil depurar, o limite de request faz com que ele execute apenas página por vez, pra vc sempre saber o que está requisitando ou depurar a execução.

Produção:

    ./manage.py runfcgi socket=/var/run/site_gerencia.sock

Simplismente executa o sock no `/var/run/site_gerencia.sock` aponte seu nginx pra lá e deixe ele fazer o trabalho sujo.

Em todos modos apresentados, o django vai reiniciar o serviço automáticamente quando você alterar algo no código.

Cuidado, alterações que quebrem o processamento podem fazer o processamento parar se ele não for daemonizado.


Compilando o NGINX com PUSH-STREAM-MODULE
-----------------------------------------

Pré requisito para a instalação do nginx:

    sudo yum install pcre-devel

Compilar com nginx versão 1.0.14 (recomendado), todos os modulos padrões e + push-stream-module:

    ./build.sh master 1.0.14
    cd build/nginx-1.0.14
    sudo make install
    cd ../..
    sudo rm /usr/local/nginx/conf/nginx.conf
    sudo cp misc/cianet/nginx.conf /usr/local/nginx/conf/nginx.conf
    sudo mkdir /usr/local/nginx/conf/conf.d

Nginx será instalado no path `/usr/local/nginx`.

Configurando ambiente de desenvolvimento:

    sudo cp misc/cianet/conf.d/dev.virtual.conf /usr/local/nginx/conf/conf.d/dev.virtual.conf 

Configurando ambiente de produção:

    sudo cp misc/cianet/conf.d/virtual.conf /usr/local/nginx/conf/conf.d/virtual.conf 

Executando seu nginx

    sudo /usr/local/nginx/sbin/nginx



Testando serviço de push-stream
-------------------------------

Enviando comando para um canal de broadcast:

    curl -s -v -X POST "http://localhost:8080/pub?id=broadcast" -d 'alert("texto por cima de tudo")'

Connectando-se ao canal de broadcast:

    curl -s -v "http://localhost:8080/sub/broadcast"

Verificando status do servidor em XML: `http://localhost:8080/channels-stats`


Testando site_gerencia
----------------------

Primeiro faça o syncdb:

    ./manager.py syncdb

URL django standalone: `http://localhost:8000/administracao`
URL nginx desenvolvedor: `http://localhost:8080/administracao`
URL nginx produção: `http://localhost/administracao`
