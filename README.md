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
    - create json files in all data examples.
    - ability to get new coordinates/positions from UI
      - just a js function to call from the console.

 - Map able to display with x,y and with lat,lng.             OK
    - Map(picture | (x,y)).set_latlng_ref(...)

 - New notebook
    - Show picture with markers
    - Show map with markers
      - from lat&lng directly
    - Show map with area + init + search
 
 Notebooks reorganisation
    - localisation - x,y
    - localisation - lat,lon
    - localisation - initialisation

 - statueofliberty is broken with current init
    - the init should be closer to the summits
 - main.py should run all the cases in data and return a score
 - handling of error from server in the UI
 - better handling of situation where the optimization get out of the acceptable zone
 - test accuracy with only three points
 - remove dead code.
 - github repo
 - deployment in Azure
 - fix CB in Azure
 
