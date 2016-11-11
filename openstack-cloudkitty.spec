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
BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: git
BuildRequires: python-ceilometerclient
BuildRequires: python-gnocchiclient
BuildRequires: python-keystoneclient
BuildRequires: python-keystonemiddleware
BuildRequires: python-iso8601
BuildRequires: python-sphinx
BuildRequires: python-stevedore
BuildRequires: python-oslo-messaging
BuildRequires: python-setuptools
BuildRequires: python-oslo-config
BuildRequires: python-oslo-sphinx
BuildRequires: python-oslo-i18n
BuildRequires: python-oslo-db
BuildRequires: python-oslo-utils
BuildRequires: python-oslo-policy
BuildRequires: python-pbr
BuildRequires: python-pecan
BuildRequires: python-paste-deploy
BuildRequires: python-six
BuildRequires: python-sqlalchemy
BuildRequires: python-tooz
BuildRequires: python-werkzeug
BuildRequires: python-wsme
BuildRequires: systemd-units

Requires: %{name}-common = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: %{name}-processor = %{version}-%{release}

%package -n python-cloudkitty-tests
Summary:        CloudKitty tests
Requires:       %{name}-common = %{version}-%{release}

%description -n python-cloudkitty-tests
This package contains the CloudKitty test files.

%prep
%setup -q -n cloudkitty-%{upstream_version}

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt

%build
%{__python} setup.py build

# Generate config file etc/cloudkitty/cloudkitty.conf.sample
PYTHONPATH=. oslo-config-generator --config-file=etc/oslo-config-generator/cloudkitty.conf

%install
%{__python} setup.py install -O1 --skip-build --root=%{buildroot}
mkdir -p %{buildroot}/var/log/cloudkitty/
mkdir -p %{buildroot}/var/run/cloudkitty/
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-cloudkitty

# install systemd unit files
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/cloudkitty-api.service
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/cloudkitty-processor.service

mkdir -p %{buildroot}/var/lib/cloudkitty/
mkdir -p %{buildroot}/etc/cloudkitty/

# we need to package sphinxcontrib-pecanwsme for this to work
#export PYTHONPATH="$( pwd ):$PYTHONPATH"
#pushd doc
#sphinx-build -b html -d build/doctrees source build/html
#popd

install -p -D -m 640 etc/cloudkitty/cloudkitty.conf.sample %{buildroot}/%{_sysconfdir}/cloudkitty/cloudkitty.conf
install -p -D -m 640 etc/cloudkitty/policy.json %{buildroot}/%{_sysconfdir}/cloudkitty/policy.json
install -p -D -m 640 etc/cloudkitty/api_paste.ini %{buildroot}%{_sysconfdir}/cloudkitty/api_paste.ini

%description
CloudKitty provides a Rating-as-a-Service component for OpenStack.


%package common
Summary: CloudKitty common
Group: System Environment/Base

Requires: python-ceilometerclient
Requires: python-gnocchiclient
Requires: python-keystoneclient
Requires: python-keystonemiddleware
Requires: python-iso8601
Requires: python-stevedore
Requires: python-oslo-messaging
Requires: python-setuptools
Requires: python-oslo-config
Requires: python-oslo-i18n
Requires: python-oslo-db
Requires: python-oslo-utils
Requires: python-oslo-policy
Requires: python-pecan
Requires: python-paste-deploy
Requires: python-six
Requires: python-sqlalchemy
Requires: python-tooz
Requires: python-werkzeug
Requires: python-wsme

Requires(pre): shadow-utils

%description common
Components common to all CloudKitty services.

%files common
%doc LICENSE
%{_bindir}/cloudkitty-dbsync
%{_bindir}/cloudkitty-storage-init
%{_bindir}/cloudkitty-writer
%{python_sitelib}/cloudkitty*
%exclude %{python2_sitelib}/cloudkitty/tests
%dir %attr(0755,cloudkitty,root) %{_localstatedir}/log/cloudkitty
%dir %attr(0755,cloudkitty,root) %{_localstatedir}/run/cloudkitty
%dir %attr(0755,cloudkitty,root) %{_sharedstatedir}/cloudkitty
%dir %attr(0755,cloudkitty,root) %{_sysconfdir}/cloudkitty
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-cloudkitty
%config(noreplace) %attr(-, root, cloudkitty) %{_sysconfdir}/cloudkitty/cloudkitty.conf
%config(noreplace) %attr(-, root, cloudkitty) %{_sysconfdir}/cloudkitty/policy.json
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

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

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

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

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

%files -n python-cloudkitty-tests
%license LICENSE
%{python2_sitelib}/cloudkitty/tests

%changelog
