## Cloud Provider Integration

### AWS CloudWatch
```yaml
monitoring:
  cloudwatch:
    enabled: true
    aws_region: us-east-1
    metrics:
      - AWS/Kafka
      - AWS/EC2
```

### GCP Stackdriver
```yaml
monitoring:
  stackdriver:
    enabled: true
    project_id: my-project
    metrics:
      - kafka.googleapis.com/topic/byte_rate
      - kafka.googleapis.com/consumer_lag
```

## Alert Management
Pre-configured alerts include:
- Under-replicated partitions
- Offline partitions
- High consumer lag (>10k messages)
- Broker down
- Disk space critical

Customize thresholds:
```yaml
monitoring:
  alerts:
    consumer_lag_threshold: 5000
    disk_alert_percent: 90
```

