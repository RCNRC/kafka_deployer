# Security Configuration

## Automatic TLS Certificate Management

### Development Environment
1. Self-signed CA generated during first deployment
2. Node certificates automatically created with SAN for cluster nodes
3. Certificates stored in `/etc/kafka/ssl` with 700 permissions
4. Auto-renewal when certificates approach expiration

### Production Setup with Let's Encrypt
1. Enable in `config/ssl_config.yml`:
   ```yaml
   lets_encrypt:
     enabled: true
     email: "your@email.com"
     staging: false
     domains: ["kafka.example.com"]
   ```
2. Ensure proper DNS records resolve to your cluster nodes
3. Certificates automatically renewed 30 days before expiration
4. Supports wildcard certificates via DNS challenge (**Requires DNS provider credentials**)

### Certificate Rotation
1. Manual rotation:
   ```bash
   python -m src.cli.cli rotate-certs
   ```
2. Scheduled rotation via cron job for Let's Encrypt certificates

### Manual Certificate Override
To use custom certificates:
1. Place CA certificate at `/etc/kafka/ssl/ca.crt`
2. Node certificate chain as `/etc/kafka/ssl/kafka.crt`
3. Private key as `/etc/kafka/ssl/kafka.key` (permissions 600)

### Security Best Practices
- Use separate certificates for production and development
- Enable certificate validation in preflight checks
- Regularly monitor certificate expiration dates
- Store Let's Encrypt credentials securely using environment variables

