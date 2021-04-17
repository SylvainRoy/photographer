#!/usr/bin/env python

"""
A server to provide the service from the web.
Run it with:
    uvicorn server:app
or
    uvicorn server:app --reload
"""

import json
import os
from pathlib import Path
from typing import List, Tuple

import PIL
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from optimizer import find_photographer_wsg84

app = FastAPI()

templates = Jinja2Templates(directory="static")

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
    return sorted(
        [p.name for p in Path("./data").iterdir()
         if p.joinpath("info.json").exists()]
    )

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

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Main page of webapp."""
    googlemapkey = os.environ["GOOGLEMAPAPIKEY"]
    return templates.TemplateResponse("index.html", {"request": request, "googlemapapikey": googlemapkey})


app.mount("/data", StaticFiles(directory="data"), name="data")
app.mount("/", StaticFiles(directory="static"), name="static")
