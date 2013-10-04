Name:           site_iptv
Version:        GIT_CURRENT_VERSION
Release:        1%{?dist}
Summary:        Sistema IPTV - Cianet

Group:          Development/Languages
License:        Proprietary
URL:            http://www.cianet.ind.br/
Source:         %{name}-%{version}.tar.gz
Source1:        tv.conf
#Source2:        site_iptv.init
Source3:        my.cnf
Source4:        cache.conf
Source5:        site_iptv.service
Source6:        site_iptv.sysconfig
Source7:        postgresql_iptv.service

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel python-setuptools-devel
BuildRequires:  systemd-units


%if 0%{?fedora} >= 19
Requires:       python-pillow
%else
Requires:       python-imaging
%endif

%if 0%{?fedora} >= 18
Requires:       python-django >= 1.4.5
BuildRequires:  python-django >= 1.4.5
%else
Requires:       Django >= 1.4
BuildRequires:  Django >= 1.4
%endif

#Requires:       mysql-server
#Requires:       MySQL-python
Requires:       postgresql-server
Requires:       python-psycopg2
Requires:       python-imaging
Requires:       python-flup

## Por hora sem migração Usando embutino no pacote com submodulo
# Requires:       Django-south
# Requires:       django-tastypie >= 0.9.14
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
# SOAP client to CAS (Verimatrix)
Requires:       python-suds
# Monitoramento
Requires:       pynag-cianet >= 0.1.1

Requires:       nginxcianet >= 1.4.1

## Por hora para a versão de demo vai instalar
Requires:       multicat >= 2.0.1
Requires:       dvblast >= 2.2.1

Prefix:         /iptv

%define www_site_dir   %{prefix}%{_localstatedir}/www/html
%define sites_dir      %{prefix}%{_localstatedir}/www/sites
%define site_home      %{sites_dir}/%{name}
%define nginx_confdir  %{prefix}%{_sysconfdir}/nginx
%define nginx_user     nginx
%define nginx_group    %{nginx_user}

%description
Sistema middleware de IPTV

%prep
%setup -q -n %{name}-%{version}

%build

