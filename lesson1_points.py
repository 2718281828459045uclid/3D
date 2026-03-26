"""
Lesson 1: Points on a 2D screen.
Learn how screen coordinates work and how to draw points at (x, y).
"""

import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 1 - Points")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

center_x, center_y = WIDTH // 2, HEIGHT // 2

points = [
    (100, 80),
    (200, 300),
    (350, 225),
    (550, 120),
    (600, 360),
]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    pygame.draw.line(screen, (221, 221, 221), (0, center_y), (WIDTH, center_y), 1)
    pygame.draw.line(screen, (221, 221, 221), (center_x, 0), (center_x, HEIGHT), 1)

    for x, y in points:
        pygame.draw.circle(screen, (65, 105, 225), (x, y), 4)
        label = font.render(f"({x}, {y})", True, (0, 0, 0))
        screen.blit(label, (x + 12, y - 18))

    note_1 = font.render("Screen origin is top left (0, 0)", True, (90, 90, 90))
    note_2 = font.render("Center axes", True, (90, 90, 90))
    # .blit draws the given surface (like a label or image) onto the screen at the specified position.
    screen.blit(note_1, (16, 14))
    screen.blit(note_2, (center_x + 14, center_y + 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
