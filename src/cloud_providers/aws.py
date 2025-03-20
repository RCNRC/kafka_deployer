import boto3
from botocore.exceptions import ClientError
from .base import CloudProvider, CloudError
from typing import Dict, Any

class AWSCloudProvider(CloudProvider):
    """AWS implementation using MSK and EC2"""
    
    REQUIRED_CONFIG = ['region', 'instance_type', 'ssh_key_name', 'auto_scaling']
    
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
                    'TargetValue': scaling_policy.get('cpu_threshold', 70.0)
                }
            )
        except ClientError as e:
            raise CloudError(3003, f"Auto-scaling configuration failed: {str(e)}")

    def scale_out(self, count: int):
        asg = boto3.client('autoscaling', self.config['region'])
        current = self.get_current_nodes()
        new_capacity = min(current + count, self.config['auto_scaling']['max_nodes'])
        asg.set_desired_capacity(
            AutoScalingGroupName=self.config['auto_scaling_group'],
            DesiredCapacity=new_capacity
        )

    def scale_in(self, count: int):
        asg = boto3.client('autoscaling', self.config['region'])
        current = self.get_current_nodes()
        new_capacity = max(current - count, self.config['auto_scaling']['min_nodes'])
        asg.set_desired_capacity(
            AutoScalingGroupName=self.config['auto_scaling_group'],
            DesiredCapacity=new_capacity
        )

    def get_current_nodes(self) -> int:
        asg = boto3.client('autoscaling', self.config['region'])
        response = asg.describe_auto_scaling_groups(
            AutoScalingGroupNames=[self.config['auto_scaling_group']]
        )
        return response['AutoScalingGroups'][0]['DesiredCapacity']

