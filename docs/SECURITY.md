## Automatic Certificate Renewal

The system performs daily checks and automatically renews certificates when:
- Certificates expire in less than 30 days (configurable via `renewal_threshold_days`)
- Certificate chain validation fails
- New nodes are added to the cluster

Integration with monitoring systems:
```yaml
alerting:
  ssl_expiry:
    enabled: true
    warning_days: 30
    critical_days: 7
```

Cloud-managed certificates:
```yaml
aws:
  use_acm: true
  acm_arn: "arn:aws:acm:..."
gcp:
  managed_certs: true
  certificate_name: "kafka-cluster-cert"
```
