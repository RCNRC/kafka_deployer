# Cloud Native Auto-scaling Integration

## Supported Providers
- AWS Auto Scaling Groups
- Google Cloud Managed Instance Groups  
- Azure Virtual Machine Scale Sets
- Kubernetes Horizontal Pod Autoscaler

## Configuration Examples

### AWS Auto Scaling
```yaml
aws:
  region: us-east-1
  auto_scaling_group: kafka-asg
  instance_type: m5.large
  scaling:
    min_nodes: 3
    max_nodes: 15
    cpu_threshold: 75
    scale_out_step: 2
    spot_ratio: 0.8
  pricing:
    on_demand: 0.12
    spot: 0.04
    reserved: 0.08
```

### Azure VM Scale Sets
```yaml
azure:
  subscription_id: "your-sub-id"
  resource_group: kafka-rg  
  scale_set_name: kafka-ss
  vm_sku: Standard_D2s_v3
  scaling:
    min_nodes: 5
    max_nodes: 20
    throughput_threshold: 500000
```

## Spot Instance Handling
1. Configure spot instance ratio (0-1)
2. Automatic instance replacement
3. Preemption monitoring
4. Fallback to on-demand instances

## Pricing Integration
```python
# Get cost-aware scaling recommendations
pricing = cloud_provider.get_pricing_data()
if pricing['spot'] < 0.5 * pricing['on_demand']:
    prefer_spot_instances()
```

## Monitoring Integration
Track scaling events in Prometheus:
- kafka_scaling_events_total
- kafka_instance_spot_ratio
- kafka_scaling_cost_impact

