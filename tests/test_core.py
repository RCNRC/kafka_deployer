import pytest
from pathlib import Path
from src.core import ConfigManager

def test_config_loading():
    cm = ConfigManager(templates_dir="configs")
    config = cm.load_config("kafka_template.yaml")
    
    assert "nodes" in config
    assert len(config["nodes"]) == 3
    assert config["kafka_version"] == "3.2.0"

def test_inventory_generation():
    cm = ConfigManager()
    nodes = [
        {"ip": "10.0.0.1", "user": "user1"},
        {"ip": "10.0.0.2", "user": "user2"}
    ]
    inventory = cm.generate_inventory(nodes)
    
    assert "10.0.0.1 ansible_user=user1" in inventory
    assert "10.0.0.2 ansible_user=user2" in inventory
