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

 - the solver should provide a JSON api
 - the solver should provider a web UI
 - the whole thing should run in a docker
 - scoring mechanism to rank optimizers
    - other optimization mimimization (e.g. x^3)
 - better handling of situation where the optimization get out of the acceptable zone


## Notes on the AJAX call

### Post request

#### Prefered option

  const data = { username: 'example' };

  fetch('https://example.com/profile', {
    method: 'POST', // or 'PUT'
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  .then(response => response.json())
  .then(data => {
    console.log('Success:', data);
  })
  .catch((error) => {
    console.error('Error:', error);
  });

#### Other option: good old way

  var xhr = new XMLHttpRequest();
  xhr.open("POST", '/server', true);

  //Send the proper header information along with the request
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

  xhr.onreadystatechange = function() { // Call a function when the state changes.
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
          // Request finished. Do processing here.
      }
  }
  xhr.send("foo=bar&lorem=ipsum");
  // xhr.send(new Int8Array());
  // xhr.send(document);


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