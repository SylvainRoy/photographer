# Where is the photographer


## introduction

Let say you have a picture with at least 5 identified points (e.g. summits) and that you want to determine from which location the picture has been taken, that's what this project is all about.

You may find the tool there: https://wherewasthephotographer.azurewebsites.net


## How To

The project relies on 'poetry' and 'invoke'.
To install all the dependencies:
  > poetry install

Then, check the various tasks:
  > invoke --list

And then, run one of them:
  > invoke unittest


## to do

- The url should be coming from an env variable:
  - dns_name_label      = "photographer-sroy"

- invoke task should say what to do next:
  - docker_run ==> docker stop ...

- invoke inject command

- improve invoke env variable check.

- port should be 80 when in azure
