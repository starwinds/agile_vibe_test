#!/bin/sh
echo ">>> Waiting for nodes to be up..."
sleep 10

echo ">>> Initiating Valkey Cluster..."
valkey-cli --cluster create \
  127.0.0.1:7000 \
  127.0.0.1:7001 \
  127.0.0.1:7002 \
  127.0.0.1:7003 \
  127.0.0.1:7004 \
  127.0.0.1:7005 \
  --cluster-replicas 1 \
  --cluster-yes

echo ">>> Valkey Cluster initialized."
