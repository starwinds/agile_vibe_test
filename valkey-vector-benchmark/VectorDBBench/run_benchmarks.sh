#!/bin/bash
set -e

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_VECTORDB_BENCH=1.0.0
pip install valkey
pip install -e .

# Function to wait for port
wait_for_port() {
    local host=$1
    local port=$2
    local timeout=$3
    local start_time=$(date +%s)
    
    echo "Waiting for $host:$port..."
    while ! nc -z $host $port; do
        current_time=$(date +%s)
        elapsed=$((current_time - start_time))
        if [ $elapsed -ge $timeout ]; then
            echo "Timeout waiting for $host:$port"
            exit 1
        fi
        sleep 1
    done
    echo "$host:$port is up."
}

# Run Cluster Benchmark
echo "----------------------------------------------------------------"
echo "Starting Valkey Cluster Benchmark"
echo "----------------------------------------------------------------"
docker-compose -f docker-compose.benchmark-cluster.yml up -d

echo "Waiting for Cluster to initialize..."
wait_for_port 127.0.0.1 7000 60
sleep 30 # Allow cluster-init to finish

echo "Building Benchmark Runner..."
docker build -t vectordbbench-runner -f Dockerfile.runner .

echo "Running Cluster Benchmark in Docker..."
# We use host networking or attach to the cluster network.
# Since cluster nodes are in valkey-cluster-net, we attach to it.
# We also need to map the results directory back to host.

docker run --rm \
    --network vectordbbench_valkey-cluster-net \
    -v $(pwd)/vectordb_bench/results:/app/vectordb_bench/results \
    -v $(pwd)/logs:/app/logs \
    vectordbbench-runner \
    "vectordbbench valkey \
    --db-label valkey-cluster \
    --deployment-type CLUSTER \
    --nodes vectordbbench-node-7000-1:6379 \
    --password '' \
    --case-type Performance1536D50K \
    --m 16 --ef-construction 200 --ef-runtime 10"

echo "Stopping Valkey Cluster..."
docker-compose -f docker-compose.benchmark-cluster.yml down -v

# Run HA Benchmark
# echo "----------------------------------------------------------------"
# echo "Starting Valkey HA Benchmark"
# echo "----------------------------------------------------------------"
# docker-compose -f docker-compose.benchmark-ha.yml up -d

# echo "Waiting for Sentinel..."
# wait_for_port 127.0.0.1 26379 60
# sleep 30 # Allow sentinel to stabilize

# echo "Running HA Benchmark..."
# vectordbbench valkey \
#     --db-label valkey-ha \
#     --deployment-type SENTINEL \
#     --nodes 127.0.0.1:26379 \
#     --service-name myvalkey \
#     --password "" \
#     --case-type Performance1536D50K \
#     --m 16 --ef-construction 200 --ef-runtime 10

# echo "Stopping Valkey HA..."
# docker-compose -f docker-compose.benchmark-ha.yml down -v

echo "Benchmarks completed successfully."
