from google.cloud import pubsub
from .base import CloudProvider, CloudError

class GCPCloudProvider(CloudProvider):
    """GCP implementation using Pub/Sub"""
    
    def _validate_config(self) -> None:
        if 'project_id' not in self.config:
            raise CloudError(3101, "Missing GCP project_id in config")
    
    def provision_infrastructure(self) -> Dict[str, str]:
        try:
            publisher = pubsub.PublisherClient()
            topic_path = publisher.topic_path(self.config['project_id'], 'kafka-events')
            publisher.create_topic(name=topic_path)
            return {'topic': topic_path}
        except Exception as e:
            raise CloudError(3102, f"GCP provisioning failed: {str(e)}")
    
    # Other method implementations...
