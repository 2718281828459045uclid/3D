"""
============================================================
LESSON 1: PYGAME AND COORDINATES
============================================================
Run:  python lesson_01_pygame.py
Requires: pip install pygame

Goals:
  - Set up a pygame window (our "canvas")
  - Understand the 2D coordinate system
  - Draw shapes: circles (planets), dots (stars), a ship
  - Run a game loop with delta time
  - Move the ship using constant velocity
============================================================
"""

import pygame   # pip install pygame
import sys
import random
import math


# ============================================================
# PYGAME SETUP
# ============================================================

pygame.init()   # initialize all pygame modules (audio, display, fonts, etc.)

# Create the window / drawing surface.
# pygame.display.set_mode((width, height)) returns a Surface object.
# Think of a Surface as a 2D grid of colored pixels — our canvas.
WIDTH, HEIGHT = 700, 460
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 1 — Canvas and Coordinates")

# Clock controls the frame rate and lets us measure delta time.
clock = pygame.time.Clock()

# Font for drawing text on screen
font_small = pygame.font.SysFont("Courier New", 12)


# ============================================================
# COORDINATE SYSTEM
# ============================================================
# In pygame, (0, 0) is the TOP-LEFT corner of the window.
#   x increases going RIGHT   →
#   y increases going DOWN    ↓
#
# This is the same as HTML canvas (Lesson 1 in JavaScript).
# In 3D (Lesson 3+) world-y will go UPWARD; we'll flip it during projection.


# ============================================================
# STARS
# ============================================================
# We create stars once (not every frame) as a list of dicts.
# Each star is a random point on the screen.
NUM_STARS = 200
stars = []
for _ in range(NUM_STARS):
    stars.append({
        "x":          random.uniform(0, WIDTH),       # anywhere across the window
        "y":          random.uniform(0, HEIGHT),      # anywhere down the window
        "radius":     random.uniform(0.5, 1.8),       # tiny dots
        "brightness": random.uniform(100, 255),       # 0–255 for alpha (pygame style)
    })


# ============================================================
# PLANETS
# ============================================================
# Placed by hand for this lesson.
# Each planet is a dict with a screen position, radius, and color.
# Colors in pygame are (R, G, B) tuples with values 0–255.
planets = [
    {"x": 140, "y": 180, "radius": 44, "color": (58, 111, 204),  "name": "Hydra"},
    {"x": 490, "y": 130, "radius": 28, "color": (204, 85, 51),   "name": "Ignis"},
    {"x": 580, "y": 350, "radius": 62, "color": (119, 68, 34),   "name": "Magna"},
    {"x": 240, "y": 360, "radius": 20, "color": (68, 119, 85),   "name": "Virid"},
    {"x": 620, "y": 220, "radius": 15, "color": (153, 136, 51),  "name": "Lutea"},
]


# ============================================================
# SHIP
# ============================================================
# The ship is a glowing dot.  It has position (x, y) and velocity (vx, vy).
# Velocity is in pixels per second.
ship_x   = 350.0
ship_y   = 230.0
ship_vx  =  55.0   # 55 px/sec to the right
ship_vy  =  20.0   # 20 px/sec downward


# ============================================================
# MAIN GAME LOOP
# ============================================================

running = True

