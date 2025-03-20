from typing import Dict, Any
import time
import logging
from ..cloud_providers import CloudProvider
from prometheus_client import Gauge

logger = logging.getLogger('kafka_deployer.scaler')

class AutoScaler:
    def __init__(self, cloud_provider: CloudProvider, config: Dict[str, Any]):
        self.cloud_provider = cloud_provider
        self.config = config
        self.cooldown = config.get('cooldown_seconds', 300)
        self.last_scale = 0
        self.spot_ratio = config.get('spot_ratio', 0.7)
        
        # Prometheus metrics
        self.scaling_events = Gauge('kafka_scaling_events_total', 'Total scaling events')
        self.spot_ratio_metric = Gauge('kafka_spot_instance_ratio', 'Current spot instance ratio')
        self.scaling_cost = Gauge('kafka_scaling_cost_impact', 'Estimated hourly cost impact')

    def evaluate(self, metrics: Dict[str, float]) -> None:
        if time.time() - self.last_scale < self.cooldown:
            return
            
        pricing = self.cloud_provider.get_pricing_data()
        current_nodes = self.cloud_provider.get_current_nodes()
        target = self._calculate_target(metrics, current_nodes, pricing)
        
        if target != current_nodes:
            spot_count = self._calculate_spot_capacity(target, pricing)
            self._execute_scaling(target, spot_count)
            self._update_metrics(target, spot_count, pricing)
            
        self._handle_instance_lifecycle()

    def _calculate_spot_capacity(self, target: int, pricing: Dict[str, float]) -> int:
        if pricing['spot'] < pricing['on_demand'] * 0.5:
            return min(int(target * 1.2), self.config['max_nodes'])
        return 0

    def _execute_scaling(self, target: int, spot_count: int):
        delta = target - self.cloud_provider.get_current_nodes()
        if delta > 0:
            self.cloud_provider.scale_out(delta, spot=(spot_count > 0))
        else:
            self.cloud_provider.scale_in(abs(delta))
            
        self.last_scale = time.time()
        self.scaling_events.inc()

    def _update_metrics(self, target: int, spot_count: int, pricing: Dict[str, float]):
        lifecycle = self.cloud_provider.get_instance_lifecycle()
        total = lifecycle['spot'] + lifecycle['on_demand']
        self.spot_ratio_metric.set(lifecycle['spot'] / total if total > 0 else 0)
        
        cost = (lifecycle['spot'] * pricing['spot'] + 
               lifecycle['on_demand'] * pricing['on_demand'])
        self.scaling_cost.set(cost)

    def _handle_instance_lifecycle(self):
        try:
            if isinstance(self.cloud_provider, AWSCloudProvider):
                self.cloud_provider.handle_spot_interruptions()
            elif isinstance(self.cloud_provider, GCPCloudProvider):
                self.cloud_provider.handle_preemptions()
        except Exception as e:
            logger.error(f"Instance lifecycle handling failed: {str(e)}")

