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
        if self.config['lets_encrypt']['enabled']:
            logger.info("Skipping CA generation - Let's Encrypt enabled")
            return

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
        if self.config['lets_encrypt']['enabled']:
            self._generate_lets_encrypt_certificate()
        else:
            self._generate_self_signed_certificate(hostnames)

    def _generate_self_signed_certificate(self, hostnames):
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
        logger.info(f"Generated self-signed certificate for {hostnames}")

    def _generate_lets_encrypt_certificate(self):
        domains = self.config['lets_encrypt']['domains']
        if not domains:
            raise ValueError("Let's Encrypt requires domains configuration")

        email = self.config['lets_encrypt']['email']
        if not email:
            raise ValueError("Let's Encrypt requires email configuration")

        certbot_cmd = [
            'certbot', 'certonly', '--non-interactive', '--agree-tos',
            '--standalone',
            '--email', email,
            '--cert-name', 'kafka-cert',
            '-d', ','.join(domains)
        ]

        if self.config['lets_encrypt']['staging']:
            certbot_cmd.append('--staging')

        try:
            subprocess.run(certbot_cmd, check=True, capture_output=True)
            logger.info("Let's Encrypt certificate generated successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Let's Encrypt failed: {e.stderr.decode()}")
            raise RuntimeError("Let's Encrypt certificate generation failed")

        le_cert_path = f'/etc/letsencrypt/live/kafka-cert/fullchain.pem'
        le_key_path = f'/etc/letsencrypt/live/kafka-cert/privkey.pem'
        
        shutil.copy(le_cert_path, self.node_cert_path)
        shutil.copy(le_key_path, self.node_key_path)
        os.chmod(self.node_key_path, 0o600)
        logger.info(f"Let's Encrypt certificates copied to {self.cert_dir}")

    def validate_certificates(self):
        if not os.path.exists(self.node_cert_path):
            raise FileNotFoundError("Node certificate missing")
        
        with open(self.node_cert_path, 'rb') as f:
            cert = x509.load_pem_x509_certificate(f.read())
            
        if datetime.utcnow() > cert.not_valid_after:
            raise ValueError("Certificate has expired")
            
        if self.config['lets_encrypt']['enabled']:
            if (cert.not_valid_after - datetime.utcnow()).days < 30:
                logger.warning("Certificate expires in less than 30 days")
                raise ValueError("Certificate renewal required")

    def renew_certificates(self):
        if self.config['lets_encrypt']['enabled']:
            self._generate_lets_encrypt_certificate()
            self.validate_certificates()
            logger.info("Certificate renewal completed successfully")

