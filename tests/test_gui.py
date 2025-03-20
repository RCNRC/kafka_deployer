import pytest
from src.gui.base import BaseGUI
from src.core import ConfigManager

def test_base_gui_config_loading():
    gui = BaseGUI()
    gui.load_config('configs/kafka_template.yaml')
    assert gui.current_config['cluster_name'] == 'test-cluster'

def test_scaling_operations(mocker):
    gui = BaseGUI()
    mocker.patch.object(gui.ansible, 'run_playbook')
    gui.handle_scaling('scale_out')
    gui.ansible.run_playbook.assert_called_with('scale_out.yml')

