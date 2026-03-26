"""
Lesson 7: Draw lines by plotting pixels yourself.
Build a line function that places one pixel at a time (no pygame.draw.line).
"""

import pygame


WIDTH, HEIGHT = 800, 600
FPS = 60


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 7 - Line From Pixels")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)


def put_pixel(x, y, color):
    # This draws exactly one pixel.
    # We also check bounds so we do not try drawing off-screen.
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        screen.set_at((x, y), color)


def draw_line_pixels(x0, y0, x1, y1, color):

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    # sx and sy are the step direction for x and y.
    # If target is to the right, sx = 1. If to the left, sx = -1.
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    err = dx - dy

    while True:
        put_pixel(x0, y0, color)

        # Stop when we reach the end point.
        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * err

        # Move in x when the error says we are too far from ideal line.
        if e2 > -dy:
            err -= dy
            x0 += sx

        # Move in y when the error says we are too far from ideal line.
        if e2 < dx:
            err += dx
            y0 += sy


# Each tuple is one line: (start_x, start_y, end_x, end_y, color).
line_segments = [
    (100, 80, 700, 80, (255, 80, 80)),
    (100, 120, 700, 280, (80, 255, 120)),
    (100, 520, 700, 120, (80, 160, 255)),
    (400, 100, 400, 520, (255, 220, 80)),
    (100, 520, 700, 520, (220, 120, 255)),
]

# Main loop.
running = True
while running:
    # Handle close-window event.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear frame.
    screen.fill((20, 20, 20))

    # Draw each line by plotting many single pixels.
    for x0, y0, x1, y1, color in line_segments:
        draw_line_pixels(x0, y0, x1, y1, color)

    # Draw a tiny center marker using pixels too.
    # cx, cy = WIDTH // 2, HEIGHT // 2
    # for dx in range(-4, 5):
    #     put_pixel(cx + dx, cy, (255, 255, 255))
    # for dy in range(-4, 5):
    #     put_pixel(cx, cy + dy, (255, 255, 255))


    label_1 = font.render("No pygame.draw.line.", True, (220, 220, 220))
    label_2 = font.render("Each line is many pixels from draw_line_pixels().", True, (220, 220, 220))
    screen.blit(label_1, (20, 16))
    screen.blit(label_2, (20, 40))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
