"""
============================================================
LESSON 3: 3D PERSPECTIVE PROJECTION
============================================================
Run:  python lesson_03_projection.py

Goals:
  - Add a Z axis: planets live in 3D space
  - Understand the perspective projection formula
  - Draw planets at their projected 2D positions
  - Use the painter's algorithm (sort by depth, draw farthest first)
  - See how focal length controls the field of view

Camera: fixed at (0,0,0), always looking in the +Z direction.
We add rotation in Lesson 4.
============================================================
"""

import pygame
import sys
import random
import math


# ============================================================
# VEC3  (same as Lesson 2)
# ============================================================
class Vec3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = float(x), float(y), float(z)

    def sub(self, v):      return Vec3(self.x-v.x, self.y-v.y, self.z-v.z)
    def scale(self, s):    return Vec3(self.x*s,   self.y*s,   self.z*s  )
    def dot(self, v):      return self.x*v.x + self.y*v.y + self.z*v.z
    def length(self):      return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    def normalize(self):
        l = self.length()
        return Vec3() if l == 0 else self.scale(1/l)


# ============================================================
# PYGAME SETUP
# ============================================================
pygame.init()
WIDTH, HEIGHT = 700, 460
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 3 — 3D Projection")
clock = pygame.time.Clock()
font  = pygame.font.SysFont("Courier New", 11)

# Canvas center = where the projection is centered.
CX, CY = WIDTH // 2, HEIGHT // 2

# FOCAL LENGTH controls field of view.
#
#   screenX = (worldX / worldZ) * FOCAL_LENGTH + CX
#
#   Intuition: hold a ruler 1 foot from your eye vs 10 feet.
#   At 10 feet it looks 10× smaller — that's division by Z.
#
#   FOCAL_LENGTH acts like the zoom of a camera lens:
#     larger → narrower view (telephoto)
#     smaller → wider view (wide angle)
#
#   A common formula:  FOCAL_LENGTH = (screen_half_width) / tan(half_FOV)
#   For 60° FOV:       FOCAL_LENGTH = 350 / tan(30°) ≈ 606
#   We use 500 for a slightly wide view.
FOCAL_LENGTH = 500
NEAR_CLIP    = 1.0    # don't project anything at depth ≤ this


# ============================================================
# PERSPECTIVE PROJECTION
# ============================================================
def project(world_x, world_y, world_z):
    """
    Project a 3D world point to 2D screen coordinates.

    Formula:
        screen_x = (world_x / world_z) * FOCAL_LENGTH + CX
        screen_y = (−world_y / world_z) * FOCAL_LENGTH + CY

    Why −world_y?
        World Y increases upward (like math).
        Screen Y increases downward.
        Negating flips the axis so 'up in the world' = 'up on screen'.

    Returns (sx, sy, scale) or None if the point is behind the camera.
    scale = FOCAL_LENGTH / world_z — how large things appear at this depth.
    """
    if world_z <= NEAR_CLIP:
        return None    # behind the camera — don't draw

    sx    =  (world_x / world_z) * FOCAL_LENGTH + CX
    sy    = -(world_y / world_z) * FOCAL_LENGTH + CY   # negate y to flip axis
    scale = FOCAL_LENGTH / world_z
    return sx, sy, scale


# ============================================================
# STARS
# ============================================================
# Stars are unit-direction vectors pointing outward in all directions.
# For a fixed camera, we just project them as very distant points.
NUM_STARS = 220
stars = []
for _ in range(NUM_STARS):
    theta  = random.uniform(0, math.pi * 2)
    phi    = math.acos(random.uniform(-1, 1))    # uniform distribution on sphere
    stars.append({
        "dir":  Vec3(
            math.sin(phi) * math.cos(theta),
            math.sin(phi) * math.sin(theta),
            math.cos(phi)
        ),
        "brightness": random.randint(100, 220),
        "size": max(1, int(random.uniform(0.5, 1.8))),
    })


# ============================================================
# PLANETS
# ============================================================
PALETTE = [
    (58,  111, 204),   # blue
    (204,  85,  51),   # orange-red
    (119,  68,  34),   # brown
    ( 68, 119,  85),   # green
    (153, 136,  51),   # gold
    (153,  68, 170),   # purple
    ( 51, 102, 136),   # teal
    (170, 102,  51),   # amber
]
NAMES = ["Hydra","Ignis","Magna","Virid","Lutea","Ceres","Nebula","Ferro",
         "Glacis","Pyrex","Umbra","Solus","Terra","Argon","Noctis"]

planets = []
for i in range(15):
    planets.append({
        "pos": Vec3(
            random.uniform(-450, 450),    # x: -450 to 450
            random.uniform(-350, 350),    # y: -350 to 350  (world y = up)
            random.uniform(80, 2080)      # z: 80–2080  (must be > 0 for camera to see them)
        ),
        "radius": random.uniform(8, 53),
        "color":  PALETTE[i % len(PALETTE)],
        "name":   NAMES[i % len(NAMES)],
    })


# ============================================================
# MAIN LOOP
# ============================================================
running = True
while running:
    clock.tick(60)   # cap at 60fps (no dt needed — camera is static this lesson)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # ---- Draw ----
    screen.fill((5, 8, 16))

    # Stars — project direction as a very distant point
    for star in stars:
        d = star["dir"]
        if d.z <= 0:
            continue    # behind camera
        sx = (d.x / d.z) * FOCAL_LENGTH + CX
        sy = -(d.y / d.z) * FOCAL_LENGTH + CY
        if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
            c = star["brightness"]
            pygame.draw.circle(screen, (c, c, c), (int(sx), int(sy)), star["size"])

    # Planets — PAINTER'S ALGORITHM:
    # Sort by depth descending (farthest first), draw in that order.
    # Each planet paints over whatever is behind it.
    sorted_planets = sorted(planets, key=lambda p: -p["pos"].z)

    for planet in sorted_planets:
        p    = planet["pos"]
        proj = project(p.x, p.y, p.z)
        if proj is None:
            continue

        sx, sy, scale = proj

        # Apparent radius:  world_radius / depth × focal_length
        # Same division-by-depth logic as the position projection.
        apparent_radius = planet["radius"] * scale
        if apparent_radius < 0.5:
            continue    # too small to see

        pygame.draw.circle(screen, planet["color"], (int(sx), int(sy)), max(1, int(apparent_radius)))

        # Faint outline
        pygame.draw.circle(screen, (255, 255, 255), (int(sx), int(sy)), max(1, int(apparent_radius)), 1)

        # Name label (only if big enough to read)
        if apparent_radius > 10:
            lbl = font.render(planet["name"], True, (190, 210, 255))
            screen.blit(lbl, (int(sx) - lbl.get_width()//2, int(sy) - int(apparent_radius) - 14))

        # Depth label (teaching aid — shows Z value)
        if apparent_radius > 5:
            z_lbl = font.render(f"z={int(p.z)}", True, (100, 130, 160))
            screen.blit(z_lbl, (int(sx) - z_lbl.get_width()//2, int(sy) + int(apparent_radius) + 3))

    # Crosshair at screen center
    pygame.draw.line(screen, (80, 80, 100), (CX - 12, CY), (CX + 12, CY), 1)
    pygame.draw.line(screen, (80, 80, 100), (CX, CY - 12), (CX, CY + 12), 1)

    # Info label
    lbl = font.render(f"camera at (0, 0, 0)  focal_length={FOCAL_LENGTH}", True, (100, 130, 170))
    screen.blit(lbl, (10, 10))

    pygame.display.flip()


pygame.quit()
sys.exit()
