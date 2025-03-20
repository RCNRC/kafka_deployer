# Automated Monitoring System

## Deployment
Enable monitoring in values.yaml:
```yaml
monitoring:
  enabled: true
  grafana:
    admin_password: "securepass"
  prometheus:
    retention: 15d
  alerts:
    enabled: true
```

Deploy with monitoring:
```bash
helm install kafka-cluster charts/kafka --set monitoring.enabled=true
```

## Features
- Pre-configured dashboards for:
  - JVM Metrics
  - Consumer Lag
  - Topic Throughput
  - Disk Utilization
- Automatic alerting for:
  - Under-replicated Partitions
  - Offline Partitions
  - High Consumer Lag
  - Broker Down

## Cloud Integration
AWS CloudWatch metrics:
```yaml
monitoring:
  cloudwatch:
    enabled: true
    aws_region: us-east-1
    metrics:
      - AWS/Kafka
      - AWS/EC2
```

GCP Stackdriver integration:
```yaml
monitoring:
  stackdriver:
    enabled: true
    project_id: my-project
```

