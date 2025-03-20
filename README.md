# Kafka Deployment Tool

Python application for automated Apache Kafka cluster deployment using Ansible.

## Project Structure

```
/src
├── core/               # Core logic (Ansible integration, configuration management)
│   ├── __init__.py
│   ├── ansible_wrapper.py
│   └── config_manager.py
├── cli/                # Command-line interface (Click)
│   ├── __init__.py
│   └── cli.py
/configs                # Cluster configuration templates
/docs                   # Documentation
/tests                  # Unit and integration tests

```

## Quick Start

1. Install dependencies (Python 3.10+ required):
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Test installation:
```bash
python -m src.cli.cli --help
```

3. Deploy test cluster:
```bash
python -m src.cli.cli deploy --config configs/kafka_template.yaml
```

## Development
```bash
# Run tests
pytest tests/
```
