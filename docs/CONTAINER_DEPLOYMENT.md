# Containerized Deployment Guide

## Prerequisites
- Kubernetes cluster (v1.19+)
- Helm 3
- Docker

## Steps

1. Build Docker images:
```bash
docker build -t myrepo/kafka:3.2.0 -f docker/kafka/Dockerfile .
docker build -t myrepo/zookeeper:3.7.1 -f docker/zookeeper/Dockerfile .
```

2. Install Helm chart:
```bash
helm install kafka-cluster charts/kafka \
  --set replicaCount=5 \
  --set persistence.size=20Gi
```

3. Verify deployment:
```bash
kubectl get pods -l app=kafka
kubectl exec -it kafka-cluster-kafka-0 -- kafka-topics --list
```

## Monitoring Integration
The Helm chart includes Prometheus annotations. To enable monitoring:
```yaml
monitoring:
  prometheus: true
```

## Persistent Storage
Configure storage class and size in values.yaml:
```yaml
persistence:
  storageClass: gp2
  size: 100Gi
```
