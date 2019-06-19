Name:		pszi-ab-dispather
Version: 	0.1
Release: 	1%{?dist}.sz
Summary: 	Диспетчер Агента Безопасности
Group: 		common
License: 	commercial
URL:		http://www.fintech.ru
Source0:	%{name}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Requires:	python_sz_daemon

#%global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib;")
%global python_sitelib /usr/lib/python2.7/site-packages

%description
Диспетчер Агента Безопасности

%prep

%setup -n %{name} -q

%install
mkdir -p %{buildroot}/%{python_sitelib}/pszi_ab_dispather/
cp -r ./lib/* %{buildroot}/%{python_sitelib}/pszi_ab_dispather/

mkdir -p %{buildroot}/usr/share/pszi_ab_dispather/
cp -r ./share/* %{buildroot}/usr/share/pszi_ab_dispather/

mkdir -p %{buildroot}/usr/sbin/
cp -r ./sbin/* %{buildroot}/usr/sbin/

%clean
rm -rf %{buildroot}

%post

%files
%defattr(644,root,root,-)
%{python_sitelib}/pszi_ab_dispather/ab_base_daemon.py
%{python_sitelib}/pszi_ab_dispather/base_db.py
%{python_sitelib}/pszi_ab_dispather/__init__.py
%{python_sitelib}/pszi_ab_dispather/job_handler.py
%{python_sitelib}/pszi_ab_dispather/socket_listener.py

%defattr(750,root,root,-)
/usr/sbin/ab-dispather
/usr/sbin/ab-console


%exclude %{python_sitelib}/pszi_ab_dispather/*.pyc
%exclude %{python_sitelib}/pszi_ab_dispather/*.pyo

%doc

%changelog
* Tue Jun 18 2019 Deyneko Aleksey <deyneko@fintech.ru> 0.1-0
- Первая версия
