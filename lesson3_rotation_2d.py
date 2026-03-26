"""
Lesson 3: Rotate points with a 2D matrix.
Apply a rotation transform to every vertex of a triangle.
"""

import math
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 3 - 2D Rotation Matrix")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

center_x, center_y = WIDTH // 2, HEIGHT // 2
angle = 0.0

triangle = [
    (-90, -60),
    (90, -60),
    (0, 110),
]


def rotate_2d(x, y, theta):
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return x * cos_t - y * sin_t, x * sin_t + y * cos_t


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    pygame.draw.line(screen, (221, 221, 221), (0, center_y), (WIDTH, center_y), 1)
    pygame.draw.line(screen, (221, 221, 221), (center_x, 0), (center_x, HEIGHT), 1)

    screen_points = []
    for x, y in triangle:
        rx, ry = rotate_2d(x, y, angle)
        sx = center_x + rx
        sy = center_y + ry
        screen_points.append((sx, sy))

    pygame.draw.polygon(screen, (65, 105, 225), screen_points, 3)
    label = font.render(f"angle = {angle:.2f} radians", True, (0, 0, 0))
    screen.blit(label, (16, 14))

    angle += 0.03
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
