class CloudMetricsExporter:
    def __init__(self, config):
        self.config = config
        
    def export_cloudwatch_metrics(self, metrics):
        if not self.config.get('cloudwatch', {}).get('enabled'):
            return
            
        client = boto3.client('cloudwatch', region_name=self.config['cloudwatch']['aws_region'])
        namespace = self.config['cloudwatch'].get('namespace', 'Kafka')
        
        metric_data = [{
            'MetricName': name,
            'Dimensions': [{'Name': 'Cluster', 'Value': self.config['cluster_name']}],
            'Value': value
        } for name, value in metrics.items()]
        
        client.put_metric_data(Namespace=namespace, MetricData=metric_data)

    def export_stackdriver_metrics(self, metrics):
        if not self.config.get('stackdriver', {}).get('enabled'):
            return
            
        from google.cloud import monitoring_v3
        client = monitoring_v3.MetricServiceClient()
        project = self.config['stackdriver']['project_id']
        
        for name, value in metrics.items():
            series = monitoring_v3.TimeSeries()
            series.metric.type = f"custom.googleapis.com/kafka/{name}"
            series.resource.type = "global"
            point = monitoring_v3.Point()
            point.value.double_value = value
            point.interval.end_time.seconds = int(time.time())
            series.points.append(point)
            
            client.create_time_series(name=f"projects/{project}", time_series=[series])

