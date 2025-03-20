import os
import subprocess
from datetime import datetime, timedelta
import yaml
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger('kafka_deployer.ssl')

class SSLCertManager:
    def __init__(self, config_path='config/ssl_config.yml'):
        self.config = self._load_config(config_path)
        self.cert_dir = self.config['cert_dir']
        self.ca_cert_path = os.path.join(self.cert_dir, 'ca.crt')
        self.ca_key_path = os.path.join(self.cert_dir, 'ca.key')
        self.node_cert_path = os.path.join(self.cert_dir, 'kafka.crt')
        self.node_key_path = os.path.join(self.cert_dir, 'kafka.key')
        
        os.makedirs(self.cert_dir, exist_ok=True)
        os.chmod(self.cert_dir, 0o700)

    def _load_config(self, path):
        with open(path) as f:
            return yaml.safe_load(f)

    def generate_ca(self):
        if os.path.exists(self.ca_cert_path) and os.path.exists(self.ca_key_path):
            logger.info("CA certificate already exists")
            return

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"Kafka Deployment CA"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=3650)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True,
        ).sign(key, hashes.SHA256(), default_backend())

        with open(self.ca_cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        with open(self.ca_key_path, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))
        
        logger.info("Generated new CA certificate")

    def generate_node_certificate(self, hostnames):
        if not os.path.exists(self.ca_cert_path):
            raise FileNotFoundError("CA certificate not found")

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"Kafka Node"),
        ])).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(h) for h in hostnames]),
            critical=False,
        ).sign(key, hashes.SHA256(), default_backend())

        with open(self.ca_key_path, "rb") as f:
            ca_key = serialization.load_pem_private_key(f.read(), password=None)
        with open(self.ca_cert_path, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())

        cert = x509.CertificateBuilder().subject_name(
            csr.subject
        ).issuer_name(
            ca_cert.subject
        ).public_key(
            csr.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=self.config['cert_expiry_days'])
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True
        ).sign(ca_key, hashes.SHA256(), default_backend())

        with open(self.node_cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        with open(self.node_key_path, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

        logger.info(f"Generated node certificate for {hostnames}")

    def validate_certificates(self):
        # Implementation for certificate validation
        pass

    def lets_encrypt_integration(self):
        # Implementation for Let's Encrypt
        pass
