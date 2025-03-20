# Kafka Deployment Tool

## New Containerized Deployment
```bash
# Install with Helm
helm repo add kafka-charts path/to/charts
helm install my-kafka kafka-charts/kafka

# Verify pods
kubectl get pods -l app.kubernetes.io/name=kafka
```

See [container deployment guide](/docs/CONTAINER_DEPLOYMENT.md) for details.
