"""
============================================================
LESSON 2: VECTORS — THE LANGUAGE OF MOVEMENT
============================================================
Run:  python lesson_02_vectors.py

Goals:
  - Build the Vec3 class (used unchanged through Lesson 6)
  - Understand add, sub, scale, length, normalize, dot, cross
  - Use WASD to apply velocity to a ship (2D; z = 0 for now)
  - Visualize the velocity vector as an arrow
  - Show the dot product in the HUD
============================================================
"""

import pygame
import sys
import random
import math


# ============================================================
# VEC3 CLASS
# ============================================================

class Vec3:
    """
    A 3D vector: three numbers (x, y, z) representing magnitude + direction.
    Can represent position, velocity, direction, or force.
    We use z = 0 in this lesson (still 2D), but the class is fully 3D.
    """

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def add(self, v):
        """Add two vectors component-by-component.
        Use: position + velocity*dt  → new position"""
        return Vec3(self.x + v.x, self.y + v.y, self.z + v.z)

    def sub(self, v):
        """Subtract v from self.  Result points FROM v TO self.
        Use: planet.pos - ship.pos  → direction from ship to planet"""
        return Vec3(self.x - v.x, self.y - v.y, self.z - v.z)

    def scale(self, s):
        """Multiply every component by scalar s.
        Use: velocity * dt  → displacement this frame"""
        return Vec3(self.x * s, self.y * s, self.z * s)

    def length(self):
        """Magnitude: sqrt(x²+y²+z²).  Represents speed if velocity, distance if displacement."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def length_sq(self):
        """Squared length — avoids sqrt.  Use for comparisons only."""
        return self.x**2 + self.y**2 + self.z**2

    def normalize(self):
        """Return a unit vector (length = 1) with the same direction.
        Strips magnitude, leaving pure direction.
        Example: Vec3(3,4,0).normalize() → Vec3(0.6, 0.8, 0) with length 1."""
        l = self.length()
        if l == 0:
            return Vec3(0, 0, 0)     # guard: can't normalize a zero vector
        return self.scale(1.0 / l)

    def dot(self, v):
        """Dot product: a.x*b.x + a.y*b.y + a.z*b.z.

        When both are unit vectors, result = cos(angle between them):
          dot =  1  → same direction
          dot =  0  → perpendicular
          dot = -1  → opposite

        Uses: 'is the target ahead of me?', lighting, camera transform."""
        return self.x * v.x + self.y * v.y + self.z * v.z

    def cross(self, v):
        """Cross product: returns a vector perpendicular to both self and v.
        Direction follows the right-hand rule.
        Uses: finding 'up' from 'forward' and 'right', surface normals."""
        return Vec3(
            self.y * v.z - self.z * v.y,   # x
            self.z * v.x - self.x * v.z,   # y
            self.x * v.y - self.y * v.x    # z
        )

    def __repr__(self):
        return f"({self.x:.1f}, {self.y:.1f}, {self.z:.1f})"

    # Python operator overloads so we can write v1 + v2 instead of v1.add(v2)
    def __add__(self, v): return self.add(v)
    def __sub__(self, v): return self.sub(v)
    def __mul__(self, s): return self.scale(s)
    def __rmul__(self, s): return self.scale(s)  # allows: 2 * vec


# ============================================================
# PYGAME SETUP
# ============================================================

pygame.init()
WIDTH, HEIGHT = 700, 460
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 2 — Vectors")
clock = pygame.time.Clock()
font  = pygame.font.SysFont("Courier New", 12)

# World center in screen pixels.
# Our world has (0,0) at the center; screen has (0,0) top-left.
CX, CY = WIDTH // 2, HEIGHT // 2


# ============================================================
# HELPERS
# ============================================================

def world_to_screen(wx, wy):
    """Convert world (x, y) to screen pixel coordinates.
    World +y is UP; screen +y is DOWN, so we negate wy."""
    return int(CX + wx), int(CY - wy)


def draw_text(surface, text, x, y, color=(180, 200, 255)):
    surf = font.render(text, True, color)
    surface.blit(surf, (x, y))


def draw_arrow(surface, x1, y1, x2, y2, color, label=None):
    """Draw an arrow from (x1,y1) to (x2,y2) with an optional label."""
    dx, dy = x2 - x1, y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    if length < 3:
        return
    pygame.draw.line(surface, color, (int(x1), int(y1)), (int(x2), int(y2)), 2)
    # Arrowhead
    angle   = math.atan2(dy, dx)
    head    = 10
    tip_x, tip_y = int(x2), int(y2)
    p1 = (tip_x - int(head * math.cos(angle - 0.4)), tip_y - int(head * math.sin(angle - 0.4)))
    p2 = (tip_x - int(head * math.cos(angle + 0.4)), tip_y - int(head * math.sin(angle + 0.4)))
    pygame.draw.polygon(surface, color, [(tip_x, tip_y), p1, p2])
    if label:
        lbl = font.render(label, True, color)
        surface.blit(lbl, (int(x2) + 5, int(y2) - 8))


# ============================================================
# WORLD SETUP
# ============================================================

stars = [
    {"x": random.uniform(0, WIDTH), "y": random.uniform(0, HEIGHT),
     "r": random.uniform(0.5, 1.5), "b": random.randint(100, 220)}
    for _ in range(160)
]

# Planets as Vec3 positions (z=0 in 2D world)
planets = [
    {"pos": Vec3(-220,  90, 0), "radius": 42, "color": (58,  111, 204), "name": "Hydra"},
    {"pos": Vec3( 190, -95, 0), "radius": 28, "color": (204,  85,  51), "name": "Ignis"},
    {"pos": Vec3( 260, 130, 0), "radius": 55, "color": (119,  68,  34), "name": "Magna"},
    {"pos": Vec3(-130,-150, 0), "radius": 20, "color": (68,  119,  85), "name": "Virid"},
]

# Ship state — both as Vec3 (z=0, this is still 2D)
ship_pos = Vec3(0, 0, 0)
ship_vel = Vec3(0, 0, 0)

THRUST = 130   # units/sec added per second while key held


# ============================================================
# MAIN LOOP
# ============================================================

running = True
while running:
    dt = clock.tick(60) / 1000.0

    # ---- Events ----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # ---- Input ----
    keys = pygame.key.get_pressed()   # returns a bool array of every key state

    if keys[pygame.K_w]: ship_vel.y += THRUST * dt   # world-y up = positive
    if keys[pygame.K_s]: ship_vel.y -= THRUST * dt
    if keys[pygame.K_a]: ship_vel.x -= THRUST * dt
    if keys[pygame.K_d]: ship_vel.x += THRUST * dt

    # Space: soft brake — exponential decay toward zero
    if keys[pygame.K_SPACE]:
        ship_vel = ship_vel.scale(0.90)

    # ---- Update ----
    # position += velocity * dt   (Euler integration, same formula as Lesson 1)
    ship_pos = ship_pos + ship_vel * dt

    # Soft world boundary (bounce gently)
    BOUND = 320
    if ship_pos.x >  BOUND: ship_pos.x =  BOUND; ship_vel.x *= -0.5
    if ship_pos.x < -BOUND: ship_pos.x = -BOUND; ship_vel.x *= -0.5
    if ship_pos.y >  BOUND: ship_pos.y =  BOUND; ship_vel.y *= -0.5
    if ship_pos.y < -BOUND: ship_pos.y = -BOUND; ship_vel.y *= -0.5

    # ---- Draw ----
    screen.fill((5, 8, 16))

    # Stars
    for s in stars:
        c = s["b"]
        pygame.draw.circle(screen, (c, c, c), (int(s["x"]), int(s["y"])), max(1, int(s["r"])))

    # Find nearest planet (for the direction visualization)
    nearest = min(planets, key=lambda p: p["pos"].sub(ship_pos).length())

    # Planets
    ship_sx, ship_sy = world_to_screen(ship_pos.x, ship_pos.y)
    for planet in planets:
        px, py = world_to_screen(planet["pos"].x, planet["pos"].y)
        pygame.draw.circle(screen, planet["color"], (px, py), planet["radius"])
        pygame.draw.circle(screen, (255, 255, 255), (px, py), planet["radius"], 1)
        lbl = font.render(planet["name"], True, (190, 210, 255))
        screen.blit(lbl, (px - lbl.get_width()//2, py - planet["radius"] - 16))

    # Direction vector to nearest planet (dashed line)
    np_sx, np_sy = world_to_screen(nearest["pos"].x, nearest["pos"].y)
    for t in range(0, 10):
        frac = t / 10
        tx = int(ship_sx + (np_sx - ship_sx) * frac)
        ty = int(ship_sy + (np_sy - ship_sy) * frac)
        if t % 2 == 0:
            pygame.draw.circle(screen, (80, 100, 160), (tx, ty), 1)

    # Velocity arrow
    VEL_SCALE = 0.14
    draw_arrow(screen,
               ship_sx, ship_sy,
               ship_sx + ship_vel.x * VEL_SCALE,
               ship_sy - ship_vel.y * VEL_SCALE,    # screen y is flipped
               (255, 204, 68), "velocity")

    # Ship glow + core
    glow = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(glow, (80, 180, 255, 50), (20, 20), 18)
    screen.blit(glow, (ship_sx - 20, ship_sy - 20))
    pygame.draw.circle(screen, (112, 216, 255), (ship_sx, ship_sy), 4)

    # ---- HUD ----
    speed = ship_vel.length()
    dot_to_nearest = 0.0
    if speed > 1:
        to_target  = nearest["pos"].sub(ship_pos).normalize()
        vel_dir    = ship_vel.normalize()
        dot_to_nearest = to_target.dot(vel_dir)

    hud_lines = [
        (f"pos:   {ship_pos}",                    (142, 184, 232)),
        (f"vel:   {ship_vel}",                    (255, 204,  68)),
        (f"speed: {speed:.1f} u/s",               (136, 255, 136)),
        (f"dot→nearest: {dot_to_nearest:.2f}",    (255, 136, 136)),
        ("  (1=toward, -1=away)",                  ( 80,  88, 112)),
    ]
    box_h = len(hud_lines) * 16 + 12
    pygame.draw.rect(screen, (4, 8, 18), (12, 12, 260, box_h))
    for i, (text, color) in enumerate(hud_lines):
        draw_text(screen, text, 20, 18 + i * 16, color)

    pygame.display.flip()


pygame.quit()
sys.exit()
