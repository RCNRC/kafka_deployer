from google.cloud import compute_v1
from .base import CloudProvider, CloudError
from typing import Dict, Any
import logging

logger = logging.getLogger('kafka_deployer.gcp')

class GCPCloudProvider(CloudProvider):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = compute_v1.InstanceGroupManagersClient()
        self.spot_suffix = "-spot"

    def scale_out(self, count: int, spot: bool = False) -> None:
        if spot:
            self._create_spot_instances(count)
        else:
            self._scale_managed_group(count)

    def _scale_managed_group(self, count: int):
        current = self.get_current_nodes()
        new_size = min(current + count, self.config['max_nodes'])
        self.client.resize(
            project=self.config['project_id'],
            zone=self.config['zone'],
            instance_group_manager=self.config['instance_group'],
            size=new_size
        )

    def _create_spot_instances(self, count: int):
        template = self.config['instance_group'] + self.spot_suffix
        config = {
            "name": f"spot-instance-{uuid.uuid4().hex}",
            "source_instance_template": template,
            "count": count,
            "minimal_action": "CREATE",
            "scheduling": {"preemptible": True}
        }
        
        operation = self.client.insert(
            project=self.config['project_id'],
            zone=self.config['zone'],
            instance_group_manager=self.config['instance_group'],
            instance_group_managers_create_instances_request=config
        )
        operation.result()
        logger.info(f"Created {count} spot instances")

    def handle_preemptions(self):
        instances = self.client.list_managed_instances(
            project=self.config['project_id'],
            zone=self.config['zone'],
            instance_group_manager=self.config['instance_group']
        )
        
        preempted = [i for i in instances if i.status == "PREEMPTED"]
        if preempted:
            logger.warning(f"Replacing {len(preempted)} preempted instances")
            self.scale_out(len(preempted))
            self._delete_instances([i.instance for i in preempted])

    def _delete_instances(self, instance_urls: list):
        self.client.delete_instances(
            project=self.config['project_id'],
            zone=self.config['zone'],
            instance_group_manager=self.config['instance_group'],
            instance_group_managers_delete_instances_request={
                "instances": instance_urls
            }
        )

