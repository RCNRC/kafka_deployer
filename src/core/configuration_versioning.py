import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger('kafka_deployer.versioning')

class ConfigurationVersioning:
    def __init__(self, history_file='config_versions.json'):
        self.history_file = Path(history_file)
        self.history = self._load_history()

    def _load_history(self) -> List[Dict]:
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []

    def record_change(self, config: Dict, comment: str = ''):
        version = {
            'timestamp': datetime.now().isoformat(),
            'config': config,
            'comment': comment,
            'hash': hash(frozenset(config.items()))
        }
        self.history.append(version)
        self._save_history()
        logger.info(f"Recorded configuration version {len(self.history)}")

    def get_version(self, index: int) -> Dict:
        if 0 <= index < len(self.history):
            return self.history[index]
        raise IndexError("Invalid version index")

    def rollback(self, index: int):
        if 0 <= index < len(self.history):
            config = self.history[index]['config']
            self.record_change(config, f"Rollback to version {index}")
            return config
        raise IndexError("Invalid rollback version")

    def _save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

