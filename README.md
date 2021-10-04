# Where is the photographer


## introduction

Let say you have a picture with at least 5 identified points (e.g. summits) and that you want to determine from which location the picture has been taken, that's what this project is all about.

You can find the tool there: https://wherewasthephotographer.azurewebsites.net


## How To

Run the unit tests:
  > python -m unittest discover .

Run the server, locally:
  > export PHO_GOOGLE_MAP_API_KEY=your_google_map_api_key
  > uvicorn server:app --reload
  Then open http://localhost:8000

Manually test the API:
  > curl -d '{"projections":[[1.2, 2.3], ...], "latlngs":[[1.3, 6.7], ...]}' -H "Content-Type: application/json" -X POST http://localhost:8000/locate/

Or with a data file:
  > curl -d "@data.json" -H "Content-Type: application/json" -X POST http://localhost:8000/locate/

Build the docker image:
  > export PHO_GOOGLE_MAP_API_KEY=your_google_map_api_key
  > docker build --build-arg PHO_GOOGLE_MAP_API_KEY=${PHO_GOOGLE_MAP_API_KEY} -t <user/image> .

Run the docker image:
  > docker run -p 8000:8000 -d <user/image>

Push it to dockerhub:
  > docker push <user/image>
