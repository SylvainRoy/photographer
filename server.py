#!/usr/bin/env python

"""
A server to provide the service from the web.
Run it with:
    uvicorn server:app
or
    uvicorn main:app --reload
"""

from typing import List, Tuple
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class Locate(BaseModel):
    projections: List[float] = []
    latlng: List[Tuple[float, float]] = []

@app.post("/locate/")
async def locate(query: Locate):
    reply = (12.97, 77.59)
    print("locate request {} => {}".format(query, reply))
    return {"location": reply}
