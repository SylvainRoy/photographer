# Where is the photographer


## introduction

Let say you have a picture with at least 5 identified points (e.g. summits) and that you want to determine from which point the picture has been taken, that's what this project does.


## How To

Run the unit tests:
  > python -m unittest discover .

Run the server, locally:
  > uvicorn server:app --reload
  Then open http://localhost:8000/index.html

Manually test the API:
  > curl -d '{"projections":[1.2, 3.4], "latlng":[[1.3, 6.7], [5.4, 9.6]]}' -H "Content-Type: application/json" -X POST http://localhost:8000/locate/

Or with a data file:
  > curl -d "@data.json" -H "Content-Type: application/json" -X POST http://localhost:8000/locate/

Run the docker image:
  > docker run -p 8000:8000 -d sroy/photographer

Build the docker image:
  > poetry export -f requirements.txt -o requirements.txt
  > docker build -t <user/repository> .

Understand how it works:
 - Check the notebook 'Locate Photograper'


## Todo

 - tests available from UI
    - config in json file                                     OK
    - service to discover & get json on server side           OK
    - ability to load a test in UI                            OK
    - create json files in all data examples.                 OK
    - ability to get new coordinates/positions from UI        OK

 - Map able to display with x,y and with lat,lng.             OK

 - New notebook
    - Show picture with markers
    - Show map with markers
      - from lat&lng directly
    - Show map with area + init + search
 
  - Investigation;
    - statueofliberty is broken:
      - it used to be much more accurate
        - an init closer to the building was working better. Maybe the issue.
      - removing the thin building close to central park gets to an impossible picture!
        - That doesn't make sense: less points makes it "more" possible.
    - aiguillemidi2
      - raise an exception when used with lat&lng

 - main.py should run all the cases in data and return a score
 - handling of error from server in the UI
 - better handling of situation where the optimization get out of the acceptable zone
 - remove dead code.
 - github repo
 - deployment in Azure
 - fix CB in Azure
 
