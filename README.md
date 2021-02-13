# Where is the photographer


## introduction

Let say you have a picture with at least 5 identified points (e.g. summits) and that you want to determine from which point the picture has been taken, that's what this project does.


## How To

Run the unit tests:
  > python -m unittest discover .

Run the server, locally:
  > uvicorn server:app --reload
  Then open http://localhost:8000/index.html#

Manually test the API:
  > curl -d '{"projections":[1.2, 3.4], "latlng":[[1.3, 6.7], [5.4, 9.6]]}' -H "Content-Type: ST http://localhost:8000/locate/

Or with a data file:
  > curl -d "@data.json" -H "Content-Type: ST http://localhost:8000/locate/

Run the docker image:
  > docker run -p 8000:8000 -d sroy/photographer

Build the docker image:
  > poetry export -f requirements.txt -o requirements.txt
  > docker build -t <user/repository> .

Understand how it works:
 - Check the notebook 'Locate Photograper'


## Todo

 - better handling of situation where the optimization get out of the acceptable zone
 - test accuracy with only three points
 - remove dead code.

