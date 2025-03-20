class AWSCloudProvider(CloudProvider):
    def get_instance_cost(self, instance_type: str) -> float:
        pricing = {
            't3.medium': 0.0416,
            'm5.large': 0.096,
            'r5.xlarge': 0.252
        }
        return pricing.get(instance_type, 0.0)

    def get_instance_specs(self, instance_type: str) -> Dict[str, Any]:
        specs = {
            't3.medium': {'vcpu': 2, 'mem_gb': 4, 'network': 'up to 5 Gbps'},
            'm5.large': {'vcpu': 2, 'mem_gb': 8, 'network': '10 Gbps'}
        }
        return specs.get(instance_type, {})

