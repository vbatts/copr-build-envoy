#!/bin/bash
set -e
/usr/bin/envoy -c $CONFIG_FILE --mode validate --base-id $BASE_ID
if [ ! $? ]; then
	echo "File $CONFIG_FILE failed validation!" 1>&2
	exit 1;
fi
exec /usr/bin/envoy -c $CONFIG_FILE --restart-epoch $RESTART_EPOCH $ENVOY_OPTIONS
