class AzureCloudProvider(CloudProvider):
    def get_instance_cost(self, instance_type: str) -> float:
        pricing = {
            'Standard_D2s_v3': 0.114,
            'Standard_E4s_v3': 0.252
        }
        return pricing.get(instance_type, 0.0)

    def get_instance_specs(self, instance_type: str) -> Dict[str, Any]:
        specs = {
            'Standard_D2s_v3': {'vcpu': 2, 'mem_gb': 8, 'network': 'Moderate'},
            'Standard_E4s_v3': {'vcpu': 4, 'mem_gb': 32, 'network': 'High'}
        }
        return specs.get(instance_type, {})

