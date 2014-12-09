%global iptv_root      /iptv
%global www_site_dir   %{iptv_root}%{_localstatedir}/www/html
%global sites_dir      %{iptv_root}%{_localstatedir}/www/sites
%global site_home      %{sites_dir}/%{name}
%global nginx_confdir  %{iptv_root}%{_sysconfdir}/nginx
%global nginx_user     nginx
%global nginx_group    %{nginx_user}

# Referencia:
# http://pkgs.fedoraproject.org/cgit/python-django.git/tree/python-django.spec

Name:           site_iptv
Version:        GIT_CURRENT_VERSION
Release:        1%{?dist}
Summary:        Sistema IPTV - Cianet

Group:          Development/Languages
License:        Proprietary
URL:            http://www.cianet.ind.br/
Source:         %{name}-%{version}.tar.gz
Source5:        site_iptv.service
Source6:        site_iptv.sysconfig
Source7:        postgresql_iptv.service

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python2-devel
# BuildRequires:  python-setuptools
BuildRequires:  python-sphinx
BuildRequires:  systemd-units


%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
Requires:       python-pillow
%else
Requires:       python-imaging
%endif

Requires:       postgresql-server
Requires:       python-psycopg2
Requires:       python-flup
# Testes unitarios
# Requires:       python-nose
# Requires:       python-django-nose

## Por hora sem migração Usando embutino no pacote com submodulo
Requires:       python-paramiko
Requires:       python-dateutil
Requires:       pytz
Requires:       python-lxml
Requires:       daemonize
Requires:       python-BeautifulSoup
Requires:       python-memcached
Requires:       memcached
Requires:       pydot
Requires:       net-snmp-python
Requires:       python-mimeparse
# SOAP client to CAS (Verimatrix)
Requires:       python-suds-jurko
# Monitoramento
Requires:       pynag

Requires:       nginxcianet >= 1.4.3
# Para requests http no nbridge
Requires:       python-requests

# Para depuração com o django-debug-toolbar
Requires:       python-sqlparse

## Por hora para a versão de demo vai instalar
# Requires:       multicat >= 2.0.1
# Requires:       dvblast >= 2.2.1

%description
Sistema middleware de IPTV

%prep
%setup -q -n %{name}-%{version}

%build

