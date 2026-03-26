# Python 3D Rendering Basics (Kid-Friendly)

This folder contains six self-contained mini lessons that build from 2D points to a rotating 3D wireframe cube using minimal libraries.

## Requirements

- Python 3.10+ (or newer)
- `pygame` (for the window and drawing lines/points)
- Uses only:
  - `pygame` for window/input/drawing
  - `math` for trig and vector math

## Lesson Files

1. `lesson1_points.py`  
   Screen coordinates and plotting points.

2. `lesson2_vectors.py`  
   Vectors as arrows and vector length.

3. `lesson3_rotation_2d.py`  
   2D rotation matrix applied to a shape.

4. `lesson4_rotate_3d_points.py`  
   3D point tuples and X/Y axis rotations (printed output).

5. `lesson5_projection.py`  
   Perspective projection from 3D points to 2D screen.

6. `lesson6_wireframe_cube.py`  
   End-to-end 3D pipeline: transform, project, draw.

## Install

From this folder:


python -m pip install pygame


If your machine uses `python3`:


python3 -m pip install pygame


## How To Run

From this folder:

python lesson1_points.py
python lesson2_vectors.py
python lesson3_rotation_2d.py
python lesson4_rotate_3d_points.py
python lesson5_projection.py
python lesson6_wireframe_cube.py


If `python` points to Python 2 on your machine, use:


python3 lesson1_points.py


