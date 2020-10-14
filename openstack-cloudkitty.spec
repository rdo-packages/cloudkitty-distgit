%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global with_doc %{!?_without_doc:1}%{?_without_doc:0}

Name: openstack-cloudkitty
Summary: OpenStack Rating (cloudkitty)
Version: 13.0.0
Release: 1%{?dist}
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
BuildRequires: git
BuildRequires: python3-ceilometerclient
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

Requires: python3-alembic >= 0.8.0
Requires: python3-gnocchiclient >= 2.5.0
Requires: python3-keystoneauth1 >= 2.1.0
Requires: python3-keystoneclient >= 1.9.0
Requires: python3-keystonemiddleware >= 4.0.0
Requires: python3-monascaclient >= 1.9.0
Requires: python3-stevedore
Requires: python3-oslo-messaging >= 5.24.2
Requires: python3-oslo-concurrency >= 3.5.0
Requires: python3-oslo-config >= 3.7.0
Requires: python3-oslo-context >= 2.9.0
Requires: python3-oslo-i18n >= 2.1.0
Requires: python3-oslo-db >= 4.1.0
Requires: python3-oslo-log >= 1.14.0
Requires: python3-oslo-middleware >= 3.27.0
Requires: python3-oslo-utils >= 3.5.0
Requires: python3-oslo-upgradecheck >= 0.1.1
Requires: python3-oslo-policy >= 0.5.0
Requires: python3-pbr >= 2.0.0
Requires: python3-pecan
Requires: python3-six
Requires: python3-sqlalchemy
Requires: python3-tooz >= 1.28.0
Requires: python3-wsme
Requires: python3-influxdb
Requires: python3-iso8601 >= 0.1.9
Requires: python3-voluptuous >= 0.11.1
Requires: python3-flask
Requires: python3-flask-restful
Requires: python3-cotyledon
Requires: python3-futurist >= 1.6.0

Requires: python3-paste-deploy
Requires: python3-dateutil >= 2.5.3

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
* Wed Oct 14 2020 RDO <dev@lists.rdoproject.org> 13.0.0-1
- Update to 13.0.0
- Enable sources tarball validation using GPG signature.

* Thu Oct 08 2020 RDO <dev@lists.rdoproject.org> 13.0.0-0.2.0rc1
- Update to 13.0.0.0rc2

* Thu Sep 24 2020 RDO <dev@lists.rdoproject.org> 13.0.0-0.1.0rc1
- Update to 13.0.0.0rc1