while running:

    # --- DELTA TIME ---
    # clock.tick(60) waits so we don't exceed 60 fps, and returns
    # the number of milliseconds since the last frame.
    # Dividing by 1000 gives dt in seconds (~0.016 at 60 fps).
    dt = clock.tick(60) / 1000.0

    # --- EVENTS ---
    # pygame.event.get() collects all pending events (key presses, window close, etc.)
    # We MUST call this every frame or the window will freeze.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:           # user clicked the X button
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:    # Esc also quits
                running = False

    # --- UPDATE ---
    # Move the ship by velocity × dt.  Same formula as the JavaScript version:
    #   position += velocity * dt
    ship_x += ship_vx * dt
    ship_y += ship_vy * dt

    # Wrap around the edges (toroidal space)
    if ship_x > WIDTH:  ship_x -= WIDTH
    if ship_x < 0:      ship_x += WIDTH
    if ship_y > HEIGHT: ship_y -= HEIGHT
    if ship_y < 0:      ship_y += HEIGHT

    # --- DRAW ---

    # CLEAR: fill the screen with a near-black color.
    # In pygame, colors are (R, G, B) tuples.
    screen.fill((5, 8, 16))

    # Stars
    for star in stars:
        alpha = star["brightness"]
        # pygame.draw.circle(surface, color, center, radius)
        # center must be (int, int); radius must be int
        color = (alpha, alpha, alpha)   # grey: same value for R, G, B
        pygame.draw.circle(
            screen, color,
            (int(star["x"]), int(star["y"])),
            max(1, int(star["radius"]))
        )

    # Planets
    for planet in planets:
        # Draw filled circle (main disk)
        pygame.draw.circle(
            screen, planet["color"],
            (planet["x"], planet["y"]),
            planet["radius"]
        )
        # Draw outline (border) — draw with width > 0 to just draw the edge
        pygame.draw.circle(
            screen, (255, 255, 255),
            (planet["x"], planet["y"]),
            planet["radius"],
            1    # line width = 1 pixel (just the edge, not filled)
        )
        # Planet name above
        label = font_small.render(planet["name"], True, (190, 210, 255))
        label_rect = label.get_rect(center=(planet["x"], planet["y"] - planet["radius"] - 8))
        screen.blit(label, label_rect)  # blit = "copy this surface onto screen"

    # Ship (glow + core)
    sx, sy = int(ship_x), int(ship_y)

    # Glow: a transparent-ish large circle
    # pygame doesn't have built-in alpha per draw call, so we use a Surface with alpha.
    glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (80, 180, 255, 50), (20, 20), 18)
    screen.blit(glow_surf, (sx - 20, sy - 20))

    # Core: bright solid dot
    pygame.draw.circle(screen, (112, 216, 255), (sx, sy), 4)

    # Ship position label
    label = font_small.render(f"ship ({int(ship_x)}, {int(ship_y)})", True, (112, 216, 255))
    screen.blit(label, (sx + 10, sy - 6))

    # Coordinate axis diagram
    draw_axes(screen, font_small, 30, 420)

    # Mouse position
    mx, my = pygame.mouse.get_pos()
    mouse_text = font_small.render(f"mouse: ({mx}, {my})", True, (150, 170, 200))
    screen.blit(mouse_text, (10, 10))

    # --- FLIP ---
    # pygame draws to a hidden back-buffer.
    # display.flip() swaps the back-buffer to the screen (double buffering).
    # This prevents flickering from partial redraws.
    pygame.display.flip()


pygame.quit()
sys.exit()


# ============================================================
# HELPER: draw coordinate axis diagram
# ============================================================
def draw_axes(surface, font, ox, oy):
    """Draw a small X/Y axis diagram at (ox, oy) to illustrate coordinate directions."""
    length = 38

    # X axis → RIGHT (positive x = right)
    pygame.draw.line(surface, (255, 100, 100), (ox, oy), (ox + length, oy), 2)
    lbl = font.render("x+", True, (255, 100, 100))
    surface.blit(lbl, (ox + length + 3, oy - 6))

    # Y axis ↓ DOWN (positive y = down — opposite of math class)
    pygame.draw.line(surface, (100, 255, 136), (ox, oy), (ox, oy + length), 2)
    lbl = font.render("y+", True, (100, 255, 136))
    surface.blit(lbl, (ox - 4, oy + length + 3))

    # Origin dot
    pygame.draw.circle(surface, (255, 255, 255), (ox, oy), 3)

    lbl = font.render("(0,0) top-left", True, (130, 150, 180))
    surface.blit(lbl, (ox + 6, oy - 16))
