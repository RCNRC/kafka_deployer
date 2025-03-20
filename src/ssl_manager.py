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
import boto3
from google.cloud import security_privateca_v1

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
        self.audit_log = []
        
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
        self._log_audit(event="SCHEDULER_START", status="SUCCESS")

    def check_and_renew(self):
        """Check certificates and renew if needed"""
        try:
            expiry_days = self.get_cert_expiry_days()
            if expiry_days <= self.renewal_threshold:
                logger.info(f"Certificate expires in {expiry_days} days, initiating renewal")
                self.renew_certificates()
                self.update_prometheus_metrics()
                self._log_audit(event="AUTO_RENEWAL", status="SUCCESS")
        except Exception as e:
            logger.error(f"Certificate renewal check failed: {str(e)}")
            self._log_audit(event="AUTO_RENEWAL", status="FAILED", error=str(e))

    def _log_audit(self, event: str, status: str, error: str = None):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "status": status,
            "error": error
        }
        self.audit_log.append(entry)

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
        """Renew certificates with zero-downtime rotation"""
        if self.config.get('use_custom_ca'):
            self._renew_self_signed_certs(hostnames)
        elif self.config.get('aws', {}).get('use_acm'):
            self._renew_acm_certificate()
        elif self.config.get('gcp', {}).get('managed_certs'):
            self._renew_gcp_certificate()
        else:
            self._renew_lets_encrypt_cert()
        
        self._restart_services_gracefully()
        logger.info("Certificate renewal completed successfully")

    def _renew_acm_certificate(self):
        """Renew certificate using AWS Certificate Manager"""
        acm = boto3.client('acm', region_name=self.config['aws']['region'])
        response = acm.request_certificate(
            DomainName=self.config['aws']['domain'],
            ValidationMethod='DNS'
        )
        cert_arn = response['CertificateArn']
        self._write_acm_cert(cert_arn)

    def _write_acm_cert(self, arn: str):
        acm = boto3.client('acm', region_name=self.config['aws']['region'])
        cert = acm.get_certificate(CertificateArn=arn)
        with open(self.node_cert_path, 'w') as f:
            f.write(cert['Certificate'])

    def _renew_gcp_certificate(self):
        """Renew certificate using Google Certificate Authority Service"""
        client = security_privateca_v1.CertificateAuthorityServiceClient()
        name = client.certificate_authority_path(
            project=self.config['gcp']['project_id'],
            location=self.config['gcp']['location'],
            certificate_authority=self.config['gcp']['ca_name']
        )
        cert = client.create_certificate(
            parent=name,
            certificate=security_privateca_v1.Certificate()
        )
        self._write_gcp_cert(cert)

    def _write_gcp_cert(self, cert):
        with open(self.node_cert_path, 'wb') as f:
            f.write(cert.pem_certificate.encode())

    def generate_k8s_csr(self):
        """Generate Kubernetes CertificateSigningRequest"""
        csr = x509.CertificateSigningRequestBuilder().subject_name(
            x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, self.config['country']),
                x509.NameAttribute(NameOID.STATE, self.config['state']),
                x509.NameAttribute(NameOID.LOCALITY, self.config['locality']),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.config['organization']),
                x509.NameAttribute(NameOID.COMMON_NAME, self.config['common_name'])
            ])
        ).sign(rsa.generate_private_key(public_exponent=65537, key_size=2048), hashes.SHA256())
        
        return csr.public_bytes(serialization.Encoding.PEM)

    def _restart_services_gracefully(self):
        """Perform rolling restart of Kafka brokers"""
        # Implementation depends on deployment method
        pass

