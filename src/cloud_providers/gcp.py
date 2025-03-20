class GCPCloudProvider(CloudProvider):
    def get_instance_cost(self, instance_type: str) -> float:
        pricing = {
            'n2-standard-2': 0.0971,
            'n2-highmem-4': 0.1943
        }
        return pricing.get(instance_type, 0.0)

    def get_instance_specs(self, instance_type: str) -> Dict[str, Any]:
        specs = {
            'n2-standard-2': {'vcpu': 2, 'mem_gb': 8, 'network': '10 Gbps'},
            'n2-highmem-4': {'vcpu': 4, 'mem_gb': 16, 'network': '10 Gbps'}
        }
        return specs.get(instance_type, {})

