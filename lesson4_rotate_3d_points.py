"""
Lesson 4: 3D points and axis rotations.
Represent points as (x, y, z) and rotate them around X and Y.
"""

import math
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60
SCALE = 120

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 4 - Rotate 3D Points")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

points = [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)]
edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)]


def rotate_x(point, theta):
    x, y, z = point
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return x, y * cos_t - z * sin_t, y * sin_t + z * cos_t


def rotate_y(point, theta):
    x, y, z = point
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return x * cos_t + z * sin_t, y, -x * sin_t + z * cos_t


def to_screen(point):
    x, y, _ = point
    sx = WIDTH // 2 + int(x * SCALE)
    sy = HEIGHT // 2 - int(y * SCALE)
    return sx, sy


angle = math.radians(30)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((245, 245, 245))

    axis_color = (220, 220, 220)
    pygame.draw.line(screen, axis_color, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 1)
    pygame.draw.line(screen, axis_color, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 1)

    projected_points = []
    for point in points:
        rotated = rotate_x(point, angle)
        rotated = rotate_y(rotated, angle)
        sx, sy = to_screen(rotated)
        projected_points.append((sx, sy))

        pygame.draw.circle(screen, (65, 105, 225), (sx, sy), 6)
        x, y, z = rotated
        label = font.render(f"({x:.2f}, {y:.2f}, {z:.2f})", True, (60, 60, 60))
        screen.blit(label, (sx + 10, sy - 8))

    for start_index, end_index in edges:
        start_pos = projected_points[start_index]
        end_pos = projected_points[end_index]
        pygame.draw.line(screen, (110, 110, 110), start_pos, end_pos, 2)

    # The square's center is (0,0,0), so rotating keeps it at the origin.
    center = rotate_x((0, 0, 0), angle)
    center = rotate_y(center, angle)

    # The square starts flat in the XY plane, so (0,0,1) is its normal.
    normal = rotate_x((0, 0, 1), angle)
    normal = rotate_y(normal, angle)

    normal_length = 1.6
    normal_start = (
        center[0] - normal[0] * normal_length,
        center[1] - normal[1] * normal_length,
        center[2] - normal[2] * normal_length,
    )
    normal_end = (
        center[0] + normal[0] * normal_length,
        center[1] + normal[1] * normal_length,
        center[2] + normal[2] * normal_length,
    )
    normal_start_2d = to_screen(normal_start)
    normal_end_2d = to_screen(normal_end)
    pygame.draw.line(screen, (220, 60, 60), normal_start_2d, normal_end_2d, 3)
    center_2d = to_screen(center)
    pygame.draw.circle(screen, (220, 60, 60), center_2d, 5)

    title = font.render("Flat square with its normal through the center", True, (40, 40, 40))
    screen.blit(title, (16, 16))
    normal_label = font.render("normal axis", True, (220, 60, 60))
    screen.blit(normal_label, (normal_end_2d[0] + 8, normal_end_2d[1] - 8))

    angle += 0.01
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
