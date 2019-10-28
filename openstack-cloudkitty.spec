# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global with_doc %{!?_without_doc:1}%{?_without_doc:0}

Name: openstack-cloudkitty
Summary: OpenStack Rating (cloudkitty)
Version: XXX
Release: XXX
License: ASL 2.0
URL: http://github.com/openstack/cloudkitty
Source0: https://tarballs.openstack.org/cloudkitty/cloudkitty-%{upstream_version}.tar.gz
Source1: cloudkitty.logrotate
Source2: cloudkitty-api.service
Source3: cloudkitty-processor.service

BuildArch: noarch
BuildRequires: python%{pyver}-devel
BuildRequires: python%{pyver}-setuptools
BuildRequires: git
BuildRequires: python%{pyver}-ceilometerclient
BuildRequires: python%{pyver}-gnocchiclient
BuildRequires: python%{pyver}-keystoneclient
BuildRequires: python%{pyver}-keystonemiddleware
BuildRequires: python%{pyver}-monascaclient
BuildRequires: python%{pyver}-sphinx
BuildRequires: python%{pyver}-stevedore
BuildRequires: python%{pyver}-oslo-messaging
BuildRequires: python%{pyver}-oslo-config
BuildRequires: python%{pyver}-oslo-sphinx
BuildRequires: python%{pyver}-oslo-i18n
BuildRequires: python%{pyver}-oslo-db
BuildRequires: python%{pyver}-oslo-utils
BuildRequires: python%{pyver}-oslo-upgradecheck
BuildRequires: python%{pyver}-oslo-policy
BuildRequires: python%{pyver}-pbr
BuildRequires: python%{pyver}-pecan
BuildRequires: python%{pyver}-six
BuildRequires: python%{pyver}-sqlalchemy
BuildRequires: python%{pyver}-tooz
BuildRequires: python%{pyver}-wsme
BuildRequires: python%{pyver}-influxdb
BuildRequires: python%{pyver}-flask
BuildRequires: python%{pyver}-flask-restful
BuildRequires: python%{pyver}-cotyledon
BuildRequires: python%{pyver}-futurist
BuildRequires: systemd
BuildRequires: openstack-macros

# Handle python2 exception
%if %{pyver} == 2
BuildRequires: python-paste-deploy
%else
BuildRequires: python%{pyver}-paste-deploy
%endif

Requires: %{name}-common = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: %{name}-processor = %{version}-%{release}

%package -n python%{pyver}-cloudkitty-tests
Summary:        CloudKitty tests
%{?python_provide:%python_provide python%{pyver}-cloudkitty-tests}
Requires:       %{name}-common = %{version}-%{release}

%description -n python%{pyver}-cloudkitty-tests
This package contains the CloudKitty test files.

%prep
%setup -q -n cloudkitty-%{upstream_version}

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
%py_req_cleanup

%build
%{pyver_build}

# Generate config file etc/cloudkitty/cloudkitty.conf.sample
PYTHONPATH=. oslo-config-generator-%{pyver} --config-file=etc/oslo-config-generator/cloudkitty.conf
%install
%{pyver_install}
mkdir -p %{buildroot}/var/log/cloudkitty/
mkdir -p %{buildroot}/var/run/cloudkitty/
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-cloudkitty

# install systemd unit files
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/cloudkitty-api.service
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/cloudkitty-processor.service

mkdir -p %{buildroot}/var/lib/cloudkitty/
mkdir -p %{buildroot}/etc/cloudkitty/

# we need to package sphinxcontrib-pecanwsme for this to work
#pushd doc
#sphinx-build-%{pyver} -b html -d build/doctrees source build/html
#popd

install -p -D -m 640 etc/cloudkitty/cloudkitty.conf.sample %{buildroot}/%{_sysconfdir}/cloudkitty/cloudkitty.conf
install -p -D -m 640 etc/cloudkitty/api_paste.ini %{buildroot}%{_sysconfdir}/cloudkitty/api_paste.ini
install -p -D -m 640 etc/cloudkitty/metrics.yml %{buildroot}%{_sysconfdir}/cloudkitty/metrics.yml

%description
CloudKitty provides a Rating-as-a-Service component for OpenStack.


%package common
Summary: CloudKitty common
Group: System Environment/Base

