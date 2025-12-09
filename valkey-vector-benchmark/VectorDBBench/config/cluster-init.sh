#!/bin/sh
echo ">>> Waiting for nodes to be up..."
sleep 10

echo ">>> Initiating Valkey Cluster..."
redis-cli --cluster create \
  node-7000:6379 \
  node-7001:6379 \
  node-7002:6379 \
  node-7003:6379 \
  node-7004:6379 \
  node-7005:6379 \
  --cluster-replicas 1 \
  --cluster-yes

echo ">>> Valkey Cluster initialized."

