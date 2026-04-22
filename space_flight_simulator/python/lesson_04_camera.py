"""
============================================================
LESSON 4: CAMERA ORIENTATION — PITCH AND YAW
============================================================
Run:  python lesson_04_camera.py
Controls:  Arrow keys

Goals:
  - Represent camera rotation with yaw and pitch angles
  - Derive the camera's local forward / right / up vectors
  - Transform world-space points into camera-local space
  - Arrow keys rotate the camera; planets and stars move accordingly

NEW this lesson:
  - compute_camera_vectors() — angles → forward, right, up
  - world_to_camera()        — world point → camera-local coordinates
  - Stars correctly rotate when you look around
============================================================
"""

import pygame
import sys
import random
import math


# ============================================================
# VEC3
# ============================================================
class Vec3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = float(x), float(y), float(z)

    def add(self, v):      return Vec3(self.x+v.x, self.y+v.y, self.z+v.z)
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
pygame.display.set_caption("Lesson 4 — Camera Orientation")
clock = pygame.time.Clock()
font  = pygame.font.SysFont("Courier New", 11)

CX, CY       = WIDTH // 2, HEIGHT // 2
FOCAL_LENGTH = 500
NEAR_CLIP    = 1.0
TURN_SPEED   = 1.1   # radians per second


# ============================================================
# CAMERA STATE
# ============================================================
# Camera is fixed at the world origin.
# Rotation is stored as two Euler angles.

yaw   = 0.0    # rotation around world Y (left/right)
pitch = 0.0    # tilt up/down (clamped to ±89° to avoid gimbal flip)


# ============================================================
# CAMERA BASIS VECTORS
# ============================================================
def compute_camera_vectors(yaw, pitch):
    """
    Compute the three unit vectors that define the camera's orientation.

    We start with default axes:
      forward = (0, 0, 1)   — looking down +Z
      right   = (1, 0, 0)
      up      = (0, 1, 0)

    Apply yaw rotation (around Y), then pitch rotation (around local X).
    The result is the camera's current forward, right, and up in world space.

    These three vectors together ARE the rotation matrix — just written as
    three separate Vec3s rather than a 3×3 array.
    """
    cos_p, sin_p = math.cos(pitch), math.sin(pitch)
    cos_y, sin_y = math.cos(yaw),   math.sin(yaw)

    # FORWARD — direction the camera is pointing after yaw+pitch rotation
    forward = Vec3(cos_p * sin_y,   sin_p,   cos_p * cos_y)

    # RIGHT — 90° to the right of forward, staying in the horizontal plane.
    # We omit pitch here (ry = 0) so strafing stays horizontal.
    right   = Vec3(cos_y,   0.0,   -sin_y)

    # UP — perpendicular to both forward and right.
    # Computed directly from angles to avoid accumulated floating-point drift.
    up      = Vec3(-sin_p * sin_y,   cos_p,   -sin_p * cos_y)

    return forward, right, up


# ============================================================
# WORLD → CAMERA TRANSFORM
# ============================================================
def world_to_camera(world_point, forward, right, up):
    """
    Express a world-space point in the camera's local coordinate frame.

    Steps:
      1. Subtract camera position (at origin here, so this is just the point itself).
      2. Dot-product with each camera axis.

    The dot product projects the vector onto each axis —
    this IS matrix multiplication, written out explicitly.

    Result:
      cam.x = how far RIGHT the point is from camera center
      cam.y = how far UP
      cam.z = depth (how far FORWARD — what we divide by during projection)
    """
    # Camera is at origin, so no position subtraction needed in this lesson.
    rel = world_point   # will become: world_point.sub(camera_pos) in Lesson 5

    return Vec3(
        rel.dot(right),      # camera-local x
        rel.dot(up),         # camera-local y
        rel.dot(forward)     # camera-local z (depth)
    )


def project(cam_point):
    """Project camera-space point to screen. Returns (sx, sy, scale) or None."""
    if cam_point.z <= NEAR_CLIP:
        return None
    sx    =  (cam_point.x / cam_point.z) * FOCAL_LENGTH + CX
    sy    = -(cam_point.y / cam_point.z) * FOCAL_LENGTH + CY
    scale =  FOCAL_LENGTH / cam_point.z
    return sx, sy, scale


# ============================================================
# WORLD SETUP
# ============================================================
NUM_STARS = 250
stars = []
for _ in range(NUM_STARS):
    theta = random.uniform(0, math.pi * 2)
    phi   = math.acos(random.uniform(-1, 1))
    stars.append({
        "dir": Vec3(math.sin(phi)*math.cos(theta), math.sin(phi)*math.sin(theta), math.cos(phi)),
        "brightness": random.randint(100, 220),
        "size": max(1, int(random.uniform(0.5, 1.8))),
    })

