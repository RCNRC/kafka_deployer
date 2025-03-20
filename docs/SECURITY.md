# Security Configuration

## Automatic TLS Certificate Management

### Development Environment
1. Self-signed CA generated during first deployment
2. Node certificates automatically created with SAN for localhost
3. Certificates stored in `/etc/kafka/ssl` with 700 permissions

### Production Setup
1. Enable Let's Encrypt integration in `config/ssl_config.yml`
2. Set valid domains for your cluster nodes
3. Certificates automatically renewed 30 days before expiration

### Manual Certificate Management
To use custom certificates:
1. Place CA certificate as `ca.crt` in certificate directory
2. Place node certificate as `kafka.crt`
3. Place private key as `kafka.key`

### Certificate Rotation
1. Run deployment with `--rotate-certs` flag
2. Existing certificates will be backed up
3. New certificates generated and deployed

### Important Security Notes
- Never expose CA private key in production
- Use different CAs for development and production
- Monitor certificate expiration dates
