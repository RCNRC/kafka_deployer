from google.cloud import compute_v1
from .base import CloudProvider, CloudError
from typing import Dict, Any

class GCPCloudProvider(CloudProvider):
    """GCP implementation using Compute Engine"""
    
    def scale_out(self, count: int):
        client = compute_v1.InstanceGroupManagersClient()
        current = self.get_current_nodes()
        new_size = min(current + count, self.config['auto_scaling']['max_nodes'])
        client.resize(
            project=self.config['project_id'],
            zone=self.config['zone'],
            instance_group_manager=self.config['instance_group'],
            size=new_size
        )

    def scale_in(self, count: int):
        client = compute_v1.InstanceGroupManagersClient()
        current = self.get_current_nodes()
        new_size = max(current - count, self.config['auto_scaling']['min_nodes'])
        client.resize(
            project=self.config['project_id'],
            zone=self.config['zone'],
            instance_group_manager=self.config['instance_group'],
            size=new_size
        )

    def get_current_nodes(self) -> int:
        client = compute_v1.InstanceGroupManagersClient()
        ig = client.get(
            project=self.config['project_id'],
            zone=self.config['zone'],
            instance_group_manager=self.config['instance_group']
        )
        return ig.target_size