PALETTE = [(58,111,204),(204,85,51),(119,68,34),(68,119,85),
           (153,136,51),(153,68,170),(51,102,136),(170,102,51)]
NAMES   = ["Hydra","Ignis","Magna","Virid","Lutea","Ceres","Nebula","Ferro",
           "Glacis","Pyrex","Umbra","Solus","Terra","Argon","Noctis"]

planets = []
for i in range(15):
    planets.append({
        "pos":    Vec3(random.uniform(-500, 500), random.uniform(-400, 400), random.uniform(80, 2080)),
        "radius": random.uniform(8, 53),
        "color":  PALETTE[i % len(PALETTE)],
        "name":   NAMES[i % len(NAMES)],
    })


# ============================================================
# MAIN LOOP
# ============================================================
MAX_PITCH = math.pi / 2 - 0.01    # clamp pitch to ±89°

running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False

    # ---- Input: rotate camera ----
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  yaw   -= TURN_SPEED * dt
    if keys[pygame.K_RIGHT]: yaw   += TURN_SPEED * dt
    if keys[pygame.K_UP]:    pitch += TURN_SPEED * dt
    if keys[pygame.K_DOWN]:  pitch -= TURN_SPEED * dt

    # Clamp pitch so the camera doesn't flip upside down
    pitch = max(-MAX_PITCH, min(MAX_PITCH, pitch))

    # ---- Recompute camera basis ----
    forward, right, up = compute_camera_vectors(yaw, pitch)

    # ---- Draw ----
    screen.fill((5, 8, 16))

    # Stars — transform direction into camera space, then project
    for star in stars:
        # For stars (infinitely far), we only rotate the direction — no position offset.
        cam_dir = Vec3(
            star["dir"].dot(right),
            star["dir"].dot(up),
            star["dir"].dot(forward)
        )
        if cam_dir.z <= 0:
            continue
        sx = (cam_dir.x / cam_dir.z) * FOCAL_LENGTH + CX
        sy = -(cam_dir.y / cam_dir.z) * FOCAL_LENGTH + CY
        if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
            c = star["brightness"]
            pygame.draw.circle(screen, (c, c, c), (int(sx), int(sy)), star["size"])

    # Planets — transform then project; depth-sort for painter's algorithm
    projected = []
    for planet in planets:
        cam_pt = world_to_camera(planet["pos"], forward, right, up)
        proj   = project(cam_pt)
        if proj:
            projected.append((cam_pt.z, planet, proj))

    projected.sort(reverse=True)    # farthest first (largest z first)

    for _, planet, (sx, sy, scale) in projected:
        r = planet["radius"] * scale
        if r < 0.5: continue

        pygame.draw.circle(screen, planet["color"], (int(sx), int(sy)), max(1, int(r)))
        pygame.draw.circle(screen, (255,255,255), (int(sx), int(sy)), max(1, int(r)), 1)

        if r > 10:
            lbl = font.render(planet["name"], True, (190, 210, 255))
            screen.blit(lbl, (int(sx) - lbl.get_width()//2, int(sy) - int(r) - 14))

    # Crosshair
    pygame.draw.line(screen, (80,80,100), (CX-12, CY), (CX+12, CY), 1)
    pygame.draw.line(screen, (80,80,100), (CX, CY-12), (CX, CY+12), 1)

    # ---- HUD ----
    hud = [
        (f"yaw:     {math.degrees(yaw):.1f}°",       (142, 184, 232)),
        (f"pitch:   {math.degrees(pitch):.1f}°",     (255, 204,  68)),
        (f"forward: ({forward.x:.2f}, {forward.y:.2f}, {forward.z:.2f})", (136, 255, 136)),
        (f"right:   ({right.x:.2f}, {right.y:.2f}, {right.z:.2f})",       (255, 136, 136)),
        (f"up:      ({up.x:.2f}, {up.y:.2f}, {up.z:.2f})",                (204, 136, 255)),
        ("Arrow keys to look around",                 ( 64,  80, 100)),
    ]
    pygame.draw.rect(screen, (4, 8, 18), (12, 12, 280, len(hud) * 16 + 12))
    for i, (text, color) in enumerate(hud):
        lbl = font.render(text, True, color)
        screen.blit(lbl, (20, 18 + i * 16))

    pygame.display.flip()


pygame.quit()
sys.exit()