Requires: python%{pyver}-alembic >= 0.8.0
Requires: python%{pyver}-ceilometerclient >= 2.2.1
Requires: python%{pyver}-gnocchiclient >= 2.5.0
Requires: python%{pyver}-keystoneauth1 >= 2.1.0
Requires: python%{pyver}-keystoneclient >= 1.9.0
Requires: python%{pyver}-keystonemiddleware >= 4.0.0
Requires: python%{pyver}-monascaclient >= 1.9.0
Requires: python%{pyver}-stevedore
Requires: python%{pyver}-oslo-messaging >= 5.24.2
Requires: python%{pyver}-oslo-concurrency >= 3.5.0
Requires: python%{pyver}-oslo-config >= 3.7.0
Requires: python%{pyver}-oslo-context >= 2.9.0
Requires: python%{pyver}-oslo-i18n >= 2.1.0
Requires: python%{pyver}-oslo-db >= 4.1.0
Requires: python%{pyver}-oslo-log >= 1.14.0
Requires: python%{pyver}-oslo-middleware >= 3.27.0
Requires: python%{pyver}-oslo-utils >= 3.5.0
Requires: python%{pyver}-oslo-upgradecheck >= 0.1.1
Requires: python%{pyver}-oslo-policy >= 0.5.0
Requires: python%{pyver}-pbr >= 2.0.0
Requires: python%{pyver}-pecan
Requires: python%{pyver}-six
Requires: python%{pyver}-sqlalchemy
Requires: python%{pyver}-tooz >= 1.28.0
Requires: python%{pyver}-wsme
Requires: python%{pyver}-influxdb
Requires: python%{pyver}-iso8601 >= 0.1.9
Requires: python%{pyver}-voluptuous >= 0.10
Requires: python%{pyver}-flask
Requires: python%{pyver}-flask-restful
Requires: python%{pyver}-cotyledon
Requires: python%{pyver}-futurist >= 1.6.0

# Handle python2 exception
%if %{pyver} == 2
Requires: python-paste-deploy
%else
Requires: python%{pyver}-paste-deploy
%endif

Requires(pre): shadow-utils

%description common
Components common to all CloudKitty services.

%files common
%doc LICENSE
%{_bindir}/cloudkitty-dbsync
%{_bindir}/cloudkitty-storage-init
%{_bindir}/cloudkitty-writer
%{_bindir}/cloudkitty-status
%{pyver_sitelib}/cloudkitty*
%exclude %{pyver_sitelib}/cloudkitty/tests
%dir %attr(0750,cloudkitty,root) %{_localstatedir}/log/cloudkitty
%dir %attr(0755,cloudkitty,root) %{_localstatedir}/run/cloudkitty
%dir %attr(0755,cloudkitty,root) %{_sharedstatedir}/cloudkitty
%dir %attr(0755,cloudkitty,root) %{_sysconfdir}/cloudkitty
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-cloudkitty
%config(noreplace) %attr(-, root, cloudkitty) %{_sysconfdir}/cloudkitty/cloudkitty.conf
%config(noreplace) %attr(-, root, cloudkitty) %{_sysconfdir}/cloudkitty/metrics.yml
%config(noreplace) %attr(-, root, cloudkitty) %{_sysconfdir}/cloudkitty/api_paste.ini

%pre common
getent group cloudkitty >/dev/null || groupadd -r cloudkitty
getent passwd cloudkitty  >/dev/null || \
useradd -r -g cloudkitty -d %{_sharedstatedir}/cloudkitty -s /sbin/nologin \
-c "CloudKitty Daemons" cloudkitty
exit 0

%package api
Summary: The CloudKitty API
Group: System Environment/Base

Requires: %{name}-common = %{version}-%{release}

%{?systemd_requires}

%description api
OpenStack API for the Rating-as-a-Service component (CloudKitty).

%files api
%doc README.rst LICENSE
%{_bindir}/cloudkitty-api
%{_unitdir}/cloudkitty-api.service

%post api
%systemd_post cloudkitty-api.service

%preun api
%systemd_preun cloudkitty-api.service

%postun api
%systemd_postun_with_restart cloudkitty-api.service


%package processor
Summary: The CloudKitty processor
Group: System Environment/Base

Requires: %{name}-common = %{version}-%{release}

%{?systemd_requires}

%description processor
CloudKitty component for computing rating data.

%files processor
%doc README.rst LICENSE
%{_bindir}/cloudkitty-processor
%{_unitdir}/cloudkitty-processor.service

%post processor
%systemd_post cloudkitty-processor.service

%preun processor
%systemd_preun cloudkitty-processor.service

%postun processor
%systemd_postun_with_restart cloudkitty-processor.service

%files -n python%{pyver}-cloudkitty-tests
%license LICENSE
%{pyver_sitelib}/cloudkitty/tests

%changelog
# REMOVEME: error caused by commit http://git.openstack.org/cgit/openstack/cloudkitty/commit/?id=1cf228104d92c6a9d57ead91d2099a9246eb13c6
