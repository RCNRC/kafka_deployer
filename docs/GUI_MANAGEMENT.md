# GUI Management Interface

## Desktop Application
```bash
python -m src.gui.desktop.app
```

Features:
- Drag-and-drop configuration file loading
- Topology visualization with health indicators
- One-click scaling operations
- Certificate management dashboard

## Web Interface
Access through port 8080:
```bash
python -m src.gui.web.server
```

Includes:
- Mobile-responsive dashboards
- REST API endpoints for automation
- Live metrics streaming

## Jupyter Integration
```python
from src.gui.jupyter import KafkaDashboard
KafkaDashboard(cluster_config).display()
```

## Accessibility Features
- Screen reader support
- Keyboard navigation
- High contrast mode
- ARIA labels for all controls

## Multi-interface Sync
All GUI modes share configuration state through core backend API.

