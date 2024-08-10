#!/bin/bash

# Install Flannel
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

# OR Install Calico
# kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

echo "Network plugin installed successfully"
