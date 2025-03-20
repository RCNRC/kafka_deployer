# Kafka Deployer Error Codes

## Preflight Check Errors (1000-1999)

| Code | Description | Resolution Steps |
|------|-------------|------------------|
| 1001 | Insufficient disk space | Free up at least 5GB on root partition |
| 1002 | Disk space check failed | Verify system permissions and disk status |
| 1003 | Missing cloud credentials | Set required environment variables for cloud provider |
| 1004 | TLS certificate not found | Verify certificate path and permissions |
| 1005 | TLS key not found | Verify key file exists and permissions |
| 1006 | TLS files check failed | Validate TLS certificate and key pair |
| 1007 | SSL generation failed | Check OpenSSL installation and permissions |
| 1008 | Certificate validation failed | Verify certificate chain and expiration dates |

## Deployment Errors (2000-2999)

| Code | Description | Resolution Steps |
|------|-------------|------------------|
| 2001 | Java installation failed | Check network connectivity and package repos |
| 2002 | Kafka download failed | Verify download URL and checksum |
| 2003 | Kafka service startup failed | Check systemd logs with 'journalctl -u kafka' |
| 2004 | SSL configuration failed | Validate certificate paths in server.properties |

## Rollback Procedures

All failed deployments automatically attempt to:
1. Stop Kafka service
2. Remove temporary files
3. Cleanup cloud resources (if applicable)
4. Restore previous SSL certificates (if available)

Manual cleanup may be required for interrupted rollbacks.

## Cloud Provider Errors (3000-3999)

| Code | Description | Resolution Steps |
|------|-------------|------------------|
| 3001 | Missing AWS config keys | Verify required keys in configuration |
| 3002 | AWS provisioning failure | Check AWS credentials and permissions |
| 3101 | Missing GCP project_id | Set project_id in config |
| 3102 | GCP topic creation failed | Verify Pub/Sub API enabled |
| 3201 | Missing Azure resource group | Specify resource_group in config |
