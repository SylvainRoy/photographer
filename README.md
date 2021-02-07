# Where is the photographer


## introduction

Let say you have a picture with at least 5 identified points (e.g. summits) and that you want to determine from which point the picture has been taken, that's what this project does.


## How To

Run the unit tests:
  > python -m unittest discover .

Run the server, locally:
  > uvicorn server:app --reload

Manually test the server:
  curl -d '{"projections":[1.2, 3.4], "latlng":[[1.3, 6.7], [5.4, 9.6]]}' -H "Content-Type: ST http://localhost:8000/locate/

or with a data file:
  curl -d "@data.json" -H "Content-Type: ST http://localhost:8000/locate/

Understand how it works:
 - Check the notebook 'Locate Photograper'


## Todo

 - the solver doesn't work anymore for statueofliberty. The initial position lead to a wrong local optimum.
 - the solver should provide a JSON api
 - the solver should provider a web UI
 - the whole thing should run in a docker
 - scoring mechanism to rank optimizers
    - other optimization mimimization (e.g. x^3)
 - better handling of situation where the optimization get out of the acceptable zone
 - test accuracy with only three points
 - remove dead code.

## Notes

### JSON

write:
  JSON.stringify({"action":"status", "switch":"west"})

read:
  var arr = JSON.parse(response);


## Notes on the API

{
  projections: [123, 456, ...],
  latlng: [
    [45.123, 7.456],
    [47.123, 14.456],
    ...
  ]
}

{
  projections: [123, 456, ...],
  coord: [
    [45.123, 7.456],
    [47.123, 14.456],
    ...
  ]
}