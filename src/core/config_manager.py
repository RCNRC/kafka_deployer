from typing import Dict, Any
import yaml

class ConfigManager:
    def __init__(self, templates_dir: str = "configs"):
        self.templates_path = templates_dir
        
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load configuration template from YAML file"""
        config_path = Path(self.templates_path) / config_name
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def generate_inventory(self, nodes: list) -> str:
        """Generate Ansible inventory from node list"""
        return "\n".join([f"{node['ip']} ansible_user={node['user']}" for node in nodes])
