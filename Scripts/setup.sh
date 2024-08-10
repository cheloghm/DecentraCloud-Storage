#!/bin/bash

# Update and install basic dependencies
sudo apt-get update
sudo apt-get install -y apt-transport-https curl python3 python3-pip git

# Install Docker
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Add Kubernetes repository and install kubeadm, kubelet, kubectl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# Install necessary Python packages
pip3 install -r requirements.txt

# Make sure all scripts are executable
chmod +x Scripts/*.sh

echo "Setup complete. You can now run the storage node."
