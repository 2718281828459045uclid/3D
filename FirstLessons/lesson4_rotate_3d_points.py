"""
Lesson 4: 3D points and axis rotations.
Represent points as (x, y, z) and rotate them around X and Y.
"""

import math
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60
SCALE = 120

# Then open pygame and create text font.
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 4 - Rotate 3D Points")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

# This is a flat square in the XY plane (notice all z values are 0).
points = [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)]
# These pairs tell us which points should have lines between them.
edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)]


def rotate_x(point, theta):
    # Rotate around X: y and z change, x stays the same.
    x, y, z = point
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return x, y * cos_t - z * sin_t, y * sin_t + z * cos_t


def rotate_y(point, theta):
    # Rotate around Y: x and z change, y stays the same.
    x, y, z = point
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return x * cos_t + z * sin_t, y, -x * sin_t + z * cos_t


def to_screen(point):
    # Convert world (x, y, z) into 2D screen coordinates.
    # For this lesson, we ignore z in this conversion on purpose.
    x, y, _ = point
    sx = WIDTH // 2 + int(x * SCALE)
    sy = HEIGHT // 2 - int(y * SCALE)
    return sx, sy


# Start at a small angle so we can already see tilt.
angle = math.radians(30)

# Main draw/update loop.
running = True
while running:
    # Handle close event.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill background each frame.
    screen.fill((245, 245, 245))

    # Draw center guide lines.
    axis_color = (220, 220, 220)
    pygame.draw.line(screen, axis_color, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 1)
    pygame.draw.line(screen, axis_color, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 1)

    # Rotate every point and store the projected screen result.
    projected_points = []
    for point in points:
        rotated = rotate_x(point, angle)
        rotated = rotate_y(rotated, angle)
        sx, sy = to_screen(rotated)
        projected_points.append((sx, sy))

        # Draw point and show its rotated coordinates.
        pygame.draw.circle(screen, (65, 105, 225), (sx, sy), 6)
        x, y, z = rotated
        label = font.render(f"({x:.2f}, {y:.2f}, {z:.2f})", True, (60, 60, 60))
        screen.blit(label, (sx + 10, sy - 8))

    # Connect the points with lines.
    for start_index, end_index in edges:
        start_pos = projected_points[start_index]
        end_pos = projected_points[end_index]
        pygame.draw.line(screen, (110, 110, 110), start_pos, end_pos, 2)

    # The square center stays at (0, 0, 0) as it rotates.
    center = rotate_x((0, 0, 0), angle)
    center = rotate_y(center, angle)

    # This starts as the square's normal direction.
    normal = rotate_x((0, 0, 1), angle)
    normal = rotate_y(normal, angle)

    # Draw a short line in both directions along the normal.
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

    # Draw the normal axis and center point.
    pygame.draw.line(screen, (220, 60, 60), normal_start_2d, normal_end_2d, 3)
    center_2d = to_screen(center)
    pygame.draw.circle(screen, (220, 60, 60), center_2d, 5)

    # Draw title and normal label.
    title = font.render("Flat square with its normal through the center", True, (40, 40, 40))
    screen.blit(title, (16, 16))
    normal_label = font.render("normal axis", True, (220, 60, 60))
    screen.blit(normal_label, (normal_end_2d[0] + 8, normal_end_2d[1] - 8))

    # Increment angle
    angle += 0.01

    # Show frame and keep timing steady.
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
