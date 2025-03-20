#!/usr/bin/env python3
import logging
import subprocess
from src.error_handler import handle_error
from src.cloud_integration import cleanup_cloud_resources
from src.ssl_manager import SSLCertManager  # New import

logging.config.fileConfig('config/logging.conf')
logger = logging.getLogger('kafka_deployer')

def run_preflight_checks():
    try:
        # SSL Certificate Management
        ssl_mgr = SSLCertManager()
        ssl_mgr.generate_ca()
        ssl_mgr.generate_node_certificate(['localhost'])  # TODO: Get actual hostnames
        
        result = subprocess.run(
            ["scripts/preflight_checks.sh"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(result.stdout)
    except subprocess.CalledProcessError as e:
        handle_error(e.returncode, e.stderr)

def main():
    try:
        logger.info("Starting Kafka deployment workflow")
        run_preflight_checks()
        
        logger.debug("Executing Ansible playbook")
        result = subprocess.run(
            ["ansible-playbook", "playbooks/deploy_kafka.yml"],
            check=True
        )
        
        logger.info("Kafka deployment completed successfully")
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        cleanup_cloud_resources()
        raise

if __name__ == "__main__":
    main()
