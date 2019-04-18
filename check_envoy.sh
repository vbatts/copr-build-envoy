#!/bin/bash
set -e
if [ -s $CONFIG_FILE ]; then
	/usr/bin/envoy -c $CONFIG_FILE --mode validate
else
	echo "File $CONFIG_FILE is empty!" 1>&2
	exit 1;
fi
