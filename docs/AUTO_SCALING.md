# Auto-scaling Implementation Guide

## Configuration
Enable auto-scaling in values.yaml:
```yaml
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPU: 80
  targetThroughput: 1000000
```

## Cloud Provider Setup

### AWS
```yaml
aws:
  auto_scaling_group: kafka-asg
  region: us-east-1
  scaling_policies:
    cpu_threshold: 80
    scale_out_step: 1
    scale_in_threshold: 30
    scale_in_step: 1
    max_nodes: 10
    min_nodes: 3
```

### GCP
```yaml
gcp:
  instance_group: kafka-ig
  zone: us-central1-a
  scaling_policies:
    throughput_threshold: 1000000
    throughput_scale_step: 2
    max_nodes: 15
    min_nodes: 5
```

## Monitoring Integration
Scaling decisions are based on Prometheus metrics:
- CPU Usage (container_cpu_usage_seconds_total)
- Network Throughput (kafka_network_throughput_bytes)
- Consumer Lag (kafka_consumer_lag_messages)

## Custom Scaling Policies
Override default policies via CLI:
```bash
python -m src.cli.cli set-policy --metric cpu --threshold 85 --step 2
```

