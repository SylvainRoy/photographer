# Where is the photographer


## introduction

Let say you have a picture with at least 5 identified points (e.g. summits) and that you want to determine from which location the picture has been taken, that's what this project is all about.


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

Build the docker image:
  > poetry export -f requirements.txt -o requirements.txt
  > docker build -t <user/repository> .

Run the docker image:
  > docker run -p 8000:8000 -d sroy/photographer

Push it to dockerhub:
  > docker push sroy/photographer:1


## Todo

 - "url/index.html" should be "url".

 - image in brevent should be without numbers.

 - the newly added 'X' marker should have a different color on the map.

 - when resizing the browser, the picture and marker shoud be resized/repositioned.


## Score evolution

### 09Apr21

No change of algo but 2 new cases.

-- Cases --
 -  nurnberg: 13 meters
 -  brevent2: 329 meters
 -  brevent3: 572 meters
 -  planpraz: 1315 meters
 -  aiguillemidi2: 600 meters
 -  aiguillemidi3: 569 meters
 -  frankfurt: 112 meters
 -  osterhofen: 558 meters
 -  statueofliberty: 6 meters
 -  aiguillemidi1: 688 meters
-- Summary --
10 cases
Average error: 476 meters

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