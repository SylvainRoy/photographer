#!/usr/bin/env python

import os
import json
import sys

from invoke import task


@task
def check_env(c):
    check_env_var(
        [
            "PHO_GOOGLE_MAP_API_KEY",
            "PHO_DOCKER_IMAGE_NAME",
            "TF_VAR_PHO_URL"
        ],
        exit_on_error=False
    )

@task
def unittest(c):
    c.run("python -m unittest discover ./src")


@task
def score(c):
    c.run("python src/score.py")


@task
def run(c):
    check_env_var(["PHO_GOOGLE_MAP_API_KEY"])
    c.run("uvicorn --app-dir ./src server:app --reload")


@task
def query(c):
    #todo...
    #> curl -d '{"projections":[[1.2, 2.3], ...], "latlngs":[[1.3, 6.7], ...]}' -H "Content-Type: application/json" -X POST http://localhost:8000/locate/
    pass


@task
def docker_build(c):
    check_env_var(["PHO_DOCKER_IMAGE_NAME", "PHO_GOOGLE_MAP_API_KEY"])
    c.run("docker build --build-arg PHO_GOOGLE_MAP_API_KEY=${PHO_GOOGLE_MAP_API_KEY} -t ${PHO_DOCKER_IMAGE_NAME} .")


@task
def docker_run(c):
    check_env_var(["PHO_DOCKER_IMAGE_NAME"])
    c.run("docker run -p 8000:8000 -d ${PHO_DOCKER_IMAGE_NAME}")


@task
def docker_push(c):
    check_env_var(["PHO_DOCKER_IMAGE_NAME"])
    c.run("docker push ${PHO_DOCKER_IMAGE_NAME}")


@task
def azure_login(c):
    c.run("az login")


@task
def azure_deploy(c):
    check_env_var(["TF_VAR_PHO_URL"])
    c.run("az login")
    c.run("cd terraform/azure && terraform apply")


@task
def azure_url(c):
    check_env_var(["TF_VAR_PHO_URL"])
    r = c.run("cd terraform/azure && terraform show --json", hide=True)
    j = json.loads(r.stdout)
    url = j["values"]["root_module"]["resources"][0]["values"]["fqdn"]
    print(f"{url}")


@task
def azure_destroy(c):
    check_env_var(["TF_VAR_PHO_URL"])
    c.run("cd terraform/azure && terraform destroy")


def check_env_var(variables, exit_on_error=True):
    ok = True
    for var in variables:
        if var not in os.environ:
            print(f"- {var} environmnent variable is not set")
            ok = False
    if not ok:
        sys.exit(1)
