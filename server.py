#!/usr/bin/env python

"""
A server to provide the service from the web.
Run it with:
  uvicorn server:app
or
  uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
