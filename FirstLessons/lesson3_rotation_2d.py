"""
Lesson 3: Rotate points with a 2D matrix.
Apply a rotation transform to every vertex of a triangle.
"""

import math
import pygame

# First, set up window size and target frame rate.
WIDTH, HEIGHT = 800, 600
FPS = 60

# Then, start pygame and create the display.
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 3 - 2D Rotation Matrix")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

# We rotate around the center of the screen.
center_x, center_y = WIDTH // 2, HEIGHT // 2
angle = 0.0

# This triangle is defined around (0, 0), not screen coordinates.
triangle = [
    (-90, -60),
    (90, -60),
    (0, 110),
]


def rotate_2d(x, y, theta):
    # This is the 2D rotation matrix:
    # x' = x*cos(theta) - y*sin(theta)
    # y' = x*sin(theta) + y*cos(theta)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return x * cos_t - y * sin_t, x * sin_t + y * cos_t


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear old drawing by filling screen
    screen.fill((255, 255, 255))

    # Draw axis lines through screen center.
    pygame.draw.line(screen, (221, 221, 221), (0, center_y), (WIDTH, center_y), 1)
    pygame.draw.line(screen, (221, 221, 221), (center_x, 0), (center_x, HEIGHT), 1)

    # Rotate each triangle point, then move it into screen space.
    screen_points = []
    for x, y in triangle:
        rx, ry = rotate_2d(x, y, angle)
        sx = center_x + rx
        sy = center_y + ry
        screen_points.append((sx, sy))

    # Draw the rotated triangle and show the current angle.
    pygame.draw.polygon(screen, (65, 105, 225), screen_points, 3)
    label = font.render(f"angle = {angle:.2f} radians", True, (0, 0, 0))
    screen.blit(label, (16, 14))

    # Increase angle a little bit each frame to animate rotation.
    angle += 0.03
    angle = angle % (2 * math.pi)

    # Show frame and wait to match FPS.
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
