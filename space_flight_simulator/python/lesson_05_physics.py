"""
============================================================
LESSON 5: THRUST AND PHYSICS
============================================================
Run:  python lesson_05_physics.py
Controls:  WASD = thrust,  Arrow keys = rotate

Goals:
  - Camera gains a position (Vec3) and velocity (Vec3)
  - WASD apply ACCELERATION (thrust) in camera-local directions
  - Euler integration:  vel += accel * dt,  pos += vel * dt
  - Zero-gravity drift: velocity persists after releasing keys
  - HUD shows velocity magnitude (speed) and position

Key difference from Lesson 2:
  - Lesson 2: keys added directly to velocity (instant speed change)
  - Lesson 5: keys add to ACCELERATION, which gradually changes velocity
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
    def __repr__(self):    return f"({self.x:.0f}, {self.y:.0f}, {self.z:.0f})"


# ============================================================
# PYGAME SETUP
# ============================================================
pygame.init()
WIDTH, HEIGHT = 700, 460
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 5 — Thrust & Physics")
clock = pygame.time.Clock()
font  = pygame.font.SysFont("Courier New", 11)

CX, CY       = WIDTH // 2, HEIGHT // 2
FOCAL_LENGTH = 500
NEAR_CLIP    = 1.0

THRUST_ACCEL = 80    # units/sec² acceleration per thrust axis
TURN_SPEED   = 1.2   # radians/sec


# ============================================================
# CAMERA STATE
# ============================================================
cam_pos   = Vec3(0, 0, 0)   # position in world space
cam_vel   = Vec3(0, 0, 0)   # velocity in world space (units/sec)
cam_yaw   = 0.0
cam_pitch = 0.0


# ============================================================
# CAMERA MATH  (same as Lesson 4)
# ============================================================
def compute_camera_vectors(yaw, pitch):
    cos_p, sin_p = math.cos(pitch), math.sin(pitch)
    cos_y, sin_y = math.cos(yaw),   math.sin(yaw)
    forward = Vec3(cos_p * sin_y,  sin_p,         cos_p * cos_y)
    right   = Vec3(cos_y,          0.0,           -sin_y)
    up      = Vec3(-sin_p * sin_y, cos_p,         -sin_p * cos_y)
    return forward, right, up


def world_to_camera(world_point, cam_position, forward, right, up):
    """
    Transform a world point into camera-local coordinates.
    NEW in Lesson 5: we subtract cam_position so the world
    moves correctly as the camera flies through it.
    """
    rel = world_point.sub(cam_position)    # vector from camera to world point
    return Vec3(
        rel.dot(right),      # how far right (camera-local x)
        rel.dot(up),         # how far up    (camera-local y)
        rel.dot(forward)     # depth         (camera-local z)
    )


def project(cam_point):
    # Points too close/behind the camera are discarded before perspective divide.
    if cam_point.z <= NEAR_CLIP: return None
    sx    =  (cam_point.x / cam_point.z) * FOCAL_LENGTH + CX
    sy    = -(cam_point.y / cam_point.z) * FOCAL_LENGTH + CY
    scale =   FOCAL_LENGTH / cam_point.z
    return sx, sy, scale


# ============================================================
# WORLD
# ============================================================
NUM_STARS = 250
stars = []
for _ in range(NUM_STARS):
    theta = random.uniform(0, math.pi * 2)
    phi   = math.acos(random.uniform(-1, 1))
    stars.append({
        "dir": Vec3(math.sin(phi)*math.cos(theta), math.sin(phi)*math.sin(theta), math.cos(phi)),
        "b": random.randint(100, 220),
        "s": max(1, int(random.uniform(0.5, 1.8))),
    })

PALETTE = [(58,111,204),(204,85,51),(119,68,34),(68,119,85),
           (153,136,51),(153,68,170),(51,102,136),(170,102,51)]
NAMES   = ["Hydra","Ignis","Magna","Virid","Lutea","Ceres","Nebula","Ferro",
           "Glacis","Pyrex","Umbra","Solus","Terra","Argon","Noctis"]
planets = []
for i in range(15):
    planets.append({
        "pos":    Vec3(random.uniform(-1000, 1000), random.uniform(-750, 750), random.uniform(200, 3000)),
        "radius": random.uniform(15, 70),
        "color":  PALETTE[i % len(PALETTE)],
        "name":   NAMES[i % len(NAMES)],
    })


# ============================================================
# MAIN LOOP
# ============================================================
MAX_PITCH = math.pi / 2 - 0.01

running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False

    keys = pygame.key.get_pressed()

    # ---- Rotation ----
    if keys[pygame.K_LEFT]:  cam_yaw   -= TURN_SPEED * dt
    if keys[pygame.K_RIGHT]: cam_yaw   += TURN_SPEED * dt
    if keys[pygame.K_UP]:    cam_pitch += TURN_SPEED * dt
    if keys[pygame.K_DOWN]:  cam_pitch -= TURN_SPEED * dt
    cam_pitch = max(-MAX_PITCH, min(MAX_PITCH, cam_pitch))

    # ---- Thrust ----
    # Compute orientation vectors BEFORE applying thrust,
    # so thrust is in the CURRENT camera direction.
    forward, right, up = compute_camera_vectors(cam_yaw, cam_pitch)

    # Each held key adds acceleration in a camera-local direction.
    #
    #   Newton's 2nd Law: F = m * a
    #   With mass = 1: a = F = THRUST_ACCEL (in units/sec²)
    #
    #   velocity += direction * THRUST_ACCEL * dt
    #
    #   Why * dt?
    #   THRUST_ACCEL is units/sec².  Multiplying by dt (seconds) gives
    #   the velocity CHANGE for this frame (units/sec).
    if keys[pygame.K_w]: cam_vel = cam_vel.add(forward.scale( THRUST_ACCEL * dt))
    if keys[pygame.K_s]: cam_vel = cam_vel.add(forward.scale(-THRUST_ACCEL * dt))
    if keys[pygame.K_a]: cam_vel = cam_vel.add(right.scale(  -THRUST_ACCEL * dt))
    if keys[pygame.K_d]: cam_vel = cam_vel.add(right.scale(   THRUST_ACCEL * dt))

    # ---- Integrate position ----
    # position += velocity * dt
    #
    # This is EULER INTEGRATION — the simplest numerical integration method.
    # In zero gravity there is no decelerating force, so vel stays constant
    # once thrust stops.  That's Newton's 1st law.
    cam_pos = cam_pos.add(cam_vel.scale(dt))

    # ---- Draw ----
    screen.fill((5, 8, 16))

    # Stars (rotate with camera; stars are infinitely far so no position offset)
    for star in stars:
        # Dotting by basis vectors rotates world direction into camera axes.
        cam_dir = Vec3(
            star["dir"].dot(right),
            star["dir"].dot(up),
            star["dir"].dot(forward)
        )
        if cam_dir.z <= 0: continue
        sx = (cam_dir.x / cam_dir.z) * FOCAL_LENGTH + CX
        sy = -(cam_dir.y / cam_dir.z) * FOCAL_LENGTH + CY
        if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
            pygame.draw.circle(screen, (star["b"],) * 3, (int(sx), int(sy)), star["s"])

    # Planets
    projected = []
    for planet in planets:
        cam_pt = world_to_camera(planet["pos"], cam_pos, forward, right, up)
        proj   = project(cam_pt)
        if proj:
            # Depth-first rendering avoids near planets being overdrawn by far ones.
            projected.append((cam_pt.z, planet, proj))
    projected.sort(reverse=True)

    for _, planet, (sx, sy, scale) in projected:
        r = int(planet["radius"] * scale)
        if r < 1: continue
        pygame.draw.circle(screen, planet["color"], (int(sx), int(sy)), r)
        pygame.draw.circle(screen, (255,255,255), (int(sx), int(sy)), r, 1)
        if r > 8:
            lbl = font.render(planet["name"], True, (190, 210, 255))
            screen.blit(lbl, (int(sx) - lbl.get_width()//2, int(sy) - r - 14))

    # Crosshair
    pygame.draw.line(screen, (80,80,100), (CX-12, CY), (CX+12, CY), 1)
    pygame.draw.line(screen, (80,80,100), (CX, CY-12), (CX, CY+12), 1)

    # ---- HUD ----
    speed = cam_vel.length()
    hud = [
        (f"pos:   {cam_pos}",                             (142, 184, 232)),
        (f"vel:   ({cam_vel.x:.1f}, {cam_vel.y:.1f}, {cam_vel.z:.1f})", (255, 204, 68)),
        (f"speed: {speed:.1f} u/s",                       (136, 255, 136)),
        (f"yaw:   {math.degrees(cam_yaw):.1f}°",          (255, 136, 136)),
        (f"pitch: {math.degrees(cam_pitch):.1f}°",        (204, 136, 255)),
        ("WASD=thrust  Arrows=rotate",                    ( 64,  80, 100)),
    ]
    pygame.draw.rect(screen, (4, 8, 18), (12, 12, 290, len(hud) * 16 + 12))
    for i, (text, color) in enumerate(hud):
        lbl = font.render(text, True, color)
        screen.blit(lbl, (20, 18 + i * 16))

    pygame.display.flip()


pygame.quit()
sys.exit()
