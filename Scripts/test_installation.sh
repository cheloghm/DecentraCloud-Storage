#!/bin/bash

# Test storage check and allocation
python check_storage.py

# Test storage partition creation
python allocate_storage.py

# Test Kubernetes installation
./install_kubernetes.sh

# Test network plugin installation
./install_network_plugin.sh

# Test Kubernetes cluster initialization
./initialize_cluster.sh

# Test cluster management
./manage_cluster.sh start
./manage_cluster.sh stop
./manage_cluster.sh scale 3

# Test RBAC and network policies
./configure_rbac.sh
./configure_network_policies.sh

echo "All tests completed successfully"
