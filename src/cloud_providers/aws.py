import boto3
from botocore.exceptions import ClientError
from .base import CloudProvider
from typing import Dict, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger('kafka_deployer.aws')

class AWSCloudProvider(CloudProvider):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = boto3.client('autoscaling', region_name=config['region'])
        self.ec2_client = boto3.client('ec2', region_name=config['region'])
        self.price_cache = {'timestamp': None, 'data': None}
        
    def scale_out(self, count: int, spot: bool = False) -> None:
        try:
            if spot and self.config.get('spot_enabled', False):
                self._scale_out_spot(count)
            else:
                self._scale_out_ondemand(count)
        except ClientError as e:
            logger.error(f"AWS scale out failed: {str(e)}")
            raise

    def _scale_out_ondemand(self, count: int):
        asg_name = self.config['auto_scaling_group']
        current = self.get_current_nodes()
        new_capacity = min(current + count, self.config['max_nodes'])
        
        self.client.set_desired_capacity(
            AutoScalingGroupName=asg_name,
            DesiredCapacity=new_capacity,
            HonorCooldown=True
        )

    def _scale_out_spot(self, count: int):
        spot_config = {
            'LaunchTemplate': {
                'LaunchTemplateName': self.config['spot_template'],
                'Version': '$Latest'
            },
            'InstanceRequirements': {
                'VCpuCount': {'Min': 2},
                'MemoryMiB': {'Min': 4096}
            }
        }
        
        response = self.client.batch_create_instances(
            InstanceType='mixed',
            SpotPercentage=100,
            LaunchTemplateConfigs=[spot_config],
            MinCount=count,
            MaxCount=count
        )
        logger.info(f"Launched {count} spot instances")

    def handle_spot_interruptions(self):
        try:
            events = self.ec2_client.describe_spot_instance_requests(
                Filters=[{'Name': 'state', 'Values': ['marked-for-termination']}]
            )
            if events['SpotInstanceRequests']:
                logger.warning(f"Spot interruption detected, replacing {len(events)} instances")
                self.scale_out(len(events), spot=True)
                self._terminate_instances([i['InstanceId'] for i in events])
        except ClientError as e:
            logger.error(f"Spot interruption handling failed: {str(e)}")

    def get_pricing_data(self) -> Dict[str, float]:
        if self.price_cache['timestamp'] and \
           (datetime.now() - self.price_cache['timestamp']) < timedelta(minutes=15):
            return self.price_cache['data']
            
        try:
            pricing = boto3.client('pricing', region_name='us-east-1')
            response = pricing.get_products(
                ServiceCode='AmazonEC2',
                Filters=[
                    {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': self.config['instance_type']},
                    {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'}
                ]
            )
            price_list = response['PriceList'][0]
            self.price_cache = {
                'timestamp': datetime.now(),
                'data': {
                    'on_demand': float(price_list['terms']['OnDemand'].values()[0]['priceDimensions'].values()[0]['pricePerUnit']['USD']),
                    'spot': self._get_spot_price(),
                    'reserved': float(price_list['terms']['Reserved'].values()[0]['priceDimensions'].values()[0]['pricePerUnit']['USD'])
                }
            }
            return self.price_cache['data']
        except Exception as e:
            logger.warning(f"Failed to get pricing data: {str(e)}")
            return self.config.get('fallback_prices', {})

    def _get_spot_price(self) -> float:
        response = self.ec2_client.describe_spot_price_history(
            InstanceTypes=[self.config['instance_type']],
            ProductDescriptions=['Linux/UNIX'],
            MaxResults=1
        )
        return float(response['SpotPriceHistory'][0]['SpotPrice'])

    def _terminate_instances(self, instance_ids: list):
        self.ec2_client.terminate_instances(InstanceIds=instance_ids)
        logger.info(f"Terminated instances: {instance_ids}")

