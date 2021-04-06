# Where is the photographer


## introduction

Let say you have a picture with at least 5 identified points (e.g. summits) and that you want to determine from which location the picture has been taken, that's what this project does.


## How To

Run the unit tests:
  > python -m unittest discover .

Run the server, locally:
  > uvicorn server:app --reload
  Then open http://localhost:8000/index.html

Manually test the API:
  > curl -d '{"projections":[1.2, 3.4], "latlngs":[[1.3, 6.7], [5.4, 9.6]]}' -H "Content-Type: application/json" -X POST http://localhost:8000/locate/

Or with a data file:
  > curl -d "@data.json" -H "Content-Type: application/json" -X POST http://localhost:8000/locate/

Run the docker image:
  > docker run -p 8000:8000 -d sroy/photographer

Build the docker image:
  > poetry export -f requirements.txt -o requirements.txt
  > docker build -t <user/repository> .

Understand how it works:
 - Check the notebook 'locate.ipynb'


## Todo

  - Investigation:

    - locate.ipynb fails miserably for aiguillemidi3 while the same case is ok on the web interface?!
      - in fact, it 'works' in both case. The issue was that the result of the search is the 'init'. So, on the notebook, it got hidden by the init icon.
      - Now, it raises a question: how come the search doesn't find anything better?!

    - Fix all notebooks
      - meta:             ok
      - sesitivity:       ok
      - initialisation:   ok
      - map:              error!
      - locatelatlngs:    error!
        - doesn't work for aiguillemidi3 while the web interface works ok.

    - The map latlng to xy feature seems completely broken?!
 
 - better handling of situation where the optimization get out of the acceptable zone
    - e.g. maximum 400 km?

 - remove dead code.

 - github repo
    - then, udpate readme & index.html with this info

 - deployment in Azure
    - fix CB in Azure

 - Improve Map class
    - Map(basemap|dimensions=200, 200).calibrate(....).draw_XXXX(...).zoom(...).show()
    - Map param:
        - file OR dimension OR nothing(sensible default)
        - y_origin


## Score evolution

### 06Apr21

After fix on aiguillemidi3 (the projections were not in order).

-- Cases --
 -  brevent2: 329 meters
 -  brevent3: 572 meters
 -  planpraz: 1315 meters
 -  aiguillemidi2: 600 meters
 -  aiguillemidi3: 569 meters
 -  osterhofen: 558 meters
 -  statueofliberty: 6 meters
 -  aiguillemidi1: 688 meters
-- Summary --
8 cases
Average error: 579 meters

### 06Apr21

new optimizer to cope with symmetrical cases like aiguillemidi3.

-- Cases --
 -  brevent2: 329 meters
 -  brevent3: 572 meters
 -  planpraz: 1315 meters
 -  aiguillemidi2: 600 meters
 -  aiguillemidi3: 2448 meters
 -  osterhofen: 558 meters
 -  statueofliberty: 6 meters
 -  aiguillemidi1: 688 meters
-- Summary --
8 cases
Average error: 814 meters

### 04Apr21

-- Cases --
-  brevent2: 396 meters
-  brevent3: 434 meters
-  planpraz: 1332 meters
-  aiguillemidi2: 623 meters
-  aiguillemidi3: 10054 meters
-  osterhofen: 502 meters
-  statueofliberty: 0 meters
-  aiguillemidi1: 694 meters
-- Summary --
8 cases
Average error: 1754 meters