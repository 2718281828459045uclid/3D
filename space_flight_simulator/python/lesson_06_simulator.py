"""
============================================================
LESSON 6: COMPLETE FLIGHT SIMULATOR
============================================================
Run:  python lesson_06_simulator.py
Controls:
  WASD       — thrust forward / back / left / right
  Arrow keys — pitch and yaw
  Space      — emergency brake (dampens velocity)

This file assembles every concept from Lessons 1–5:
  canvas drawing, Vec3, perspective projection,
  camera orientation, and Newtonian physics.

Additions over Lesson 5 (cosmetic / quality-of-life only):
  - More planets spread over a larger world
  - Planet glow halos
  - Speed color bar in HUD
  - Nearest planet name + distance
  - Brake flash overlay
  - Control reminder
============================================================
"""

import pygame
import sys
import random
import math


# ============================================================
# VEC3  (unchanged from Lessons 2–5)
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
    def __repr__(self):
        return f"({self.x:.0f}, {self.y:.0f}, {self.z:.0f})"


# ============================================================
# PYGAME SETUP
# ============================================================
pygame.init()
WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 6 — Space Flight Simulator")
clock = pygame.time.Clock()
font  = pygame.font.SysFont("Courier New", 11)
font_lg = pygame.font.SysFont("Courier New", 14)

CX, CY       = WIDTH // 2, HEIGHT // 2
FOCAL_LENGTH = 500
NEAR_CLIP    = 5.0    # raised from 2 — prevents extreme scale values when very close to a planet

THRUST_ACCEL = 90     # units/sec²
TURN_SPEED   = 1.2    # radians/sec


# ============================================================
# CAMERA
# ============================================================
cam_pos   = Vec3(0, 0, 0)
cam_vel   = Vec3(0, 0, 0)
cam_yaw   = 0.0
cam_pitch = 0.0
MAX_PITCH = math.pi / 2 - 0.01

brake_flash = 0.0    # 0–1, decays each frame (visual only)


# ============================================================
# CAMERA MATH
# ============================================================
# Given the camera's current yaw and pitch, compute its forward, right, and up vectors.
# These vectors represent the camera's orientation in 3D space:
#   - forward: the direction the camera is looking
#   - right:   the direction to the camera's right (used for strafing, x axis)
#   - up:      the 'upward' direction from the camera's point of view (y axis)
# This uses spherical coordinates math.
def compute_camera_vectors(yaw, pitch):
    # Compute cos/sin for yaw and pitch for later use
    cos_p, sin_p = math.cos(pitch), math.sin(pitch)
    cos_y, sin_y = math.cos(yaw),   math.sin(yaw)

    # Forward vector (the direction the camera faces)
    # X: horizontal movement (depends on yaw and pitch)
    # Y: vertical movement (depends only on pitch)
    # Z: forward/back movement (depends on yaw and pitch)
    forward = Vec3(cos_p * sin_y,  sin_p,         cos_p * cos_y)

    # Right vector (perpendicular to forward, on the ground plane)
    # X: right, horizontal (depends only on yaw)
    # Z: right, horizontal (depends only on yaw)
    right   = Vec3(cos_y,          0.0,           -sin_y)

    # Up vector (perpendicular to both forward and right, uses right-hand rule)
    # Points 'up' from the camera's perspective
    up      = Vec3(-sin_p * sin_y, cos_p,         -sin_p * cos_y)

    # Return three orthogonal direction vectors from the camera's perspective
    return forward, right, up


def world_to_camera(world_point, cam_position, forward, right, up):
    """
    Convert a point from world coordinates into camera-local coordinates.

    The camera basis vectors (`right`, `up`, `forward`) form the camera's local
    axes. By subtracting camera position first, then dotting against those axes,
    we express the point as:
      x = how far right of camera
      y = how far above camera
      z = how far in front of camera
    """
    # Shift point into a frame centered at camera position.
    rel = world_point.sub(cam_position)
    # Project onto camera basis to get camera-space coordinates.
    return Vec3(rel.dot(right), rel.dot(up), rel.dot(forward))


