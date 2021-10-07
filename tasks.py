#!/usr/bin/env python

import os
import json

from invoke import task


@task
def check(c):
    if "PHO_GOOGLE_MAP_API_KEY" not in os.environ:
        print("- environment variable PHO_GOOGLE_MAP_API_KEY is not set!")
    if "PHO_DOCKER_IMAGE_NAME" not in os.environ:
        print("- environment variable PHO_DOCKER_IMAGE_NAME is not set!")


@task
def unittest(c):
    c.run("python -m unittest discover ./src")


@task
def score(c):
    c.run("python src/score.py")


@task
def run(c):
    if "PHO_GOOGLE_MAP_API_KEY" not in os.environ:
        print("Error: You must set the environment variable PHO_GOOGLE_MAP_API_KEY")
        return
    c.run("uvicorn --app-dir ./src server:app --reload")


@task
def query(c):
    #todo...
    #> curl -d '{"projections":[[1.2, 2.3], ...], "latlngs":[[1.3, 6.7], ...]}' -H "Content-Type: application/json" -X POST http://localhost:8000/locate/
    pass


@task
def docker_build(c):
    for var in ["PHO_GOOGLE_MAP_API_KEY", "PHO_DOCKER_IMAGE_NAME"]:
        if var not in os.environ:
            print(f"Error: You must set the environment variable {var}")
            return -1
    c.run("docker build --build-arg PHO_GOOGLE_MAP_API_KEY=${PHO_GOOGLE_MAP_API_KEY} -t ${PHO_DOCKER_IMAGE_NAME} .")


@task
def docker_run(c):
    if "PHO_DOCKER_IMAGE_NAME" not in os.environ:
        print(f"Error: You must set the environment variable PHO_DOCKER_IMAGE_NAME")
        return -1
    c.run("docker run -p 8000:8000 -d ${PHO_DOCKER_IMAGE_NAME}")


@task
def docker_push(c):
    if "PHO_DOCKER_IMAGE_NAME" not in os.environ:
        print(f"Error: You must set the environment variable PHO_DOCKER_IMAGE_NAME")
        return -1
    c.run("docker push ${PHO_DOCKER_IMAGE_NAME}")


@task
def azure_login(c):
    c.run("az login")


@task
def azure_deploy(c):
    if "TF_VAR_PHO_URL" not in os.environ:
        print(f"Error: You must set the environment variable TF_VAR_PHO_URL")
        return -1
    c.run("az login")
    c.run("cd terraform/azure && terraform apply")


@task
def azure_url(c):
    if "TF_VAR_PHO_URL" not in os.environ:
        print(f"Error: You must set the environment variable TF_VAR_PHO_URL")
        return -1
    r = c.run("cd terraform/azure && terraform show --json", hide=True)
    j = json.loads(r.stdout)
    url = j["values"]["root_module"]["resources"][0]["values"]["fqdn"]
    print(f"{url}:8000")


@task
def azure_destroy(c):
    if "TF_VAR_PHO_URL" not in os.environ:
        print(f"Error: You must set the environment variable TF_VAR_PHO_URL")
        return -1
    c.run("cd terraform/azure && terraform destroy")
