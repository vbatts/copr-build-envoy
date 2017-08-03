## waiting on 1.4.0 to be released, so using the HEAD commit from 2017-08-02
%global git_commit ee138524fc55b4b9a9918d11976aa2b5d59cc694
%global git_shortcommit     %(c=%{git_commit}; echo ${c:0:7})

# don't strip binaries at all
%global __strip /bin/true
%global debug_package %{nil}

Name:		envoy
Version:	1.3.0.git.%{git_shortcommit}
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
%setup -q -c -n %{name}-%{git_commit}

%build

pushd %{name}-%{git_commit}

# build twice, cause the first one often fails in a clean build cache
%if 0%{?rhel} > 6
scl enable devtoolset-4 -- bazel build //source/... ||:
scl enable devtoolset-4 -- bazel build //source/...
%else
bazel build //source/... ||:
bazel build //source/...
%endif

%install
cp /dev/null docs.file-list
filelist=$(realpath docs.file-list)
pushd %{name}-%{git_commit}
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
%copying LICENSE
%{_bindir}/envoy

%files docs -f docs.file-list
%doc README.md DEVELOPER.md CONTRIBUTING.md CODE_OF_CONDUCT.md
%dir %{_datadir}/%{name}-%{version}


%changelog
* Wed Aug 02 2017 Vincent Batts <vbatts@fedoraproject.org> 1.3.0.git.ee13852-1
- update from upstream
