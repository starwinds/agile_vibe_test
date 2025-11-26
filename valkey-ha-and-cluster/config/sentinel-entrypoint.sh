#!/bin/sh
# sentinel-entrypoint.sh

# Wait until the master is resolvable
until ping -c 1 valkey-master; do
  echo "Waiting for valkey-master..."
  sleep 1
done

# Get the master IP dynamically
MASTER_IP=$(getent hosts valkey-master | awk '{ print $1 }')
echo "Resolved valkey-master to $MASTER_IP"

# Create a temporary sentinel config with the resolved IP
cat > /tmp/sentinel.conf << EOF
sentinel monitor myvalkey $MASTER_IP 6379 2
sentinel down-after-milliseconds myvalkey 2000
sentinel failover-timeout myvalkey 10000
sentinel parallel-syncs myvalkey 1
EOF

# Start the sentinel with the dynamic config
exec valkey-sentinel /tmp/sentinel.conf