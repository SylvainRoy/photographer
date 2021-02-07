#!/usr/bin/env python

"""
A server to provide the service from the web.
Run it with:
    uvicorn server:app
or
    uvicorn server:app --reload
"""

from typing import List, Tuple

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from optimizer import find_photograper_wsg84

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class Locate(BaseModel):
    projections: List[float] = []
    latlngs: List[Tuple[float, float]] = []

@app.post("/locate/")
async def locate(query: Locate):
    """API entry point to locate the photographer."""
    try:
        location, error, _ = find_photograper_wsg84(query.latlngs, query.projections)
        reply = {"location": location, "error": error, "status": "ok"}
    except RuntimeError as e:
        reply = {"status": str(e)}
    print("locate request {} => {}".format(query, reply))
    return reply
