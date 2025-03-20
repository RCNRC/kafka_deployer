# Performance Tuning Guide

## Auto-Optimization Rules
1. When JVM memory usage exceeds 80%:
   - Increase `num.io.threads`
   - Reduce `log.flush.interval.messages`
   
2. When consumer lag > 1000 messages:
   - Increase `num.partitions`
   - Adjust `fetch.max.bytes`

## Monitoring Setup
To enable performance monitoring:
1. Install Prometheus and Grafana using:
```bash
ansible-playbook monitoring.yml
```
2. Import dashboard template from `configs/grafana/`

## Auto-Scaling Configuration
Configure threshold values in cloud provider config:
```yaml
aws:
  auto_scaling:
    cpu_threshold: 80
    scale_out_step: 1
    scale_in_step: 1
```

