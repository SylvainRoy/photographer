# Where is the photographer


## introduction

Let say you have a picture with at least 5 identified points (e.g. summits) and that you want to determine from which point the picture has been taken, that's what this project does.


## How To

Run the unit tests:
  > python -m unittest discover .
  

## Todo

 - the solver doesn't work anymore for statueofliberty. The initial position lead to a wrong local optimum.
 - the solver should provide a JSON api
 - the solver should provider a web UI
 - the whole thing should run in a docker
 - other optimization mimimization (e.g. x^3)
 - better handling of situation where the optimization get out of the acceptable zone


 ## Done

 - the Map class should be in a different file
 - the Map class should only do display. No computation
 - (more) real pictures!!!
 - ph.py should be split in optimizer1.py and main.py
 - there should be room for several solver
 - Start a new optimizer:
    - position_lens should be compute_projections_on_picture
        - the alphas are not limited between 0 and 1 (the dimensions on the picture
        and on the map are mixed while probably not in the same units!)
        - the way it projects s2_ to sM_ seems wrong in the limit cases of an alpha = 0
    - optimize_photographer should be find_photographer
        - search to consider alpha bigger that 1
            - OR scale picture according to alpha
        - Internal error function should be a std function called evaluate_picture_position
 - hot_colorize is probably buggy. Triple check new version and replace old one.
 - split computation and display to be able to tweak afterward.
 - optimise_picture return result (much) bigger than 1. How come?
    - Cause the projection can be outside of the picture, so normalizing with the max distance of the summits doesn't necessarily bring it below 1.
 - hot_colorize to use a log scale for the color
