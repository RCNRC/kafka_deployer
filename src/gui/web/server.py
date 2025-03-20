from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from ..base import BaseGUI
from ...core import ConfigManager

app = FastAPI()
base_gui = BaseGUI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return base_gui.render_web_template("index.html")

@app.post("/api/scale/{operation}")
async def scale_cluster(operation: str):
    return base_gui.handle_scaling(operation)

@app.get("/api/metrics")
async def get_metrics():
    return base_gui.get_current_metrics()

