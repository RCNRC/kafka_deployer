# Cloud Native Auto-scaling Integration

## Spot Instance Management
```yaml
scaling:
  spot:
    enabled: true
    max_price: 0.25  # Max bid price as percentage of on-demand
    replacement_timeout: 300  # Seconds to replace interrupted instances
    fallback: true  # Use on-demand if spot unavailable
```

## Multi-cloud Cost Optimization
```python
# Select cheapest provider for scaling
prices = {
    'aws': aws_provider.get_pricing_data(),
    'gcp': gcp_provider.get_pricing_data()
}
cheapest = min(prices, key=lambda k: prices[k]['spot'])
cloud_provider = providers[cheapest]
```

## Monitoring Metrics
- `kafka_scaling_events_total`
- `kafka_spot_instance_ratio`
- `kafka_scaling_cost_impact`

## Spot Interruption Handling
```python
# AWS example using instance metadata service
def check_spot_interruption():
    try:
        response = requests.get(
            'http://169.254.169.254/latest/meta-data/spot/instance-action',
            timeout=2
        )
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        return False
```

## Hybrid Scaling Example
```yaml
scaling:
  strategy: hybrid
  rules:
    - metric: cpu
      threshold: 75
      duration: 300
      action: add:2
      priority: 100
    - metric: cost
      threshold: 0.50
      action: replace_spot
      priority: 200
```

