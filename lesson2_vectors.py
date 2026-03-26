"""
Lesson 2: Vectors as arrows.
Use vectors for direction and size, then measure vector length.
"""

import math
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 2 - Vectors")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

origin = (WIDTH // 2, HEIGHT // 2)

vectors = [
    (140, -40),
    (-90, -120),
    (70, 140),
]

colors = ["royalblue", "crimson", "seagreen"]


def draw_arrow(start, end, color):
    pygame.draw.line(screen, color, start, end, 3)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)
    head_len = 14
    left = (
        end[0] - head_len * math.cos(angle - math.radians(25)),
        end[1] - head_len * math.sin(angle - math.radians(25)),
    )
    right = (
        end[0] - head_len * math.cos(angle + math.radians(25)),
        end[1] - head_len * math.sin(angle + math.radians(25)),
    )
    pygame.draw.polygon(screen, color, [end, left, right])


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    pygame.draw.line(screen, (221, 221, 221), (0, origin[1]), (WIDTH, origin[1]), 1)
    pygame.draw.line(screen, (221, 221, 221), (origin[0], 0), (origin[0], HEIGHT), 1)
    origin_label = font.render("origin", True, (90, 90, 90))
    screen.blit(origin_label, (origin[0] + 8, origin[1] + 8))


    for i in range(len(vectors)):
        vx, vy = vectors[i]  # (vx, vy) gets x and y from one pair.
        color = colors[i]

        ox, oy = origin
        ex = ox + vx
        ey = oy + vy
        length = math.sqrt(vx * vx + vy * vy)

        draw_arrow((ox, oy), (ex, ey), color)
        vector_label = font.render(f"v=({vx}, {vy}), |v|={length:.1f}", True, color)
        screen.blit(vector_label, (ex + 10, ey - 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
