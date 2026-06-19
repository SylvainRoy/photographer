# Where is the photographer

## Introduction

Let say you have a picture with at least 5 identified points (e.g. summits) and that you want to determine from which location the picture has been taken, that's what this project is all about.

## How To

Run the unit tests:

```sh
uv run -m unittest discover .
```

Run the server, locally:

```sh
uv run uvicorn server:app --reload
```

Then open <http://localhost:8000/index.html>

Manually test the API:

```sh
curl -d '{"projections":[1.2, 3.4], "latlngs":[[1.3, 6.7], [5.4, 9.6]]}' -H "Content-Type: application/json" -X POST http://localhost:8000/locate/
```

Or with a data file:

```sh
curl -d "@data.json" -H "Content-Type: application/json" -X POST http://localhost:8000/locate/
```

Build the docker image:

```sh
docker build -t <user/repository> .
```

Run the docker image (the Google Maps API key is passed at runtime, never baked
into the image):

```sh
docker run -p 8000:8000 -e GOOGLE_MAPS_API_KEY=your-key-here -d <user/repository>
```

## Score evolution

### 09Apr21

No change of algo but 2 new cases.

-- Cases --

- nurnberg: 13 meters
- brevent2: 329 meters
- brevent3: 572 meters
- planpraz: 1315 meters
- aiguillemidi2: 600 meters
- aiguillemidi3: 569 meters
- frankfurt: 112 meters
- osterhofen: 558 meters
- statueofliberty: 6 meters
- aiguillemidi1: 688 meters

-- Summary --

10 cases
Average error: 476 meters

### 06Apr21

After fix on aiguillemidi3 (the projections were not in order).

-- Cases --

- brevent2: 329 meters
- brevent3: 572 meters
- planpraz: 1315 meters
- aiguillemidi2: 600 meters
- aiguillemidi3: 569 meters
- osterhofen: 558 meters
- statueofliberty: 6 meters
- aiguillemidi1: 688 meters

-- Summary --

8 cases
Average error: 579 meters

### 06Apr21 (new optimizer)

New optimizer to cope with symmetrical cases like aiguillemidi3.

-- Cases --

- brevent2: 329 meters
- brevent3: 572 meters
- planpraz: 1315 meters
- aiguillemidi2: 600 meters
- aiguillemidi3: 2448 meters
- osterhofen: 558 meters
- statueofliberty: 6 meters
- aiguillemidi1: 688 meters

-- Summary --

8 cases
Average error: 814 meters

### 04Apr21

-- Cases --

- brevent2: 396 meters
- brevent3: 434 meters
- planpraz: 1332 meters
- aiguillemidi2: 623 meters
- aiguillemidi3: 10054 meters
- osterhofen: 502 meters
- statueofliberty: 0 meters
- aiguillemidi1: 694 meters

-- Summary --

8 cases
Average error: 1754 meters
