from azure.mgmt.compute import ComputeManagementClient
from azure.identity import DefaultAzureCredential
from .base import CloudProvider, CloudError
from typing import Dict, Any

class AzureCloudProvider(CloudProvider):
    """Azure implementation using VM Scale Sets"""
    
    def scale_out(self, count: int):
        client = ComputeManagementClient(
            DefaultAzureCredential(),
            self.config['subscription_id']
        )
        current = self.get_current_nodes()
        new_capacity = min(current + count, self.config['auto_scaling']['max_nodes'])
        client.virtual_machine_scale_sets.update(
            self.config['resource_group'],
            self.config['scale_set_name'],
            {'sku': {'capacity': new_capacity}}
        )

    def scale_in(self, count: int):
        client = ComputeManagementClient(
            DefaultAzureCredential(),
            self.config['subscription_id']
        )
        current = self.get_current_nodes()
        new_capacity = max(current - count, self.config['auto_scaling']['min_nodes'])
        client.virtual_machine_scale_sets.update(
            self.config['resource_group'],
            self.config['scale_set_name'],
            {'sku': {'capacity': new_capacity}}
        )

    def get_current_nodes(self) -> int:
        client = ComputeManagementClient(
            DefaultAzureCredential(),
            self.config['subscription_id']
        )
        scale_set = client.virtual_machine_scale_sets.get(
            self.config['resource_group'],
            self.config['scale_set_name']
        )
        return scale_set.sku.capacity

