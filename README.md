# Where is the photographer

Let say you have a picture with at least 5 identified points (e.g. summits) and that you want to determine from which point the picture has been taken, that's what this project does.

## Todo

 - ph.py should be main.py and call optimizer.py (then, there could be other optimizer)
 - the solver should provide a JSON api
 - there should be room for several solver
 - the solver should provider a web UI
 - the whole thing should run in a docker
 - other optimization mimimization (e.g. x^3)
 - better handling of situation where the optimization get out of the acceptable zone
 - (more) real pictures!!!

 ## Done

 - the Map class should be in a different file
 - the Map class should only do display. No computation
