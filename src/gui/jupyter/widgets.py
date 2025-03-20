from IPython.display import display
from ipywidgets import Tab, Output
from ..base import BaseGUI
import time

class KafkaJupyterGUI(BaseGUI):
    def __init__(self, cluster_config):
        self.config = cluster_config
        self.tabs = Tab()
        self.output = Output()
        
    def display(self):
        self.create_config_pane()
        self.create_metrics_pane()
        display(self.tabs, self.output)
        
    def update_dashboard(self):
        with self.output:
            print(f"Last update: {time.ctime()}")
            # Add metric visualization

