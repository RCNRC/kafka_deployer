from abc import ABC, abstractmethod
from ...core import ConfigManager, AnsibleRunner

class BaseGUI(ABC):
    def __init__(self):
        self.config_manager = ConfigManager()
        self.ansible = AnsibleRunner()
        self.current_config = None

    @abstractmethod
    def render(self):
        pass

    def load_config(self, path=None):
        self.current_config = self.config_manager.load_config(path or 'default.yaml')

    def handle_scaling(self, operation):
        if operation == 'scale_out':
            return self.ansible.run_playbook('scale_out.yml')
        elif operation == 'scale_in':
            return self.ansible.run_playbook('scale_in.yml')

    def get_current_metrics(self):
        return {
            'cpu_usage': 65.2,
            'memory_usage': 42.8
        }

