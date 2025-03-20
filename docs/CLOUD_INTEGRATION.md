# Cloud Provider Integration Guide

## AWS Configuration
1. Set environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID="your_access_key"
   export AWS_SECRET_ACCESS_KEY="your_secret_key"
   ```
2. Example configuration:
   ```yaml
   aws:
     region: us-east-1
     instance_type: t3.medium
     ssh_key_name: kafka-cluster-key
   ```

## GCP Configuration
1. Set service account credentials:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
   ```
2. Required IAM roles:
   - Pub/Sub Admin
   - Compute Instance Admin

## Azure Configuration
1. Authenticate using Azure CLI:
   ```bash
   az login
   ```
2. Required RBAC roles:
   - EventHub Contributor
   - Network Contributor
