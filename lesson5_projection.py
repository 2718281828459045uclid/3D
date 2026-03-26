"""
Lesson 5: Perspective projection.
Convert each 3D point (x, y, z) into a 2D screen point (sx, sy).
"""

import pygame

WIDTH, HEIGHT = 800, 600
FOCAL_LENGTH = 260
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 5 - Perspective Projection")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

points_3d = [
    (-1, -1, 3),
    (1, -1, 3),
    (1, 1, 3),
    (-1, 1, 3),
    (-1, -1, 6),
    (1, -1, 6),
    (1, 1, 6),
    (-1, 1, 6),
]
edges = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
]


def project(point):
    x, y, z = point
    if z <= 0.1:
        return None
    sx = WIDTH // 2 + (x * FOCAL_LENGTH) / z
    sy = HEIGHT // 2 - (y * FOCAL_LENGTH) / z
    return int(sx), int(sy)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    projected_points = []
    for point in points_3d:
        projected = project(point)
        projected_points.append(projected)
        if projected is None:
            continue
        x, y = projected
        pygame.draw.circle(screen, (65, 105, 225), (x, y), 4)
        label = font.render(f"z={point[2]}", True, (90, 90, 90))
        screen.blit(label, (x + 10, y - 18))

    for start_index, end_index in edges:
        start = projected_points[start_index]
        end = projected_points[end_index]
        if start is not None and end is not None:
            pygame.draw.line(screen, (120, 120, 120), start, end, 2)

    note1 = font.render("Larger z means farther away,", True, (90, 90, 90))
    note2 = font.render("meaning smaller and closer to the center on screen.", True, (90, 90, 90))

    screen.blit(note1, (90, 16))
    screen.blit(note2, (90, 32))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