def project(cam_point):
    """
    Projects a 3D point from camera space onto the 2D screen using perspective projection.

    Arguments:
        cam_point (Vec3): The 3D point in camera-relative coordinates.

    Returns:
        (sx, sy, scale): Tuple containing:
            - sx: x-coordinate on the screen.
            - sy: y-coordinate on the screen.
            - scale: scale factor for sizing objects at this depth.
        Returns None if the point is behind the camera's near clipping plane.

    Explanation:
      - If the point is closer than NEAR_CLIP (i.e., behind or too close to the camera), it won't be displayed.
      - sx and sy are calculated by projecting the 3D coordinates onto the 2D screen using focal length and the screen's center (CX, CY).
      - The y projection is flipped (negative sign) to match screen coordinates.
      - scale gives a size scaling factor based on depth so objects farther away appear smaller.
    """
    if cam_point.z <= NEAR_CLIP:
        return None
    sx    =  (cam_point.x / cam_point.z) * FOCAL_LENGTH + CX
    sy    = -(cam_point.y / cam_point.z) * FOCAL_LENGTH + CY
    scale =   FOCAL_LENGTH / cam_point.z
    return sx, sy, scale


# ============================================================
# WORLD GENERATION
# ============================================================

# Stars
NUM_STARS = 300
stars = []
for _ in range(NUM_STARS):
    # Uniformly sample a direction on a unit sphere:
    # - theta: azimuth around vertical axis
    # - phi: inclination from top pole
    theta = random.uniform(0, math.pi * 2)
    phi   = math.acos(random.uniform(-1, 1))
    stars.append({
        # Direction only; stars are rendered as infinitely far points.
        "dir": Vec3(math.sin(phi)*math.cos(theta), math.sin(phi)*math.sin(theta), math.cos(phi)),
        # Random brightness and size create depth variation.
        "b":   random.randint(100, 220),
        "s":   max(1, int(random.uniform(0.5, 1.8))),
    })

# Planets — spread in a large sphere around the starting position
PALETTE = [
    ((58,  111, 204), (30,  60, 150, 80)),   # blue
    ((204,  85,  51), (160, 50,  20, 80)),   # orange-red
    ((119,  68,  34), (100, 55,  20, 70)),   # brown
    (( 68, 119,  85), ( 40, 100, 55, 70)),   # green
    ((153, 136,  51), (140, 120, 20, 70)),   # gold
    ((153,  68, 170), (120, 40, 150, 70)),   # purple
    (( 51, 102, 136), ( 30,  80, 130, 70)),  # teal
    ((170, 102,  51), (160,  90,  30, 70)),  # amber
]
NAMES = ["Hydra","Ignis","Magna","Virid","Lutea","Ceres","Nebula","Ferro",
         "Glacis","Pyrex","Umbra","Solus","Terra","Argon","Noctis",
         "Oriox","Kaspa","Venti","Zura","Pelox"]

planets = []
for i in range(20):
    # Cycle through color palette and names so each planet has identity.
    base_col, glow_col = PALETTE[i % len(PALETTE)]
    theta = random.uniform(0, math.pi * 2)
    phi   = math.acos(random.uniform(-1, 1))
    # Planet distance from origin; broad range creates near/far objects.
    dist  = random.uniform(600, 4100)
    planets.append({
        "pos": Vec3(
            # Compress Y axis slightly so world distribution feels flatter.
            math.sin(phi) * math.cos(theta) * dist,
            math.sin(phi) * math.sin(theta) * dist * 0.6,
            # Offset forward so player starts facing into populated space.
            math.cos(phi) * dist + 800
        ),
        "radius":    random.uniform(20, 90),
        "base_col":  base_col,
        "glow_col":  glow_col,
        "name":      NAMES[i % len(NAMES)],
    })


