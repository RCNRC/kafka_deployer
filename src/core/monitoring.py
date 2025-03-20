from grafana_api.grafana_face import GrafanaFace
import yaml
import requests

class MonitoringManager:
    def __init__(self, config):
        self.grafana = GrafanaFace(
            auth=config['grafana']['admin_password'],
            host=config['grafana']['host']
        )
        self.prometheus_url = config['prometheus']['url']
        
    def import_dashboards(self):
        with open('configs/grafana/dashboard.json') as f:
            dashboard = json.load(f)
        self.grafana.dashboard.update_dashboard({
            'dashboard': dashboard,
            'overwrite': True
        })
    
    def setup_alerts(self):
        alerts = [
            {
                "name": "HighConsumerLag",
                "query": "kafka_consumer_lag_messages > 10000",
                "for": "5m",
                "labels": {"severity": "critical"},
                "annotations": {"summary": "High consumer lag detected"}
            }
        ]
        for alert in alerts:
            requests.post(
                f"{self.prometheus_url}/api/v1/alerts",
                json=alert
            )

    def sync_cloud_metrics(self, provider):
        if provider == 'aws':
            self._setup_cloudwatch_integration()
        elif provider == 'gcp':
            self._setup_stackdriver_integration()

