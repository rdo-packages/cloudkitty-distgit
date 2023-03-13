%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
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
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/cloudkitty/cloudkitty-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch: noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif
BuildRequires: python3-devel
BuildRequires: python3-setuptools
BuildRequires: git-core
BuildRequires: python3-gnocchiclient
BuildRequires: python3-keystoneclient
BuildRequires: python3-keystonemiddleware
BuildRequires: python3-monascaclient
BuildRequires: python3-sphinx
BuildRequires: python3-stevedore
BuildRequires: python3-oslo-messaging
BuildRequires: python3-oslo-config
BuildRequires: python3-oslo-sphinx
BuildRequires: python3-oslo-i18n
BuildRequires: python3-oslo-db
BuildRequires: python3-oslo-utils
BuildRequires: python3-oslo-upgradecheck
BuildRequires: python3-oslo-policy
BuildRequires: python3-pbr
BuildRequires: python3-pecan
BuildRequires: python3-six
BuildRequires: python3-sqlalchemy
BuildRequires: python3-tooz
BuildRequires: python3-wsme
BuildRequires: python3-influxdb
BuildRequires: python3-flask
BuildRequires: python3-flask-restful
BuildRequires: python3-cotyledon
BuildRequires: python3-futurist
BuildRequires: systemd
BuildRequires: openstack-macros

BuildRequires: python3-paste-deploy

Requires: %{name}-common = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: %{name}-processor = %{version}-%{release}

%package -n python3-cloudkitty-tests
Summary:        CloudKitty tests
%{?python_provide:%python_provide python3-cloudkitty-tests}
Requires:       %{name}-common = %{version}-%{release}

%description -n python3-cloudkitty-tests
This package contains the CloudKitty test files.

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%setup -q -n cloudkitty-%{upstream_version}

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
%py_req_cleanup

%build
%{py3_build}

# Generate config file etc/cloudkitty/cloudkitty.conf.sample
PYTHONPATH=. oslo-config-generator --config-file=etc/oslo-config-generator/cloudkitty.conf
%install
%{py3_install}
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
#sphinx-build -b html -d build/doctrees source build/html
#popd

install -p -D -m 640 etc/cloudkitty/cloudkitty.conf.sample %{buildroot}/%{_sysconfdir}/cloudkitty/cloudkitty.conf
install -p -D -m 640 etc/cloudkitty/api_paste.ini %{buildroot}%{_sysconfdir}/cloudkitty/api_paste.ini
install -p -D -m 640 etc/cloudkitty/metrics.yml %{buildroot}%{_sysconfdir}/cloudkitty/metrics.yml

%description
CloudKitty provides a Rating-as-a-Service component for OpenStack.


%package common
Summary: CloudKitty common
Group: System Environment/Base

Requires: python3-alembic >= 1.4.3
Requires: python3-gnocchiclient >= 7.0.6
Requires: python3-keystoneauth1 >= 4.2.1
Requires: python3-keystoneclient >= 4.1.1
Requires: python3-keystonemiddleware >= 9.1.0
Requires: python3-monascaclient >= 2.2.1
Requires: python3-stevedore >= 3.2.2
Requires: python3-oslo-messaging >= 14.1.0
Requires: python3-oslo-concurrency >= 4.3.1
Requires: python3-oslo-config >= 8.3.3
Requires: python3-oslo-context >= 3.1.1
Requires: python3-oslo-i18n >= 5.0.1
Requires: python3-oslo-db >= 8.4.0
Requires: python3-oslo-log >= 4.4.0
Requires: python3-oslo-middleware >= 4.1.1
Requires: python3-oslo-utils >= 4.7.0
Requires: python3-oslo-upgradecheck >= 1.3.0
Requires: python3-oslo-policy >= 3.6.0
Requires: python3-pbr >= 5.5.1
Requires: python3-pecan >= 1.3.3
Requires: python3-sqlalchemy >= 1.3.20
Requires: python3-tooz >= 2.7.1
Requires: python3-wsme >= 0.10.0
Requires: python3-influxdb >= 5.3.1
Requires: python3-iso8601 >= 0.1.13
Requires: python3-voluptuous >= 0.12.0
Requires: python3-flask >= 2.0.0
Requires: python3-flask-restful >= 0.3.9
Requires: python3-cotyledon >= 1.7.3
Requires: python3-futurist >= 2.3.0

Requires: python3-paste-deploy >= 2.1.1
Requires: python3-dateutil >= 2.8.0
Requires: python3-datetimerange >= 0.6.1

Requires(pre): shadow-utils

%description common
Components common to all CloudKitty services.

%files common
%doc LICENSE
%{_bindir}/cloudkitty-dbsync
%{_bindir}/cloudkitty-storage-init
%{_bindir}/cloudkitty-writer
%{_bindir}/cloudkitty-status
%{python3_sitelib}/cloudkitty*
%exclude %{python3_sitelib}/cloudkitty/tests
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

%files -n python3-cloudkitty-tests
%license LICENSE
%{python3_sitelib}/cloudkitty/tests

%changelog
