# Where is the photographer


## introduction

Let say you have a picture with at least 5 identified points (e.g. summits) and that you want to determine from which point the picture has been taken, that's what this project does.


## How To

Run the unit tests:
  > python -m unittest discover .

Run the server, locally:
  > uvicorn server:app --reload

Understand how it works:
 - Check the notebook 'Locate Photograper'


## Todo

 - the solver should provide a JSON api
 - the solver should provider a web UI
 - the whole thing should run in a docker
 - scoring mechanism to rank optimizers
    - other optimization mimimization (e.g. x^3)
 - better handling of situation where the optimization get out of the acceptable zone



## Notes on marker.js

### Uploading an image in the page

 - This tutorial:
    - https://www.youtube.com/watch?v=VElnT8EoEEM&ab_channel=dcode
 - And the associated code:
    - https://svelte.dev/repl/b5333059a2f548809a3ac3f60a17a8a6?version=3.31.2

### Anotating the image with markers:

 - https://markerjs.com/


## Notes on the integration of the map

Using Google Maps API.

To do before to get started:
 - https://developers.google.com/maps/gmp-get-started

google.maps.Map class
 - constructor(
    - mapDiv:div object return by getElementById(),
    - opts?: {center:..., zoom:...}           
 - getBounds() -> LatLngBounds
 - addListener(eventName:string, handler:fun) -> MapsEventListener
    - eventName: "click"
    - fun(event:MapMouseEvent or IconMouseEvent)

google.maps.MapMouseEvent & google.maps.IconMouseEvent interfaces
 - description:
    - both event contain the below. So canbe treated in the same way.
    - fired when the user clicks on the map.
 - properties:
    - latLng: The lat/long that was below the cursos when the event occured

google.maps.LatLng class
- description:
  - No need to build it, most functions accept {lat: -34, lng: 151}
- metods:
  - lat()
  - lon()
  - toJSON()
  - toString()
  - toUrlValue()

Markers is the way to have points on the map.

google.maps.Marker
 - ref:
    - https://developers.google.com/maps/documentation/javascript/markers?hl=en
 - properties:
    - position
    - map
    - title
 - methods:
    - setMap(map)
        - map == null --> erase marker


The following piece of code seems really close to what I want (ref: https://developers.google.com/maps/documentation/javascript/markers?hl=en#maps_marker_labels-javascript)


    // In the following example, markers appear when the user clicks on the map.
    // Each marker is labeled with a single alphabetical character.
    const labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    let labelIndex = 0;
    
    function initMap() {
      const bangalore = { lat: 12.97, lng: 77.59 };
      const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: bangalore,
      });
      // This event listener calls addMarker() when the map is clicked.
      google.maps.event.addListener(map, "click", (event) => {
        addMarker(event.latLng, map);
      });
      // Add a marker at the center of the map.
      addMarker(bangalore, map);
    }
    
    // Adds a marker to the map.
    function addMarker(location, map) {
      // Add the marker at the clicked location, and add the next-available label
      // from the array of alphabetical characters.
      new google.maps.Marker({
        position: location,
        label: labels[labelIndex++ % labels.length],
        map: map,
      });
    }