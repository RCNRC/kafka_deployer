import subprocess
from pathlib import Path

class AnsibleRunner:
    def __init__(self, playbooks_path: str = "ansible/playbooks"):
        self.playbooks_dir = Path(playbooks_path)
        
    def run_playbook(self, playbook: str, inventory: str = "inventory.ini") -> bool:
        """Execute Ansible playbook with given inventory"""
        try:
            result = subprocess.run(
                ["ansible-playbook", "-i", inventory, str(self.playbooks_dir / playbook)],
                check=True,
                capture_output=True
            )
            print(result.stdout.decode())
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error executing playbook: {e.stderr.decode()}")
            return False
