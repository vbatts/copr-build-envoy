%global git_commit ee138524fc55b4b9a9918d11976aa2b5d59cc694

%global debug_package %{nil}

# don't strip binaries at all
%global __strip /bin/true

Name:		envoy
Version:	1.3.0.git.%{git_commit}
Release:	1%{?dist}
Summary:	Envoy is an open source edge and service proxy

#Group:		
License:	Apache v2
URL:		https://github.com/lyft/envoy
#Source0:	https://github.com/lyft/%{name}/archive/v%{version}.tar.gz
Source0:	https://github.com/lyft/envoy/archive/%{git_commit}.zip

# see https://copr.fedorainfracloud.org/coprs/vbatts/bazel/
BuildRequires:	bazel

BuildRequires:	wget
BuildRequires:	make
BuildRequires:	git
BuildRequires:	java-1.8.0-openjdk-devel
BuildRequires:	bc
BuildRequires:	libtool
BuildRequires:	zip
BuildRequires:	unzip
BuildRequires:	gdb
BuildRequires:	strace
#BuildRequires:	python2-pip
BuildRequires:	python-virtualenv
BuildRequires:	which
BuildRequires:	golang
BuildRequires:  clang

%if 0%{?rhel} > 6
BuildRequires:	centos-release-scl
BuildRequires:	devtoolset-4-gcc-c++

## TODO make an rpm from the newer cmake in the copr repo
#BuildRequires:  cmake-3.4
%else
BuildRequires:	gcc-c++
BuildRequires:  libstdc++-static
BuildRequires:	cmake
%endif

#Requires:	

%description
%{summary}.

%prep
%setup -q -c -n %{name}-%{git_commit}

%build

pushd %{name}-%{git_commit}

%if 0%{?rhel} > 6
scl enable devtoolset-4 -- bazel build //source/... ||:
scl enable devtoolset-4 -- bazel build //source/...
%else
bazel build //source/... ||:
bazel build //source/...
%endif

%install
pushd %{name}-%{git_commit}
#%make_install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/%{_bindir}
cp -pav bazel-bin/source/exe/envoy-static $RPM_BUILD_ROOT/%{_bindir}/envoy


%files
%doc

%{_bindir}/envoy


%changelog
* Wed Aug 02 2017 Vincent Batts <vbatts@fedoraproject.org> 1.3.0-1
- update from upstream
