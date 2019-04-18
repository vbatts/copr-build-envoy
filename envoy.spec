# this is just a monotonically increasing number to preceed the git hash, to get incremented on every git bump
%global git_bump		0
%global git_commit		fa69fad0de6b63a254ce6a9f8164b31163a1ada0
%global git_shortcommit		%(c=%{git_commit}; echo ${c:0:7})

# don't strip binaries at all
%global __strip			/bin/true
%global debug_package		%{nil}

# don't byte compile the ./examples ...
%global __spec_install_post	/usr/lib/rpm/check-rpaths   /usr/lib/rpm/check-buildroot  \
				/usr/lib/rpm/brp-compress

# they warn against doing this ... :-\
%define _disable_source_fetch 0

Name:		envoy
Version:	1.11.0.%{git_bump}.git.%{git_shortcommit}
Release:	2%{?dist}
Summary:	Envoy is an open source edge and service proxy

#Group:		
License:	Apache v2
URL:		https://github.com/envoyproxy/envoy
#Source0:	https://github.com/envoyproxy/%{name}/archive/v%{version}.tar.gz
Source0:	https://github.com/envoyproxy/envoy/archive/%{git_commit}.zip
Source1:	envoy@.service
Source2:	envoy.sysconfig
Source3:	check_envoy.sh
Source4:	start_envoy.sh
Source5:	reload_envoy.sh

# see https://copr.fedorainfracloud.org/coprs/vbatts/bazel/
BuildRequires:	bazel

BuildRequires:	wget
BuildRequires:	rsync
BuildRequires:	make
BuildRequires:	git
BuildRequires:	java-1.8.0-openjdk-devel
BuildRequires:	bc
BuildRequires:	libtool
BuildRequires:	zip
BuildRequires:	unzip
BuildRequires:	gdb
BuildRequires:	strace
BuildRequires:	python-virtualenv
BuildRequires:	which
BuildRequires:	golang
BuildRequires:  clang
BuildRequires:	coreutils
BuildRequires:	ninja-build

%if 0%{?rhel} > 6
BuildRequires:	centos-release-scl
BuildRequires:	devtoolset-4-gcc-c++
BuildRequires:	cmake3
BuildRequires:    systemd-units
Requires:         firewalld-filesystem
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%else
BuildRequires:	gcc-c++
BuildRequires:  libstdc++-static
BuildRequires:	cmake >= 3.1
%endif

%description
%{summary}.

%package docs
Summary:	Docs and examples for envoy
BuildArch:	noarch

Requires:	%{name} = %{version}-%{release}

%description docs
%{summary}

%prep
sha1sum %{SOURCE0}
%setup -q -n %{name}-master

%build

# Needs to be a git sha1
# https://github.com/envoyproxy/envoy/blob/master/source/server/server.cc#L58
echo -n "%{git_commit}" > SOURCE_VERSION

# build twice, cause the first one often fails in a clean build cache
# ignore shutdown failures (timing out in resource-constrained environments)
%if 0%{?rhel} > 6

# naming hack ..
export mypath=$(mktemp -d)
export PATH=$mypath:$PATH
ln -sf /usr/bin/ninja-build ${mypath}/ninja # https://bugzilla.redhat.com/show_bug.cgi?id=1608565
ln -sf /usr/bin/cmake3 ${mypath}/cmake

#scl enable devtoolset-4 -- bazel build --verbose_failures //source/exe:envoy-static
scl enable devtoolset-4 -- bazel --bazelrc=/dev/null build --verbose_failures --copt "-DENVOY_IGNORE_GLIBCXX_USE_CXX11_ABI_ERROR=1" -c opt //source/exe:envoy-static ||:
scl enable devtoolset-4 -- bazel --bazelrc=/dev/null build --verbose_failures --copt "-DENVOY_IGNORE_GLIBCXX_USE_CXX11_ABI_ERROR=1" -c opt //source/exe:envoy-static
scl enable devtoolset-4 -- bazel shutdown ||:

%else
bazel --bazelrc=/dev/null build --verbose_failures -c opt //source/exe:envoy-static ||:
bazel --bazelrc=/dev/null build --verbose_failures -c opt //source/exe:envoy-static
bazel shutdown
%endif

%install
cp /dev/null docs.file-list
filelist=$(realpath docs.file-list)

rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/%{_bindir}
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/envoy
cp -pav bazel-bin/source/exe/envoy-static $RPM_BUILD_ROOT/%{_bindir}/envoy

%if 0%{?rhel} > 6
%{__install} -d -m 0755 %{buildroot}%{_unitdir} \
                        %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}@.service
%{__install} -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/%{name}-template
%{__install} -m 0755 restarter/hot-restarter.py %{buildroot}%{_bindir}
%{__install} -m 0755 %{SOURCE3} %{buildroot}%{_bindir}
%{__install} -m 0755 %{SOURCE4} %{buildroot}%{_bindir}
%{__install} -m 0755 %{SOURCE5} %{buildroot}%{_bindir}
%endif

# docs stuff
install -d -p $RPM_BUILD_ROOT/%{_datadir}/%{name}-%{version}
for file in $(find docs examples -type f) ; do
	install -d -p $RPM_BUILD_ROOT/%{_datadir}/%{name}-%{version}/$(dirname $file)
	cp -pav $file $RPM_BUILD_ROOT/%{_datadir}/%{name}-%{version}/$file
	echo "%{_datadir}/%{name}-%{version}/$file" >> $filelist
done

%post
%if 0%{?systemd_post:1}
    %systemd_post %{name}.service
%endif

%preun
%if 0%{?systemd_preun:1}
    %systemd_preun %{name}.service
%endif

%postun
%if 0%{?systemd_postun:1}
    %systemd_postun %{name}.service
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%license LICENSE
%{_bindir}/envoy
%dir %{_sysconfdir}/envoy
%if 0%{?rhel} > 6
%attr(-,root,root) %{_unitdir}/%{name}@.service
%attr(-,root,root) %{_sysconfdir}/sysconfig/%{name}-template
%{_bindir}/hot-restarter.py*
%{_bindir}/*_envoy.sh
%endif

%files docs -f docs.file-list
%doc README.md DEVELOPER.md CONTRIBUTING.md CODE_OF_CONDUCT.md
%dir %{_datadir}/%{name}-%{version}


%changelog
* Tue Apr 09 2019 Giuseppe Ragusa <giuseppe.ragusa@fastmail.fm> 1.11.0.0.git.fa69fad-2
- add systemd unit file, hot restarter and support scripts for CentOS/RHEL > 6

* Tue Apr 09 2019 Giuseppe Ragusa <giuseppe.ragusa@fastmail.fm> 1.11.0.0.git.fa69fad-1
- update from upstream (using master)

* Tue Apr 02 2019 Giuseppe Ragusa <giuseppe.ragusa@fastmail.fm> 1.10.0.0.git.fd273a6-1
- update from upstream (using master)
- drop patch

* Mon Aug 07 2017 Vincent Batts <vbatts@fedoraproject.org> 1.3.0.3.git.4837f32-1
- update from upstream

* Fri Aug 04 2017 Vincent Batts <vbatts@fedoraproject.org> 1.3.0.2.git.4837f32-1
- update from upstream
- add another digit to the version to handle version bumps due to git commits.

* Thu Aug 03 2017 Vincent Batts <vbatts@fedoraproject.org> 1.3.0.1.git.2fa90d2-1
- update from upstream
- add another digit to the version to handle version bumps due to git commits.

* Wed Aug 02 2017 Vincent Batts <vbatts@fedoraproject.org> 1.3.0.git.ee13852-1
- update from upstream
