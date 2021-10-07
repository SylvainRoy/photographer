#!/usr/bin/env python

import os
import json
import sys
import requests

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
def query(c, url='http://localhost:8000/locate/', query=None):
    if query is None:
        query = {"projections": [[1214.379914313618,1096.0557175343424],
                                 [1806.000898209996,1164.5591998802386],
                                 [2497.2633109731323,1158.3316105760662],
                                 [3568.4086712907847,946.5935742342047],
                                 [4595.960906479231,1033.7798244926182]],
                 "latlngs":[[45.9169134,7.0246497],
                            [45.8999213,7.0040026],
                            [45.8874995,7.0069444],
                            [45.8688259,6.9879852],
                            [45.8622473,6.9518381]]}
        query = json.dumps(query)
    print(f"\nQuery:\n{query}")
    r = requests.post(url, data=query)
    print(f"\nReply:\n{r.text}\n")


@task
def docker_build(c):
    check_env_var(["PHO_DOCKER_IMAGE_NAME", "PHO_GOOGLE_MAP_API_KEY"])
    c.run("docker build --build-arg PHO_GOOGLE_MAP_API_KEY=${PHO_GOOGLE_MAP_API_KEY} -t ${PHO_DOCKER_IMAGE_NAME} .")


@task
def docker_run(c):
    check_env_var(["PHO_DOCKER_IMAGE_NAME"])
    c.run("docker run -p 8000:80 -d ${PHO_DOCKER_IMAGE_NAME}")


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
    azure_url(c)

@task
def azure_url(c):
    check_env_var(["TF_VAR_PHO_URL"])
    r = c.run("cd terraform/azure && terraform show --json", hide=True)
    j = json.loads(r.stdout)
    url = j["values"]["root_module"]["resources"][0]["values"]["fqdn"]
    print(f"\nThe website is available at his url:\n\n  {url}")


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
