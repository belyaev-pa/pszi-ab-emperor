Name:		pszi-ab-dispatcher
Version: 	0.1
Release: 	1%{?dist}.sz
Summary: 	Диспетчер Агента Безопасности
Group: 		common
License: 	commercial
URL:		http://www.fintech.ru
Source0:	%{name}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Requires:	python-sz-daemon

#%global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib;")
%global python_sitelib /usr/lib/python2.7/site-packages

%description
Диспетчер Агента Безопасности + модуль консольного управления

%prep
%setup -n %{name} -q

%install
mkdir -p %{buildroot}/%{python_sitelib}/ab_dispatcher/
cp -r ./lib/* %{buildroot}/%{python_sitelib}/ab_dispatcher/

mkdir -p %{buildroot}/etc/ab-dispatcher/
cp    ./conf/ab-dispatcher.conf  %{buildroot}/etc/ab-dispatcher/
cp    ./conf/handle_scheme.json %{buildroot}/etc/ab-dispatcher/

mkdir -p %{buildroot}/etc/systemd/system/
cp    ./conf/ab-dispatcher.service %{buildroot}/etc/systemd/system/

mkdir -p %{buildroot}/usr/sbin/
cp -r ./sbin/ab_demon.py %{buildroot}/usr/sbin/ab-dispatcher
cp -r ./sbin/console_util.py %{buildroot}/usr/sbin/ab-console

mkdir -p %{buildroot}/var/lib/ab-dispatcher/

mkdir -p %{buildroot}/var/log/ab-dispatcher/

%clean
rm -rf %{buildroot}

%post
echo "Применение файлов из пакета"
/bin/systemctl daemon-reload
/bin/systemctl enable ab-dispatcher.service

%files
%defattr(644,root,root,-)
%{python_sitelib}/ab_dispatcher/ab_base_daemon.py
%{python_sitelib}/ab_dispatcher/base_db.py
%{python_sitelib}/ab_dispatcher/__init__.py
%{python_sitelib}/ab_dispatcher/job_handler.py
%{python_sitelib}/ab_dispatcher/socket_listener.py
%{python_sitelib}/ab_dispatcher/tools.py

/etc/ab-dispatcher/ab-dispatcher.conf
/etc/ab-dispatcher/handle_scheme.json

/etc/systemd/system/ab-dispatcher.service

%defattr(750,root,root,-)
/usr/sbin/ab-dispatcher
/usr/sbin/ab-console

%dir /var/lib/ab-dispatcher/
%dir /var/log/ab-dispatcher/

%exclude %{python_sitelib}/ab_dispatcher/*.pyc
%exclude %{python_sitelib}/ab_dispatcher/*.pyo

%doc

%changelog
* Tue Jun 18 2019 Deyneko Aleksey <deyneko@fintech.ru> 0.1-0
- Первая версия
