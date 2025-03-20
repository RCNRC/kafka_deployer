from typing import Dict, Any
import time
import logging
from ..cloud_providers import CloudProvider

logger = logging.getLogger('kafka_deployer.scaler')

class AutoScaler:
    def __init__(self, cloud_provider: CloudProvider, config: Dict[str, Any]):
        self.cloud_provider = cloud_provider
        self.config = config
        self.cooldown = config.get('cooldown_seconds', 300)
        self.last_scale = 0
        self.spot_ratio = config.get('spot_ratio', 0.7)
        
    def evaluate(self, metrics: Dict[str, float]) -> None:
        if time.time() - self.last_scale < self.cooldown:
            return
            
        current_nodes = self.cloud_provider.get_current_nodes()
        target = self._calculate_target(metrics, current_nodes)
        
        if target != current_nodes:
            self._execute_scaling(target, current_nodes)
            self._optimize_instance_mix()
            
    def _calculate_target(self, metrics: Dict[str, float], current: int) -> int:
        # CPU-based scaling
        cpu_target = current
        if metrics['cpu'] > self.config['cpu_threshold']:
            cpu_target = min(current + self.config['scale_out_step'], 
                           self.config['max_nodes'])
        elif metrics['cpu'] < self.config['scale_in_threshold']:
            cpu_target = max(current - self.config['scale_in_step'],
                           self.config['min_nodes'])
                           
        # Throughput-based scaling
        throughput_target = current
        if metrics['throughput'] > self.config['throughput_threshold']:
            throughput_target = min(current + self.config['throughput_step'],
                                  self.config['max_nodes'])
                                  
        return max(cpu_target, throughput_target)
        
    def _execute_scaling(self, target: int, current: int) -> None:
        try:
            delta = target - current
            if delta > 0:
                self.cloud_provider.scale_out(delta)
            else:
                self.cloud_provider.scale_in(abs(delta))
                
            self.last_scale = time.time()
            logger.info(f"Scaled from {current} to {target} nodes")
        except Exception as e:
            logger.error(f"Scaling failed: {str(e)}")
            
    def _optimize_instance_mix(self) -> None:
        lifecycle = self.cloud_provider.get_instance_lifecycle()
        total = lifecycle['spot'] + lifecycle['on_demand']
        
        if total == 0:
            return
            
        current_ratio = lifecycle['spot'] / total
        if current_ratio < self.spot_ratio:
            self._replace_instances(int(total * (self.spot_ratio - current_ratio)))
            
    def _replace_instances(self, count: int) -> None:
        logger.info(f"Replacing {count} on-demand instances with spot")
        try:
            self.cloud_provider.scale_out(count)
            self.cloud_provider.scale_in(count)
        except Exception as e:
            logger.error(f"Instance replacement failed: {str(e)}")

