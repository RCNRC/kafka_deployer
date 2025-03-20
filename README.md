# Kafka Deployment Tool

Python application for automated Apache Kafka cluster deployment using Ansible.

## Project Structure

```
/src
├── core/          # Core logic (Ansible integration, config management)
├── cli/           # Command-line interface (Click)
├── api/           # REST API endpoints (FastAPI) - TODO
└── gui/           # GUI components (PyQt/Gradio) - TODO

/configs           # Cluster configuration templates
/docs             # Documentation and guides
/tests            # Unit and integration tests
```

## Quick Start

1. Clone repository:
```bash
git clone https://github.com/your/repo.git
cd kafka_deployer
```

2. Install dependencies (requires Python 3.10+):
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Deploy test cluster:
```bash
python -m src.cli.cli deploy --config configs/kafka_template.yaml
```

## Development
```bash
# Run tests
pytest tests/

# Generate documentation
mkdocs serve
```
