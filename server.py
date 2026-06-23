#!/usr/bin/env python

"""
A server to provide the service from the web.
Run it with:
    uvicorn server:app
or
    uvicorn server:app --reload
"""

import os
import json
import PIL

from pathlib import Path
from typing import List, Tuple

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from optimizer import find_photographer_wsg84


def _load_dotenv(path=".env"):
    """Minimal .env loader so secrets can stay out of the source tree and out
    of git. Existing environment variables take precedence."""
    env_file = Path(path)
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

app = FastAPI()


class Locate(BaseModel):
    projections: List[Tuple[float, float]] = []
    latlngs: List[Tuple[float, float]] = []

@app.post("/locate/")
async def locate(query: Locate):
    """API entry point to locate the photographer."""
    projections = [p[0] for p in query.projections]
    try:
        optimisation = find_photographer_wsg84(query.latlngs, projections)
        reply = {"location": optimisation.photographer, "error": optimisation.error, "status": "ok"}
    except RuntimeError as e:
        reply = {"status": str(e)}
    print("locate request {} => {}".format(query, reply))
    return reply
 
@app.get("/examples/")
async def list_examples():
    """API entry point to get the list of examples."""
    return [p.name for p in Path("./data").iterdir()
            if p.joinpath("info.json").exists()]

@app.get("/examples/{name}")
async def get_example(name: str):
    """API entry point to get data of a given example."""
    dir = Path("./data") / name
    with dir.joinpath("info.json").open() as info:
        data = json.load(info)
        with PIL.Image.open(dir / data["picture"]) as img:
            data["picture_size"] = img.size    
        data["picture"] = dir / data["picture"]
        return data

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
@app.api_route("/index.html", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def index():
    """Serve index.html with the Google Maps API key injected from the
    environment, so the key never lives in the source tree."""
    html = Path("static/index.html").read_text()
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        print("WARNING: GOOGLE_MAPS_API_KEY is not set; the map will not load.")
    return html.replace("{{GOOGLE_MAPS_API_KEY}}", api_key)

app.mount("/data", StaticFiles(directory="data"), name="data")
app.mount("/", StaticFiles(directory="static"), name="static")
