"""
Lesson 5: Perspective projection.
Convert each 3D point (x, y, z) into a 2D screen point (sx, sy).
"""

import pygame

# First, choose window and camera-like values.
WIDTH, HEIGHT = 800, 600
FOCAL_LENGTH = 260
FPS = 60

# Then start pygame and set up text.
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 5 - Perspective Projection")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

# These are two squares at different depths (z=3 and z=6).
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

# These edges connect points into a box wireframe.
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
    # Read x, y, z from the 3D point.
    x, y, z = point

    # If z is too small or behind us, we skip that point.
    if z <= 0.1:
        return None

    # Perspective formula: divide x and y by z.
    sx = WIDTH // 2 + (x * FOCAL_LENGTH) / z
    sy = HEIGHT // 2 - (y * FOCAL_LENGTH) / z
    return int(sx), int(sy)


# Main app loop.
running = True
while running:
    # Handle close window events.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear frame.
    screen.fill((255, 255, 255))

    # Project each 3D point and draw it.
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

    # Draw lines between projected points so the shape is easier to read.
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
