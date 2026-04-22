# Space Flight Simulator — A 2-Hour Intro to 3D Graphics & Game Dev

Two parallel versions of the same lesson series:
- **JavaScript** — open any `index.html` in a browser, no install needed
- **Python** — `pip install pygame`, then `python lesson_XX_....py`

---

## Learning Path (~2 hours)

| Lesson | Topic | Key Concepts |
|--------|-------|--------------|
| 01 — Canvas / Pygame | Drawing & the game loop | Pixels, 2D coordinates, game loop, delta time |
| 02 — Vectors | The math of movement | `Vec3` class, add/sub/scale/dot/cross, velocity as a vector |
| 03 — Projection | Entering 3D | Perspective projection, focal length, depth sorting |
| 04 — Camera | Looking around | Pitch & yaw, forward/right/up vectors, world→camera transform |
| 05 — Physics | Thrust & zero gravity | Acceleration, Newton's 2nd law, Euler integration |
| 06 — Simulator | The complete game | Everything combined — fly! |

---

## JavaScript Version

Each lesson is a folder with three files:
- `index.html` — page structure, explanatory text, links to CSS and JS
- `../common.css` — shared dark-space theme (one file for all lessons)
- `main.js` — all the game logic for that lesson

Open `index.html` in any browser. No build step, no server required.

```
lesson_01_canvas/   index.html  main.js
lesson_02_vectors/  index.html  main.js
lesson_03_projection/ index.html  main.js
lesson_04_camera/   index.html  main.js
lesson_05_physics/  index.html  main.js
lesson_06_simulator/ index.html  main.js
common.css
```

---

## Python Version

Single `.py` file per lesson. Run directly with Python 3.

```bash
pip install pygame        # one-time install
python python/lesson_01_pygame.py
python python/lesson_02_vectors.py
# ... etc
```

```
python/
  lesson_01_pygame.py
  lesson_02_vectors.py
  lesson_03_projection.py
  lesson_04_camera.py
  lesson_05_physics.py
  lesson_06_simulator.py
  requirements.txt
```

---

## Controls (Lessons 4 – 6, both versions)

| Key | Action |
|-----|--------|
| `W` / `S` | Thrust forward / backward |
| `A` / `D` | Thrust left / right (strafe) |
| `↑` / `↓` | Pitch up / down |
| `←` / `→` | Yaw left / right |
| `Space` | Emergency brake |

---

## What You'll Learn

**Physics**
- Vectors: position, velocity, acceleration as the same mathematical object
- Newton's 1st law: in zero gravity, you drift forever once moving
- Newton's 2nd law: F = ma — thrust changes velocity, not position directly
- Euler integration: `vel += accel * dt`, `pos += vel * dt`

**3D Graphics**
- World space → camera space → screen space (the rendering pipeline)
- Perspective projection: why things look smaller when far away (division by Z)
- Euler angles (pitch and yaw) and deriving a camera rotation frame
- The painter's algorithm for depth sorting (and why real engines use a depth buffer)
- Focal length and its relationship to field of view

**Programming**
- The game loop pattern (`requestAnimationFrame` / `pygame.Clock`)
- Delta time for frame-rate independent movement
- Object-oriented design (`Vec3` class used across six lessons)
- Event-driven keyboard input