%install
rm -rf $RPM_BUILD_ROOT
%{__install} -p -d -m 0755 %{buildroot}%{site_home}
cp -r  %{_builddir}/%{name}-%{version}/* %{buildroot}%{site_home}/
%{__install} -p -d -m 0775 %{buildroot}%{www_site_dir}/tvfiles
%{__install} -p -d -m 0775 %{buildroot}%{www_site_dir}/tvfiles/media
%{__install} -p -d -m 0775 %{buildroot}%{www_site_dir}/tvfiles/static
%{__install} -p -d -m 0755 %{buildroot}%{iptv_root}%{_localstatedir}/lib/cache
%{__install} -p -d 0755 %{buildroot}%{_sysconfdir}
%{__mkdir_p} %{buildroot}%{iptv_root}%{_localstatedir}/log
%{__mkdir_p} %{buildroot}%{iptv_root}%{_localstatedir}/www
%{__mkdir_p} %{buildroot}%{iptv_root}%{_localstatedir}/run
%{__mkdir_p} %{buildroot}%{iptv_root}%{_localstatedir}/run/%{name}
%{__mkdir_p} %{buildroot}%{iptv_root}%{_localstatedir}/log/multicat
%{__mkdir_p} %{buildroot}%{iptv_root}%{_localstatedir}/log/dvblast
%{__mkdir_p} %{buildroot}%{iptv_root}%{_localstatedir}/log/vlc
%{__mkdir_p} %{buildroot}%{iptv_root}%{_localstatedir}/log/ffmpeg
%{__mkdir_p} %{buildroot}%{iptv_root}%{_localstatedir}/run/multicat
%{__mkdir_p} %{buildroot}%{iptv_root}%{_localstatedir}/run/multicat/sockets
%{__mkdir_p} %{buildroot}%{iptv_root}%{_localstatedir}/run/dvblast
%{__mkdir_p} %{buildroot}%{iptv_root}%{_localstatedir}/run/dvblast/sockets
%{__mkdir_p} %{buildroot}%{iptv_root}%{_localstatedir}/run/diskctrl
%{__install} -p -d -m 0700 %{buildroot}%{iptv_root}%{_localstatedir}/lib/postgresql
%{__install} -p -d -m 0755 %{buildroot}%{_unitdir}
%{__install} -p -m 0644 %{SOURCE5} %{buildroot}%{_unitdir}/site_iptv.service
%{__install} -p -d -m 0755 %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -p -m 0644 %{SOURCE6} %{buildroot}%{_sysconfdir}/sysconfig/site_iptv
%{__install} -p -m 0644 %{SOURCE7} %{buildroot}%{_unitdir}/postgresql_iptv.service
%{__mkdir_p} %{buildroot}%{_localstatedir}/lib/iptv/recorder
%{__mkdir_p} %{buildroot}%{_localstatedir}/lib/iptv/videos
# Definindo um arquivo para colocar o nome da versão
%{__mkdir_p} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
echo "%{version}-%{release}" > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/site_iptv_version

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post %{name}.service
%systemd_post
/usr/bin/systemctl daemon-reload --system
/sbin/usermod -a -G video -s /bin/bash nginx

# É uma atualização?
if [ "$1" = "2" ];then
    current=$(cat %{_sysconfdir}/sysconfig/site_iptv_version)
    echo "Current=$current"
    if [[ -f %{_sysconfdir}/sysconfig/site_iptv_version ]];then
        if [ "$current" = "0.19.6-1.fc20" ]; then
            # Migração fake
            echo "Migração fake para atualizar versão Django 1.7"
            /bin/su nginx -c "%{__python} %{site_home}/manage.py migrate --fake"
        else
            /bin/su nginx -c "%{__python} %{site_home}/manage.py migrate"
        fi
    fi
else
    echo -e "\033[0;31m"
    echo "========================================================================="
    echo "Atenção: Criar um usuário com senha no banco de dados."
    echo "Editar a configuração: %{site_home}/settings.py."
    echo ""
    echo "Após configurado executar os comandos:"
    echo "Inicializar o banco de dados:"
    echo "su - postgres"
    echo "initdb -D /iptv/var/lib/postgresql"
    echo "========================================================================="
    echo -e "\033[0m"
fi

/bin/su nginx -c "%{__python} %{site_home}/manage.py collectstatic --noinput" > /dev/null
echo "Migrando banco de dados"
/bin/su nginx -c "%{__python} %{site_home}/manage.py migrate"

# https://fedoraproject.org/wiki/Packaging:ScriptletSnippets
%pre -p %{__python}
# -*- encoding:utf8 -*-

# Caso seja uma atualização:
# Caso a versão anterior seja anterior à 0.19.6-1 Interrompe a atualização de exibe mensagem de erro avisando que primeiro deve atualizar para 0.19.6-1
# Caso seja posterior à 0.20.0-1 após a instalação executar migrate noramalmente
import rpm
from rpmUtils import miscutils
import sys, os

install_status = sys.argv[1]

v_migrate = '0.19.6-1.fc20'
v_current = '%{version}-%{release}'

version_migrate = miscutils.stringToVersion(v_migrate)
version_current = miscutils.stringToVersion(v_current)
version_compare = miscutils.compareEVR(version_migrate, version_current)

if install_status >= 2: # Atualização
    if version_compare <= 0:
        print('Para atualização, é necessário atualizar para a versão 0.19.6-1 primeiro.')
        sys.exit(-1)
    version_path = '%{_sysconfdir}/sysconfig/site_iptv_version'
    if os.path.exists(version_path):
        with open(version_path) as f:
            version_info = f.read()
            old_version_string = version_info.strip()
            old_version = miscutils.stringToVersion(old_version_string)
            version_compare = miscutils.compareEVR(version_migrate, old_version)
            if version_compare <= 0:
                # Pode atualizar
                print('Para atualização, é necessário atualizar para a versão 0.19.6-1 primeiro.')
                sys.exit(-1)
    else:
        # É uma versão anteriror à 0.19.6-1
        print('Para atualização, é necessário atualizar para a versão 0.19.6-1 primeiro.')
        sys.exit(-1)


%preun
%systemd_preun

%postun
%systemd_postun

%files
%defattr(-,%{nginx_user},%{nginx_group},-)
%{site_home}/*
%dir %{www_site_dir}/tvfiles
%dir %{www_site_dir}/tvfiles/media
%dir %{www_site_dir}/tvfiles/static
%dir %{sites_dir}
%dir %{iptv_root}%{_localstatedir}/log/multicat
%dir %{iptv_root}%{_localstatedir}/log/dvblast
%dir %{iptv_root}%{_localstatedir}/log/vlc
%dir %{iptv_root}%{_localstatedir}/log/ffmpeg
%dir %{iptv_root}%{_localstatedir}/run/multicat
%dir %{iptv_root}%{_localstatedir}/run/multicat/sockets
%dir %{iptv_root}%{_localstatedir}/run/dvblast
%dir %{iptv_root}%{_localstatedir}/run/dvblast/sockets
%dir %{iptv_root}%{_localstatedir}/run/diskctrl
%dir %{iptv_root}%{_localstatedir}/www
%dir %{iptv_root}%{_localstatedir}/run/%{name}
%dir %{iptv_root}%{_localstatedir}/lib/cache
%dir %{site_home}
%config(noreplace) %{site_home}/iptv/settings.py
%dir %{_localstatedir}/lib/iptv/recorder
%dir %{_localstatedir}/lib/iptv/videos
# IPTV Database
%defattr(-,postgres,postgres,-)
%dir %{iptv_root}%{_localstatedir}/lib/postgresql
%defattr(-,root,root,-)
%{_unitdir}/site_iptv.service
%{_unitdir}/postgresql_iptv.service
%config(noreplace) %{_sysconfdir}/sysconfig/site_iptv
# Arquivo com a versão do pacote
%{_sysconfdir}/sysconfig/site_iptv_version


%changelog
* Tue Dec 09 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.20.0-1
- Update Django 1.7 exclude south.
* Thu Dec 04 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.19.6-1
- Auto migração de banco de dados
- Arquivo com a versão do pacote para atualizações
* Wed Nov 19 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.19.5-1
- lock to stop tvod
* Thu Oct 23 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.19.4-1
- Desativando fix de tvod
- Permissão de acesso do STB na gravação com respostas diferenciadas do motivo
- Habilita o inline só na edição de STB
- logs
- Campo com problema na migração
* Thu Oct 09 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.19.1-1
- Timeout to tvod lock.
* Wed Oct 08 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.19.0-1
- Fix TVoD, validate MAC addr.
* Tue Sep 16 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.18.1-1
- Nbridge offline.
- Middleware API filter.
- Remote debug on admin to STB.
* Wed Sep 10 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.17.3-1
- Remote debug STB on admin.
* Tue Sep 09 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.17.2-1
- Devolve o objeto criado sempre por causa do bug do backbone.
- Não salva mais os logos no frontend pois não faz mais sentido.
* Fri Sep 05 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.17.1-1
- Fix rpm query on server.
* Thu Sep 04 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.17.0-1
- Release with reload_channel API. Some fix.
* Fri Aug 22 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.16.1-1
- Replace python-suds to python-suds-jurko.
- Merge dev epg to fix importation.
* Mon Aug 11 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.16.0-1
- Remove some dependencies, add some epg import fix
* Fri Aug 01 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.15.0-1
- Fix import epg. Fix search on tv.
* Thu Jul 24 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.14.0-1
- EPG importer, on/off-line nbridge-stb.
* Mon Jun 02 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.13.0-1
- Schedule API and remote control first test.
* Fri May 02 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.12.0-1
- Schedule API + Migrations.
* Tue Mar 18 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.11.2-1
- Fix Image replace on config to frontend.
* Mon Mar 17 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.11.0-1
- Stop TVoD on login. Status on-line on login. New STB fields.
* Mon Feb 24 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.10.8-1
- Fix TVoD
* Thu Feb 13 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.10.6-1
- Fix all channel. STB reboot. SoftTranscode with ffmpeg.
* Wed Jan 22 2014 Helber Maciel Guerra <helber@cianet.ind.br> - 0.10.2-1
- API V2 channel and userchennel.
- Request reload channel and user channel to nbridge on SetTopBoxChannel (create, delete)
* Thu Nov 14 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.10.0-1
- New release Django 1.5 all settings moved to iptv.
* Fri Nov 01 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.16.0-1
- Move nbridge systemd to nbridge rpm.
* Sat Oct 19 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.15.4-1
- Conflito com pacote nbridge.
* Fri Oct 18 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.15.3-1
- Creation of systemd config and env files to nbridge.
* Wed Oct 09 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.15.0-1
- nbridge with systemd.
* Fri Oct 04 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.14.0-1
- Enable nbridge to websocket client and nginx-fe restart.
* Thu Oct 03 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.13.4-1
- Fix nbridge, monitoring template tag.
* Fri Sep 27 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.13.1-1
- Fix limit 20 on device. systemd config. recorder SSD.
* Sun Aug 25 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.12.0-1
- Release to Netcom and life telecom.
- Integration with albis STB.
* Wed Aug 07 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.11.2-1
- Fix recorder command, django-south e django-tastypie
- Fix rpm spec
* Tue Jul 02 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.8.0-0
- Storage, player and recorder fix
* Thu May 16 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.3.2-0
- Fix erp access on tv.channel API.
* Tue May 07 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.3.1-2
- Fix nginx location
* Mon May 06 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.3.0-0
- Release to life telecom, integration API, operator log
* Mon May 06 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.2.4-0
- TV API always return 200 OK. But filtred channel list
* Tue Apr 23 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.2.2-1
- Fix arguments on API app tv
* Mon Apr 22 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.2.1-0
- Fix timezone on tools/date
* Mon Apr 22 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.2.0-0
- Release to compact API frontend
* Tue Apr 02 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.1.0-0
- Integration release
* Tue Mar 19 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.0.1-0
- Fix de filter channel on API. Stop stream on delete.
* Fri Mar 15 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.0.0-3
- sysconfig dir nginx
* Fri Mar 15 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.0.0-2
- Fix missing module init on root
* Fri Mar 15 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.0.0-1
- Correção de settings
* Thu Mar 14 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.0.0
- Release 0.9.0.0
* Thu Feb 21 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.8.0-2
- Solve conflict on package nginxcianet
* Fri Jan 25 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.8.0-1
- Bug Fix import_portalbsd
* Thu Jan 24 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.8.0
- New release to test.
* Fri Jan 18 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.6.5-4
- Fix symbolic link template to frontend
* Wed Jan 16 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.6.5-3
- Try fix pcrpid recorder. Servidor de monitoramento. Middleware can be not only localhost.
* Wed Jan 16 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.6.5-2
- Bug fix on start DigitalTuner and IsdbTuner
* Wed Jan 16 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.6.5-1
- Bug Fix recursive stop on UniqueIP. Bug Fix import_digitaltv
* Wed Jan 09 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.6.5
- Fix importation duplicated elements o EPG
* Thu Jan 03 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.6.4
- Bug Fix - Duplicated EPG on import
* Mon Dec 17 2012 Helber Maciel Guerra <helber@cianet.ind.br> - 0.6.3-1
- Pass redirect / to /tv/box/
* Fri Dec 14 2012 Helber Maciel Guerra <helber@cianet.ind.br> - 0.6.3
- FIX recursion on pushstream.
- Feature monitoramento.
* Wed Dec 12 2012 Helber Maciel Guerra <helber@cianet.ind.br> - 0.6.2
- Created systemd service to respect dependency.
- Created memcached now to tvod semaphore.
* Fri Oct 19 2012 Helber Maciel Guerra <helber@cianet.ind.br> - 0.6.1
- Fix EPG import and enable cache for list request on nginx
* Thu Oct 04 2012 Helber Maciel Guerra <helber@cianet.ind.br> - 0.6.0
- Nova versão para Life telecom e futurecom
* Mon Aug 27 2012 Helber Maciel Guerra <helber@cianet.ind.br> - 0.5.2 build 3
- Correção na criação das imagens de canal
* Fri Aug 10 2012 Helber Maciel Guerra <helber@cianet.ind.br> - 0.5.2
- Bug recursive execution. Removed command runmedia on init. Backup settings.py with rpm noreplace.
* Thu Aug 09 2012 Helber Maciel Guerra <helber@cianet.ind.br> - 0.5.1
- Put restart on save transcode volume. Tested transcode volume.
* Tue Jul 31 2012 Helber Maciel Guerra <helber@cianet.ind.br> - 0.5.0
- New version with easy interfece to ABTA and wizard
* Tue Jul 17 2012 Helber Maciel Guerra <helber@cianet.ind.br> - 0.4.3
- First test release to Osvaldo: Bugfix, TVOD, EPG
* Tue Jul 17 2012 Helber Maciel Guerra <helber@cianet.ind.br> - 0.4.2
- Fix timezone on epg, python-BeautifulSoup on requires.
* Mon Jul 16 2012 Helber Maciel Guerra <helber@cianet.ind.br> - 0.4.1
- New version and skip network connection on database.
* Thu Jun 14 2012 Helber Maciel Guerra <helber@cianet.ind.br> - 0.3.4
- Multiples changes on this release
* Wed Dec 14 2011 Helber Maciel Guerra <helber@cianet.ind.br> - 0.0.2
- Criação de autostart de fluxos e ligação entre device DVB pelo MAC
