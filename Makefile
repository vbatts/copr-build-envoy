
CWD := $(shell pwd)

srpm: envoy.spec $(wildcard *.diff)
	rpmbuild --define "_topdir $(CWD)" --define "_sourcedir $(CWD)" -bs ./envoy.spec
