# this is just a monotonically increasing number to preceed the git hash, to get incremented on every git bump
%global git_bump		3
%global git_commit		c473b56a87560bb08916a2d6835e82710356d193
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
Version:	1.4.0.%{git_bump}.git.%{git_shortcommit}
Release:	2%{?dist}
Summary:	Envoy is an open source edge and service proxy

#Group:		
License:	Apache v2
URL:		https://github.com/envoyproxy/envoy
#Source0:	https://github.com/envoyproxy/%{name}/archive/v%{version}.tar.gz
Source0:	https://github.com/envoyproxy/envoy/archive/%{git_commit}.zip

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
BuildRequires:	cmake
BuildRequires:	coreutils

%if 0%{?rhel} > 6
BuildRequires:	centos-release-scl
BuildRequires:	devtoolset-4-gcc-c++
%else
BuildRequires:	gcc-c++
BuildRequires:  libstdc++-static
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
%setup -q -n %{name}-%{git_commit}

%build

# Needs to be a git sha1
# https://github.com/envoyproxy/envoy/blob/master/source/server/server.cc#L58
echo -n "%{git_commit}" > SOURCE_VERSION

## upstream's recommendation for a release build
#bazel --bazelrc=/dev/null build -c opt //source/exe:envoy-static.stripped.stamped

# build twice, cause the first one often fails in a clean build cache
%if 0%{?rhel} > 6
#scl enable devtoolset-4 -- bazel build --verbose_failures //source/exe:envoy-static
scl enable devtoolset-4 -- bazel --bazelrc=/dev/null build --verbose_failures -c opt //source/exe:envoy-static.stripped.stamped ||:
scl enable devtoolset-4 -- bazel --bazelrc=/dev/null build --verbose_failures -c opt //source/exe:envoy-static.stripped.stamped
scl enable devtoolset-4 -- bazel shutdown
%else
#bazel build --verbose_failures //source/exe:envoy-static
bazel --bazelrc=/dev/null build --verbose_failures -c opt //source/exe:envoy-static.stripped.stamped ||:
bazel --bazelrc=/dev/null build --verbose_failures -c opt //source/exe:envoy-static.stripped.stamped
bazel shutdown
%endif

%install
cp /dev/null docs.file-list
filelist=$(realpath docs.file-list)

rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/%{_bindir}
cp -pav bazel-bin/source/exe/envoy-static $RPM_BUILD_ROOT/%{_bindir}/envoy

# docs stuff
install -d -p $RPM_BUILD_ROOT/%{_datadir}/%{name}-%{version}
for file in $(find docs examples -type f) ; do
	install -d -p $RPM_BUILD_ROOT/%{_datadir}/%{name}-%{version}/$(dirname $file)
	cp -pav $file $RPM_BUILD_ROOT/%{_datadir}/%{name}-%{version}/$file
	echo "%{_datadir}/%{name}-%{version}/$file" >> $filelist
done

%files
%license LICENSE
%{_bindir}/envoy

%files docs -f docs.file-list
%doc README.md DEVELOPER.md CONTRIBUTING.md CODE_OF_CONDUCT.md
%dir %{_datadir}/%{name}-%{version}


%changelog
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
