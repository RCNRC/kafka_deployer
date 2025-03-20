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

## Deployment Errors (2000-2999)

| Code | Description | Resolution Steps |
|------|-------------|------------------|
| 2001 | Java installation failed | Check network connectivity and package repos |
| 2002 | Kafka download failed | Verify download URL and checksum |
| 2003 | Kafka service startup failed | Check systemd logs with 'journalctl -u kafka' |

## Rollback Procedures

All failed deployments automatically attempt to:
1. Stop Kafka service
2. Remove temporary files
3. Cleanup cloud resources (if applicable)

Manual cleanup may be required for interrupted rollbacks.
