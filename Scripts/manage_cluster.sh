#!/bin/bash

case $1 in
    start)
        sudo systemctl start kubelet
        echo "Kubernetes cluster started"
        ;;
    stop)
        sudo systemctl stop kubelet
        echo "Kubernetes cluster stopped"
        ;;
    scale)
        if [ -z "$2" ]; then
            echo "Usage: $0 scale <replicas>"
            exit 1
        fi
        kubectl scale deployment/my-deployment --replicas=$2
        echo "Kubernetes cluster scaled to $2 replicas"
        ;;
    *)
        echo "Usage: $0 {start|stop|scale <replicas>}"
        exit 1
        ;;
esac
