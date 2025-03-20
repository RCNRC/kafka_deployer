# Kafka Deployer Error Codes

## SSL/TLS Errors (1000-1999)

| Code | Description | Resolution Steps |
|------|-------------|------------------|
| 1004 | Certificate generation failed | Verify OpenSSL/certbot installation and permissions |
| 1005 | Let's Encrypt challenge failed | Check DNS/HTTP validation configuration |
| 1006 | Certificate validation failed | Check expiration dates and SAN configuration |
| 1007 | Certificate missing or invalid | Generate new certificates or check paths |
| 1008 | Private key mismatch | Verify key pair generation process |
| 1009 | Missing required domain in certificate | Ensure all required domains are in config |
| 1010 | DNS validation timeout | Increase dns_propagation timeout value |

## Cloud Provider Errors (3000-3999)
| Code | Description | Resolution Steps |
|------|-------------|------------------|
| 3001 | Missing AWS config keys | Verify required keys in configuration |
| 3002 | AWS provisioning failure | Check AWS credentials and permissions |
| 3101 | Missing GCP project_id | Set project_id in config |
| 3102 | GCP topic creation failed | Verify Pub/Sub API enabled |
| 3201 | Missing Azure resource group | Specify resource_group in config |

