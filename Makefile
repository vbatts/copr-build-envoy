
pkgname := envoy
specname ?= $(pkgname).spec
pwd := $(shell pwd)
NAME ?= $(shell rpmspec -q --qf "%{name}\n" $(specname) |head -1)
VERSION ?= $(shell rpmspec -q --qf "%{version}\n" $(specname) |head -1)
RELEASE ?= $(shell rpmspec -q --qf "%{release}\n" $(specname) | head -1)
NVR := $(NAME)-$(VERSION)-$(RELEASE)

default: srpm

name:
	@echo $(NVR)

all: rpm srpm

rpm:
	rpmbuild \
                --define '_sourcedir $(pwd)' \
                --define '_specdir $(pwd)' \
                --define '_builddir $(pwd)' \
                --define '_srcrpmdir $(pwd)' \
                --define '_rpmdir $(pwd)' \
                --nodeps \
                -bb ./$(specname)

srpm: $(NVR).src.rpm

$(NVR).src.rpm: $(specname) $(wildcard *.diff)
	rpmbuild \
                --define '_sourcedir $(pwd)' \
                --define '_specdir $(pwd)' \
                --define '_builddir $(pwd)' \
                --define '_srcrpmdir $(pwd)' \
                --define '_rpmdir $(pwd)' \
                --nodeps \
                -bs ./$(specname)

bazel:
	dnf copr enable -y vbatts/bazel

builddep: bazel $(NVR).src.rpm
	dnf builddep -y $(NVR).src.rpm

rebuild: builddep
	rpmbuild --rebuild $(NVR).src.rpm

clean:
	rm -rf *~ *.rpm noarch

