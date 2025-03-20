import boto3
from botocore.exceptions import ClientError
from .base import CloudProvider
from typing import Dict, Any
import logging

logger = logging.getLogger('kafka_deployer.aws')

class AWSCloudProvider(CloudProvider):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = boto3.client('autoscaling', region_name=config['region'])
        self.ec2_client = boto3.client('ec2', region_name=config['region'])
        
    def scale_out(self, count: int) -> None:
        try:
            asg_name = self.config['auto_scaling_group']
            current = self.get_current_nodes()
            new_capacity = min(current + count, self.config['max_nodes'])
            
            self.client.set_desired_capacity(
                AutoScalingGroupName=asg_name,
                DesiredCapacity=new_capacity,
                HonorCooldown=True
            )
            logger.info(f"Scaled out AWS ASG {asg_name} to {new_capacity}")
        except ClientError as e:
            logger.error(f"AWS scale out failed: {str(e)}")
            raise

    def scale_in(self, count: int) -> None:
        try:
            asg_name = self.config['auto_scaling_group']
            current = self.get_current_nodes()
            new_capacity = max(current - count, self.config['min_nodes'])
            
            self.client.set_desired_capacity(
                AutoScalingGroupName=asg_name,
                DesiredCapacity=new_capacity,
                HonorCooldown=True
            )
            logger.info(f"Scaled in AWS ASG {asg_name} to {new_capacity}")
        except ClientError as e:
            logger.error(f"AWS scale in failed: {str(e)}")
            raise

    def get_current_nodes(self) -> int:
        asg_name = self.config['auto_scaling_group']
        response = self.client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[asg_name]
        )
        return response['AutoScalingGroups'][0]['DesiredCapacity']

    def get_pricing_data(self) -> Dict[str, float]:
        try:
            response = self.ec2_client.describe_spot_price_history(
                InstanceTypes=[self.config['instance_type']],
                ProductDescriptions=['Linux/UNIX'],
                MaxResults=1
            )
            spot_price float float(response['SpotPriceHistory'][0]['SpotPrice'])
            
            return {
                'on_demand': self.config.get('on_demand_price', 0.12),
                'spot': spot_price,
                'reserved': self.config.get('reserved_price', 0.08)
            }
        except ClientError as e:
            logger.warning(f"Failed to get spot prices: {str(e)}")
            return self.config.get('fallback_prices', {})

    def get_instance_lifecycle(self) -> Dict[str, float]:
        response = self.ec2_client.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )
        lifecycle = {'spot': 0, 'on_demand': 0}
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                if instance.get('InstanceLifecycle') == 'spot':
                    lifecycle['spot'] += 1
                else:
                    lifecycle['on_demand'] += 1
        return lifecycle

