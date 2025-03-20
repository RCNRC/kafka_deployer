class MetricsCollector:
    def _initialize_metrics(self):
        self.metrics = {
            'ssl_cert_expiry_days': Gauge('kafka_ssl_cert_expiry_days', 'Days remaining until SSL certificate expiration'),
            # Existing metrics...
        }
        # Rest of initialization

class AutoOptimizer:
    # Existing code...
    
    def generate_cert_alerts(self, metrics):
        """Generate alerts for certificate expiration"""
        if metrics.get('kafka_ssl_cert_expiry_days', 365) <= 30:
            return {'SSL_CERT_EXPIRY_WARNING': f"Certificate expires in {metrics['kafka_ssl_cert_expiry_days']} days"}
        return {}
