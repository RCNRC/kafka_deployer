from typing import Dict, Any
from prometheus_client import CollectorRegistry
from ..cloud_providers import get_cloud_provider
import logging
import time

logger = logging.getLogger('kafka_deployer.scaler')

class AutoScaler:
    def __init__(self, config: Dict[str, Any]):
        self.cloud_provider = get_cloud_provider(config)
        self.scaling_policies = config.get('scaling_policies', {})
        self.cooldown_period = config.get('cooldown_seconds', 300)
        self.last_scale_time = 0
        
    def evaluate_metrics(self, metrics: Dict[str, float]) -> None:
        if time.time() - self.last_scale_time < self.cooldown_period:
            return
            
        current_nodes = self.cloud_provider.get_current_nodes()
        desired_nodes = current_nodes
        
        # CPU-based scaling
        cpu_threshold = self.scaling_policies.get('cpu_threshold', 80)
        if metrics['cpu_usage'] > cpu_threshold:
            desired_nodes = min(
                current_nodes + self.scaling_policies.get('scale_out_step', 1),
                self.scaling_policies['max_nodes']
            )
        elif metrics['cpu_usage'] < self.scaling_policies.get('scale_in_threshold', 30):
            desired_nodes = max(
                current_nodes - self.scaling_policies.get('scale_in_step', 1),
                self.scaling_policies['min_nodes']
            )
            
        # Throughput-based scaling
        throughput_threshold = self.scaling_policies.get('throughput_threshold', 1000000)
        if metrics['network_throughput'] > throughput_threshold:
            desired_nodes = min(
                desired_nodes + self.scaling_policies.get('throughput_scale_step', 1),
                self.scaling_policies['max_nodes']
            )
            
        if desired_nodes != current_nodes:
            self.execute_scaling(desired_nodes, current_nodes)
            
    def execute_scaling(self, desired: int, current: int) -> None:
        try:
            if desired > current:
                self.cloud_provider.scale_out(desired - current)
                logger.info(f"Scaling out from {current} to {desired} nodes")
            else:
                self.cloud_provider.scale_in(current - desired)
                logger.info(f"Scaling in from {current} to {desired} nodes")
                
            self.last_scale_time = time.time()
        except Exception as e:
            logger.error(f"Scaling failed: {str(e)}")

