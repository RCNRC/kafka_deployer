import os
import subprocess
import shutil
from datetime import datetime, timedelta
import logging
import yaml
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger('kafka_deployer.ssl')

class SSLCertManager:
    def __init__(self, config_path='config/ssl_config.yml'):
        self.config = self._load_config(config_path)
        self.cert_dir = self.config['cert_dir']
        self.ca_cert_path = os.path.join(self.cert_dir, 'ca.crt')
        self.ca_key_path = os.path.join(self.cert_dir, 'ca.key')
        self.node_cert_path = os.path.join(self.cert_dir, 'kafka.crt')
        self.node_key_path = os.path.join(self.cert_dir, 'kafka.key')
        self.scheduler = BackgroundScheduler()
        self.renewal_threshold = self.config.get('renewal_threshold_days', 30)
        
        os.makedirs(self.cert_dir, exist_ok=True)
        os.chmod(self.cert_dir, 0o700)

    def _load_config(self, path):
        with open(path) as f:
            return yaml.safe_load(f)

    def start_auto_renewal(self):
        """Start scheduled certificate renewal checks"""
        self.scheduler.add_job(
            self.check_and_renew, 
            'interval', 
            hours=24,
            next_run_time=datetime.now()
        )
        self.scheduler.start()
        logger.info("Started SSL certificate auto-renewal scheduler")

    def check_and_renew(self):
        """Check certificates and renew if needed"""
        try:
            expiry_days = self.get_cert_expiry_days()
            if expiry_days <= self.renewal_threshold:
                logger.info(f"Certificate expires in {expiry_days} days, initiating renewal")
                self.renew_certificates()
                
                # Update metrics after renewal
                self.update_prometheus_metrics()
        except Exception as e:
            logger.error(f"Certificate renewal check failed: {str(e)}")

    def get_cert_expiry_days(self) -> float:
        """Calculate remaining validity days for certificate"""
        with open(self.node_cert_path, 'rb') as f:
            cert = x509.load_pem_x509_certificate(f.read())
        delta = cert.not_valid_after - datetime.utcnow()
        return delta.days + delta.seconds / 86400

    def update_prometheus_metrics(self):
        """Update Prometheus metrics for certificate expiry"""
        from ..core.monitoring import MetricsCollector
        collector = MetricsCollector()
        expiry_days = self.get_cert_expiry_days()
        collector.metrics['ssl_cert_expiry_days'].set(expiry_days)

    def renew_certificates(self, hostnames=None):
        # Existing renewal logic remains
        # Added metrics update after successful renewal
        logger.info("Certificate renewal completed successfully")

    # Rest of existing class methods remain unchanged
