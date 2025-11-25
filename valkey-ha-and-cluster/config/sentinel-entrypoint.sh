#!/bin/sh
# sentinel-entrypoint.sh

# Wait until the master is resolvable
until ping -c 1 valkey-master; do
  echo "Waiting for valkey-master..."
  sleep 1
done

# Give a bit more time for DNS to be fully propagated
sleep 2

# Start the sentinel
exec valkey-sentinel /etc/valkey/sentinel.conf