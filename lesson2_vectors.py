"""
Lesson 2: Vectors as arrows.
Use vectors for direction and size, then measure vector length.
"""

import math
import pygame

# First, set up the window size and frame rate.
WIDTH, HEIGHT = 800, 600
FPS = 60

# Then, start pygame and create the app window.
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 2 - Vectors")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

# We use the center of the screen as the origin for all vectors.
origin = (WIDTH // 2, HEIGHT // 2)

# Each tuple is one vector (vx, vy): x movement and y movement.
vectors = [
    (140, -40),
    (-90, -120),
    (70, 140),
]

# We give each vector a different color so they are easy to tell apart.
colors = ["royalblue", "crimson", "seagreen"]


def draw_arrow(start, end, color):
    # First, draw the long line part of the arrow.
    pygame.draw.line(screen, color, start, end, 3)

    # Next, compute arrow direction so we can build the arrowhead.
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)

    # Then, create two side points for a little triangle tip.
    head_len = 14
    left = (
        end[0] - head_len * math.cos(angle - math.radians(25)),
        end[1] - head_len * math.sin(angle - math.radians(25)),
    )
    right = (
        end[0] - head_len * math.cos(angle + math.radians(25)),
        end[1] - head_len * math.sin(angle + math.radians(25)),
    )

    # Finally, draw the arrowhead triangle.
    pygame.draw.polygon(screen, color, [end, left, right])


# Main loop for continuous drawing.
running = True
while running:
    # Handle close-window events.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear old frame.
    screen.fill((255, 255, 255))

    # Draw light axis guides and the origin label.
    pygame.draw.line(screen, (221, 221, 221), (0, origin[1]), (WIDTH, origin[1]), 1)
    pygame.draw.line(screen, (221, 221, 221), (origin[0], 0), (origin[0], HEIGHT), 1)
    origin_label = font.render("origin", True, (90, 90, 90))
    screen.blit(origin_label, (origin[0] + 8, origin[1] + 8))

    # Loop through vectors by index so each vector gets its matching color.
    for i in range(len(vectors)):
        # Yhis one line pulls x and y from one pair.
        vx, vy = vectors[i]
        color = colors[i]

        # Start at origin, then move by (vx, vy) to get end point.
        ox, oy = origin
        ex = ox + vx
        ey = oy + vy

        # Vector length is sqrt(vx^2 + vy^2).  (Pythagoras!)
        length = math.sqrt(vx * vx + vy * vy)

        # Draw the arrow and write its numbers.
        draw_arrow((ox, oy), (ex, ey), color)
        vector_label = font.render(f"v=({vx}, {vy}), |v|={length:.1f}", True, color)
        screen.blit(vector_label, (ex + 10, ey - 10))

    # Push new frame to screen and keep frame rate stable.
    pygame.display.flip()
    clock.tick(FPS)

# Close app
pygame.quit()
