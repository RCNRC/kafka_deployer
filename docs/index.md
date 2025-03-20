# Kafka Deployer Documentation

## Core Components

### ConfigManager
Responsible for loading YAML configuration templates and generating inventory files

### AnsibleRunner
Wrapper for executing Ansible playbooks with proper inventory and credentials

## CLI Reference
```bash
python -m src.cli.cli deploy --config <path_to_config>
```