# ============================================================
# HELPER: draw a glowing circle (planet body + halo)
# ============================================================
def draw_planet(sx, sy, r, base_col, glow_col):
    """Draw a planet as a filled circle with a soft glow halo."""
    sx, sy, r = int(sx), int(sy), max(1, int(r))

    # Cap r so we never allocate a surface larger than the window.
    # Without this cap, a planet at depth just above NEAR_CLIP produces
    # r in the tens-of-thousands, and pygame.Surface((huge, huge)) crashes.
    r = min(r, HEIGHT)

    # Glow halo (larger, transparent Surface so alpha works)
    if r > 3:
        glow_r   = min(int(r * 1.8), HEIGHT)   # also capped for safety
        glow_dia = glow_r * 2
        glow_surf = pygame.Surface((glow_dia, glow_dia), pygame.SRCALPHA)
        # Draw concentric circles fading out — approximates a radial gradient
        for step in range(6, 0, -1):
            alpha = int(glow_col[3] * step / 6)
            rad   = int(glow_r * step / 6)
            color = (glow_col[0], glow_col[1], glow_col[2], alpha)
            pygame.draw.circle(glow_surf, color, (glow_r, glow_r), rad)
        screen.blit(glow_surf, (sx - glow_r, sy - glow_r))

    # Planet disk
    pygame.draw.circle(screen, base_col, (sx, sy), r)

    # Subtle highlight on upper-left (fake lighting)
    if r > 5:
        hi_r    = min(r, HEIGHT // 2)   # capped for safety
        hi_surf = pygame.Surface((hi_r * 2, hi_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(hi_surf, (255, 255, 255, 35), (hi_r // 2, hi_r // 2), hi_r)
        screen.blit(hi_surf, (sx - hi_r, sy - hi_r))


# ============================================================
# MAIN LOOP
# ============================================================
running = True
while running:
    # Frame delta time in seconds keeps physics frame-rate independent.
    dt = clock.tick(60) / 1000.0

    # Event queue handles app close and immediate escape exit.
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False

    # Snapshot keyboard state for continuous controls.
    keys = pygame.key.get_pressed()

    # ---- Rotation ----
    if keys[pygame.K_LEFT]:  cam_yaw   -= TURN_SPEED * dt
    if keys[pygame.K_RIGHT]: cam_yaw   += TURN_SPEED * dt
    if keys[pygame.K_UP]:    cam_pitch += TURN_SPEED * dt
    if keys[pygame.K_DOWN]:  cam_pitch -= TURN_SPEED * dt
    cam_pitch = max(-MAX_PITCH, min(MAX_PITCH, cam_pitch))

    # Recompute camera basis vectors after any rotation this frame.
    forward, right, up = compute_camera_vectors(cam_yaw, cam_pitch)

    # ---- Thrust ----
    if keys[pygame.K_w]: cam_vel = cam_vel.add(forward.scale( THRUST_ACCEL * dt))
    if keys[pygame.K_s]: cam_vel = cam_vel.add(forward.scale(-THRUST_ACCEL * dt))
    if keys[pygame.K_a]: cam_vel = cam_vel.add(right.scale(  -THRUST_ACCEL * dt))
    if keys[pygame.K_d]: cam_vel = cam_vel.add(right.scale(   THRUST_ACCEL * dt))

    # ---- Brake ----
    if keys[pygame.K_SPACE]:
        cam_vel     = cam_vel.scale(max(0.0, 1.0 - dt * 4))
        brake_flash = 1.0
    else:
        brake_flash *= 0.85

    # ---- Integrate ----
    # Basic Euler integration: new position = old position + velocity * dt.
    cam_pos = cam_pos.add(cam_vel.scale(dt))

    # ---- Draw ----
    screen.fill((5, 8, 16))

    # Stars
    for star in stars:
        # Rotate static star direction into camera view space via dot products.
        d = Vec3(star["dir"].dot(right), star["dir"].dot(up), star["dir"].dot(forward))
        # Skip stars behind camera.
        if d.z <= 0: continue
        # Perspective divide for screen projection.
        sx = (d.x / d.z) * FOCAL_LENGTH + CX
        sy = -(d.y / d.z) * FOCAL_LENGTH + CY
        if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
            c = star["b"]
            pygame.draw.circle(screen, (c, c, c), (int(sx), int(sy)), star["s"])

    # Nearest planet
    nearest, nearest_dist = None, float("inf")
    for p in planets:
        # True Euclidean distance in world space to current camera position.
        d = p["pos"].sub(cam_pos).length()
        if d < nearest_dist:
            nearest_dist, nearest = d, p

    # Project and sort planets
    projected = []
    for planet in planets:
        # Transform each planet center into camera coordinates.
        cam_pt = world_to_camera(planet["pos"], cam_pos, forward, right, up)
        # Convert to 2D screen position + depth scale (or None if clipped).
        proj   = project(cam_pt)
        if proj:
            # Keep depth so we can draw far-to-near for painter's algorithm.
            projected.append((cam_pt.z, planet, proj))
    projected.sort(reverse=True)    # farthest first

    for _, planet, (sx, sy, scale) in projected:
        # Radius shrinks with distance due to perspective.
        r = planet["radius"] * scale
        # Ignore subpixel planets to save draw calls.
        if r < 0.4: continue
        draw_planet(sx, sy, r, planet["base_col"], planet["glow_col"])
        # Label only when planet is visually large enough to read.
        if r > 12:
            lbl = font.render(planet["name"], True, (190, 210, 255))
            screen.blit(lbl, (int(sx) - lbl.get_width()//2, int(sy) - int(r) - 14))

    # Crosshair (split, gap in the middle)
    pygame.draw.line(screen, (100, 100, 120), (CX-14, CY), (CX-4, CY), 1)
    pygame.draw.line(screen, (100, 100, 120), (CX+4,  CY), (CX+14, CY), 1)
    pygame.draw.line(screen, (100, 100, 120), (CX, CY-14), (CX, CY-4), 1)
    pygame.draw.line(screen, (100, 100, 120), (CX, CY+4),  (CX, CY+14), 1)

    # Brake flash overlay
    if brake_flash > 0.01:
        # Full-screen transparent overlay that fades out exponentially.
        flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash_surf.fill((255, 80, 0, int(brake_flash * 35)))
        screen.blit(flash_surf, (0, 0))
        # Optional center text at stronger flash levels.
        if brake_flash > 0.3:
            lbl = font_lg.render("BRAKING", True, (255, 80, 0))
            screen.blit(lbl, (CX - lbl.get_width()//2, CY + 28))

    # ---- HUD ----
    speed    = cam_vel.length()
    # Used for HUD speed gauge normalization.
    MAX_SPEED = 500

    # Left panel — ship state
    left_hud = [
        (f"pos:   {cam_pos}",                  (142, 184, 232)),
        (f"speed: {speed:.1f} u/s",            (136, 255, 136)),
        (f"yaw:   {math.degrees(cam_yaw):.0f}°",   (170, 170, 200)),
        (f"pitch: {math.degrees(cam_pitch):.0f}°", (170, 170, 200)),
    ]
    pygame.draw.rect(screen, (4, 8, 18), (12, 12, 240, len(left_hud) * 16 + 12))
    for i, (text, color) in enumerate(left_hud):
        lbl = font.render(text, True, color)
        screen.blit(lbl, (20, 18 + i * 16))

    # Speed bar
    bar_y = 12 + len(left_hud) * 16 + 18
    pygame.draw.rect(screen, (4, 8, 18), (12, bar_y, 240, 22))
    pygame.draw.rect(screen, (20, 40, 70), (20, bar_y + 6, 224, 8))
    # Clamp fill to [0, 1] of bar width.
    fill_w = int(min(speed / MAX_SPEED, 1.0) * 224)
    # Color transitions from green (slow) to red (fast).
    t      = min(speed / MAX_SPEED, 1.0)
    r_col  = int(min(t * 2, 1) * 255)
    g_col  = int(min((1 - t) * 2, 1) * 255)
    pygame.draw.rect(screen, (r_col, g_col, 40), (20, bar_y + 6, fill_w, 8))
    lbl = font.render("speed", True, (50, 70, 100))
    screen.blit(lbl, (20, bar_y + 14 + 4))

    # Right panel — nearest planet
    if nearest:
        # Switch units for readability at larger distances.
        dist_str = (f"{int(nearest_dist)} u" if nearest_dist < 10000
                    else f"{nearest_dist/1000:.1f} ku")
        right_hud = [
            ("NEAREST PLANET", (80, 130, 180)),
            (nearest["name"],  (220, 230, 255)),
            (dist_str,         (255, 204,  68)),
        ]
        rx = WIDTH - 12 - 180
        pygame.draw.rect(screen, (4, 8, 18), (rx, 12, 180, len(right_hud) * 16 + 12))
        for i, (text, color) in enumerate(right_hud):
            lbl = font.render(text, True, color)
            screen.blit(lbl, (rx + 90 - lbl.get_width()//2, 18 + i * 16))

    # Controls reminder (bottom-left)
    rem = ["WASD — thrust", "Arrows — rotate", "Space — brake"]
    ry  = HEIGHT - 12 - len(rem) * 16 - 4
    pygame.draw.rect(screen, (4, 8, 18), (12, ry, 160, len(rem) * 16 + 8))
    for i, text in enumerate(rem):
        lbl = font.render(text, True, (55, 75, 100))
        screen.blit(lbl, (20, ry + 6 + i * 16))

    # Push final composed frame to display.
    pygame.display.flip()


# Clean shutdown for pygame and Python process.
pygame.quit()
sys.exit()
