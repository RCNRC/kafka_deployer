import boto3
from botocore.exceptions import ClientError
from .base import CloudProvider, CloudError

class AWSCloudProvider(CloudProvider):
    """AWS implementation using MSK and EC2"""
    
    REQUIRED_CONFIG = ['region', 'instance_type', 'ssh_key_name']
    
    def configure_autoscaling(self, scaling_policy: Dict[str, Any]):
        autoscaling = boto3.client('autoscaling', region_name=self.config['region'])
        try:
            autoscaling.put_scaling_policy(
                AutoScalingGroupName=self.config['auto_scaling_group'],
                PolicyName='kafka-cpu-scaling',
                PolicyType='TargetTrackingScaling',
                TargetTrackingConfiguration={
                    'PredefinedMetricSpecification': {
                        'PredefinedMetricType': 'ASGAverageCPUUtilization'
                    },
                    'TargetValue': 70.0
                }
            )
        except ClientError as e:
            raise CloudError(3003, f"Auto-scaling configuration failed: {str(e)}")

    def handle_scaling_event(self, metrics: Dict[str, float]):
        current_nodes = len(self.get_active_nodes())
        if metrics['cpu_usage'] > 80:
            self.scale_out(1)
        elif metrics['cpu_usage'] < 30 and current_nodes > 3:
            self.scale_in(1)