%install
rm -rf $RPM_BUILD_ROOT
#/var/www/sites/site_iptv
%{__install} -p -d -m 0755 %{buildroot}%{site_home}
cp -r  %{_builddir}/%{name}-%{version}/* %{buildroot}%{site_home}/
#%{__ln_s} %{sites_dir}/frontend %{buildroot}%{site_home}/frontend
#%{__mkdir} %{buildroot}%{site_home}/templates/box
#%{__rm} -f %{buildroot}%{site_home}/templates/box/index.html
#%{__ln_s} %{sites_dir}/frontend/dist/index.html %{buildroot}%{site_home}/templates/box/index.html
%{__install} -p -d -m 0775 %{buildroot}%{www_site_dir}/tvfiles
%{__install} -p -d -m 0775 %{buildroot}%{www_site_dir}/tvfiles/media
%{__install} -p -d -m 0775 %{buildroot}%{www_site_dir}/tvfiles/static
#%{__install} -p -d -m 0755 %{buildroot}%{nginx_confdir}/plugins
#%{__install} -p -m 0644 %{SOURCE1} %{buildroot}%{nginx_confdir}/plugins
#%{__install} -p -d -m 0755 %{buildroot}%{nginx_confdir}/conf.d
#%{__install} -p -m 0644 %{SOURCE4} %{buildroot}%{nginx_confdir}/conf.d/0001-cache.conf
%{__install} -p -d -m 0755 %{buildroot}/%{prefix}/%{_localstatedir}/lib/cache
%{__install} -p -d 0755 %{buildroot}%{_sysconfdir}
#%{__install} -p -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/my.cnf.cianet
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/log
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/www
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/run
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/run/%{name}
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/log/multicat
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/log/dvblast
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/log/vlc
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/log/nbridge
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/run/multicat
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/run/multicat/sockets
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/run/dvblast
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/run/dvblast/sockets
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/run/nbridge
%{__mkdir_p} %{buildroot}/%{prefix}/%{_localstatedir}/run/diskctrl
%{__install} -p -d -m 0770 %{buildroot}/%{prefix}/usr/lib/nbridge
%{__install} -p -d -m 0700 %{buildroot}/%{prefix}/%{_localstatedir}/lib/postgresql
%{__install} -p -d -m 0755 %{buildroot}%{_unitdir}
%{__install} -p -m 0644 %{SOURCE5} %{buildroot}%{_unitdir}/site_iptv.service
%{__install} -p -d -m 0755 %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -p -m 0644 %{SOURCE6} %{buildroot}%{_sysconfdir}/sysconfig/site_iptv
%{__install} -p -m 0644 %{SOURCE7} %{buildroot}%{_unitdir}/postgresql_iptv.service
%{__mkdir_p} %{buildroot}/%{_localstatedir}/lib/iptv/recorder
%{__mkdir_p} %{buildroot}/%{_localstatedir}/lib/iptv/videos

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ $1 == 1 ]; then
    systemctl enable %{name}.service
    systemctl daemon-reload --system
fi
%systemd_post %{name}.service
%systemd_post

echo -e "\033[0;31m"
echo "========================================================================="
echo "Atenção: Criar um usuário com senha no banco de dados."
echo "Editar a configuração: %{site_home}/settings.py."
echo ""
echo "Após configurado executar os comandos:"
echo "Inicializar o banco de dados:"
echo "su - postgres"
echo "initdb -D /iptv/var/lib/postgresql"
echo "su - nginx"
echo "%{__python} %{site_home}/manage.py syncdb"
echo "%{__python} %{site_home}/manage.py collectstatic --noinput"
echo ""
echo "Para resetar algum app:"
echo "%{__python} %{site_home}/manage.py reset <app> --noinput"
echo "Para resetar os gravadores: %{site_home}device/storage_recorder_player.sql"
echo "========================================================================="
echo -e "\033[0m"

#%{__mv} %{_sysconfdir}/my.cnf %{_sysconfdir}/my.cnf.orig
#%{__ln_s} %{_sysconfdir}/my.cnf.cianet %{_sysconfdir}/my.cnf

%preun
%systemd_preun

%postun
%systemd_postun

%files
%defattr(-,%{nginx_user},%{nginx_group},-)
#%config(noreplace) %{nginx_confdir}/plugins/*.conf
#%config(noreplace) %{nginx_confdir}/conf.d/*.conf
%{site_home}/*
%dir %{www_site_dir}/tvfiles
%dir %{www_site_dir}/tvfiles/media
%dir %{www_site_dir}/tvfiles/static
%dir %{sites_dir}
%dir %{prefix}/%{_localstatedir}/log/multicat
%dir %{prefix}/%{_localstatedir}/log/dvblast
%dir %{prefix}/%{_localstatedir}/log/vlc
%dir %{prefix}/%{_localstatedir}/log/nbridge
%dir %{prefix}/%{_localstatedir}/run/multicat
%dir %{prefix}/%{_localstatedir}/run/multicat/sockets
%dir %{prefix}/%{_localstatedir}/run/dvblast
%dir %{prefix}/%{_localstatedir}/run/dvblast/sockets
%dir %{prefix}/%{_localstatedir}/run/diskctrl
%dir %{prefix}/%{_localstatedir}/run/nbridge
%dir %{prefix}/usr/lib/nbridge
%dir %{prefix}/%{_localstatedir}/www
%dir %{prefix}/%{_localstatedir}/run/%{name}
%dir %{prefix}/%{_localstatedir}/lib/cache
%dir %{site_home}
%config(noreplace) %{site_home}/settings.py
%dir %{_localstatedir}/lib/iptv/recorder
%dir %{_localstatedir}/lib/iptv/videos
# IPTV Database
#%config %{_sysconfdir}/my.cnf.cianet
#%defattr(-,mysql,mysql,-)
#%dir %{prefix}/%{_localstatedir}/lib/mysql
%defattr(-,postgres,postgres,-)
%dir %{prefix}/%{_localstatedir}/lib/postgresql
%defattr(-,root,root,-)
%{_unitdir}/site_iptv.service
%{_unitdir}/postgresql_iptv.service
%config(noreplace) %{_sysconfdir}/sysconfig/site_iptv


%changelog
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
* Wed May 16 2013 Helber Maciel Guerra <helber@cianet.ind.br> - 0.9.3.2-0
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
