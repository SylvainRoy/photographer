#!/usr/bin/env python

import os

from invoke import task


@task
def check(c):
    if "PHO_GOOGLE_MAP_API_KEY" not in os.environ:
        print("- environment variable PHO_GOOGLE_MAP_API_KEY is not set!")
    if "PHO_DOCKER_IMAGE_NAME" not in os.environ:
        print("- environment variable PHO_DOCKER_IMAGE_NAME is not set!")

@task
def unittest(c):
    c.run("python -m unittest discover .")

@task
def run(c):
    if "PHO_GOOGLE_MAP_API_KEY" not in os.environ:
        print("Error: You must set the environment variable PHO_GOOGLE_MAP_API_KEY")
        return
    c.run("uvicorn server:app --reload")

@task
def build_docker(c):
    for var in ["PHO_GOOGLE_MAP_API_KEY", "PHO_DOCKER_IMAGE_NAME"]:
        if var not in os.environ:
            print(f"Error: You must set the environment variable {var}")
            return -1
    c.run("docker build --build-arg PHO_GOOGLE_MAP_API_KEY=${PHO_GOOGLE_MAP_API_KEY} -t ${PHO_DOCKER_IMAGE_NAME} .")

@task
def run_docker(c):
    if "PHO_DOCKER_IMAGE_NAME" not in os.environ:
        print(f"Error: You must set the environment variable PHO_DOCKER_IMAGE_NAME")
        return -1
    c.run("docker run -p 8000:8000 -d ${PHO_DOCKER_IMAGE_NAME}")

@task
def push_docker(c):
    if "PHO_DOCKER_IMAGE_NAME" not in os.environ:
        print(f"Error: You must set the environment variable PHO_DOCKER_IMAGE_NAME")
        return -1
    c.run("docker push ${PHO_DOCKER_IMAGE_NAME}")
