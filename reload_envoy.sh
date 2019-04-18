#!/bin/bash
set -e
MAIN_PID=$1
/usr/bin/envoy -c $CONFIG_FILE --mode validate --base-id $BASE_ID
if [ ! $? ]; then
	echo "File $CONFIG_FILE failed validation!" 1>&2
	exit 1;
fi
/bin/kill -1 $MAIN_PID
