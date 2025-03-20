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
     domains: ["kafka.example.com", "*.kafka-cluster"]
     dns_provider: cloudflare
     dns_propagation: 120
     dns_env:
       CLOUDFLARE_API_TOKEN: "your-token"
   ```
2. Supported DNS providers: cloudflare, route53, digitalocean and others via certbot plugins
3. Certificates automatically renewed 30 days before expiration
4. Wildcard certificates require DNS challenge configuration

### Certificate Rotation
1. Manual rotation:
   ```bash
   python -m src.cli.cli rotate-certs --dns kafka.example.com,broker1.kafka.example.com
   ```
2. Force renewal for valid certificates:
   ```bash
   python -m src.cli.cli rotate-certs --force
   ```

### Certificate Validation
Preflight checks verify:
- Certificate expiration dates
- Matching private key
- Inclusion of all required domain names (SAN)
- Proper certificate chain

