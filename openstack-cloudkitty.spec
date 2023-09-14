%global milestone .0rc1
%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x815AFEC729392386480E076DCC0DFE2D21C023C9
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order os-api-ref
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif
%global with_doc %{!?_without_doc:1}%{?_without_doc:0}

Name: openstack-cloudkitty
Summary: OpenStack Rating (cloudkitty)
Version: 19.0.0
Release: 0.1%{?milestone}%{?dist}
License: Apache-2.0
URL: http://github.com/openstack/cloudkitty
Source0: https://tarballs.openstack.org/cloudkitty/cloudkitty-%{upstream_version}.tar.gz
#
# patches_base=19.0.0.0rc1
#

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
BuildRequires: pyproject-rpm-macros
BuildRequires: git-core
BuildRequires: systemd
BuildRequires: openstack-macros

Requires: %{name}-common = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: %{name}-processor = %{version}-%{release}

%package -n python3-cloudkitty-tests
Summary:        CloudKitty tests
Requires:       %{name}-common = %{version}-%{release}

%description -n python3-cloudkitty-tests
This package contains the CloudKitty test files.

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n cloudkitty-%{upstream_version} -S git


sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini
sed -i '/.*pip install.*/d' tox.ini

# Remove syntax check tests
rm -f cloudkitty/tests/test_hacking.py

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
%pyproject_wheel

%install
%pyproject_install

# Generate config file etc/cloudkitty/cloudkitty.conf.sample
PYTHONPATH="%{buildroot}/%{python3_sitelib}" oslo-config-generator --config-file=etc/oslo-config-generator/cloudkitty.conf

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

Requires(pre): shadow-utils

%description common
Components common to all CloudKitty services.

%check
%tox -e %{default_toxenv}

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
* Thu Sep 14 2023 RDO <dev@lists.rdoproject.org> 19.0.0-0.1.0rc1
- Update to 19.0.0.0rc1

