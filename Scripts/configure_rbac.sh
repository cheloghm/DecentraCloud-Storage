#!/bin/bash

kubectl create clusterrolebinding permissive-binding \
    --clusterrole=cluster-admin \
    --group=system:serviceaccounts

echo "RBAC configuration applied"
