"""
Lesson 6: Full mini 3D pipeline.
Rotate a cube in 3D, project to 2D, and draw wireframe edges.
"""

import math
import pygame

WIDTH, HEIGHT = 800, 600
FOCAL_LENGTH = 320
CAMERA_Z = 4.0
FPS = 60
AXIS_LENGTH = 2.2
BUTTON_Y = HEIGHT - 44

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 6 - Wireframe Cube")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)
button_font = pygame.font.Font(None, 26)

vertices = [
    (-1, -1, -1),
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, 1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, 1, 1),
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
faces = [
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (0, 1, 5, 4),
    (2, 3, 7, 6),
    (1, 2, 6, 5),
    (0, 3, 7, 4),
]

angle_x = 0.0
angle_y = 0.0
angle_z = 0.0
rotate_x_on = True
rotate_y_on = True
rotate_z_on = False
speed_x = 0.014
speed_y = 0.020
speed_z = 0.012

x_button = pygame.Rect(160, BUTTON_Y, 140, 32)
y_button = pygame.Rect(330, BUTTON_Y, 140, 32)
z_button = pygame.Rect(500, BUTTON_Y, 140, 32)
axes_toggle_button = pygame.Rect(WIDTH - 180, 16, 164, 32)
show_axes = False


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


def rotate_z(point, theta):
    x, y, z = point
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return x * cos_t - y * sin_t, x * sin_t + y * cos_t, z


def project(point):
    x, y, z = point
    z += CAMERA_Z
    if z <= 0.1:
        return None
    sx = WIDTH / 2 + (x * FOCAL_LENGTH) / z
    sy = HEIGHT / 2 - (y * FOCAL_LENGTH) / z
    return int(sx), int(sy)


def cross(a, b):
    ax, ay, az = a
    bx, by, bz = b
    return ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx


def length(v):
    x, y, z = v
    return math.sqrt(x * x + y * y + z * z)


def normalize(v):
    v_len = length(v)
    if v_len == 0:
        return 0.0, 0.0, 0.0
    x, y, z = v
    return x / v_len, y / v_len, z / v_len


def draw_toggle_button(rect, text, enabled):
    fill_color = (60, 150, 90) if enabled else (80, 80, 80)
    pygame.draw.rect(screen, fill_color, rect, border_radius=8)
    pygame.draw.rect(screen, (210, 210, 210), rect, 2, border_radius=8)
    label = button_font.render(text, True, (255, 255, 255))
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)


def draw_arrow(start, end, color, width=3):
    pygame.draw.line(screen, color, start, end, width)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    mag = math.hypot(dx, dy)
    if mag < 1:
        return
    ux = dx / mag
    uy = dy / mag
    head_len = 12
    head_w = 7
    left = (
        end[0] - ux * head_len + (-uy) * head_w,
        end[1] - uy * head_len + ux * head_w,
    )
    right = (
        end[0] - ux * head_len - (-uy) * head_w,
        end[1] - uy * head_len - ux * head_w,
    )
    pygame.draw.polygon(screen, color, [end, left, right])


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if x_button.collidepoint(mouse_pos):
                rotate_x_on = not rotate_x_on
            elif y_button.collidepoint(mouse_pos):
                rotate_y_on = not rotate_y_on
            elif z_button.collidepoint(mouse_pos):
                rotate_z_on = not rotate_z_on
            elif axes_toggle_button.collidepoint(mouse_pos):
                show_axes = not show_axes

    screen.fill((0, 0, 0))

    if show_axes:
        axis_segments = [
            ((-AXIS_LENGTH, 0, 0), (AXIS_LENGTH, 0, 0), (255, 90, 90), "X"),
            ((0, -AXIS_LENGTH, 0), (0, AXIS_LENGTH, 0), (90, 255, 90), "Y"),
            ((0, 0, -AXIS_LENGTH), (0, 0, AXIS_LENGTH), (90, 90, 255), "Z"),
        ]

        for axis_start_3d, axis_end_3d, axis_color, axis_name in axis_segments:
            axis_start_2d = project(axis_start_3d)
            axis_end_2d = project(axis_end_3d)
            if axis_start_2d is not None and axis_end_2d is not None:
                pygame.draw.line(screen, axis_color, axis_start_2d, axis_end_2d, 2)
                axis_label = font.render(axis_name, True, axis_color)
                screen.blit(axis_label, (axis_end_2d[0] + 6, axis_end_2d[1] - 6))

    transformed = []
    for vertex in vertices:
        p = rotate_x(vertex, angle_x)
        p = rotate_y(p, angle_y)
        p = rotate_z(p, angle_z)
        transformed.append(p)

    # List comprehension builds a new list from every transformed vertex.
    projected = [project(point) for point in transformed]

    for edge in edges:
        i, j = edge  # Tuple unpacking: each edge has two vertex indexes.
        a = projected[i]
        b = projected[j]
        if a is not None and b is not None:
            pygame.draw.line(screen, (0, 255, 255), a, b, 2)

    for face in faces:
        i0, i1, i2, i3 = face
        p0 = transformed[i0]
        p1 = transformed[i1]
        p2 = transformed[i2]
        p3 = transformed[i3]
        center = (
            (p0[0] + p1[0] + p2[0] + p3[0]) / 4.0,
            (p0[1] + p1[1] + p2[1] + p3[1]) / 4.0,
            (p0[2] + p1[2] + p2[2] + p3[2]) / 4.0,
        )
        edge_a = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
        edge_b = (p3[0] - p0[0], p3[1] - p0[1], p3[2] - p0[2])
        normal = normalize(cross(edge_a, edge_b))
        # Flip when needed so the normal points away from cube center (outward).
        dot_to_center = normal[0] * center[0] + normal[1] * center[1] + normal[2] * center[2]
        if dot_to_center < 0:
            normal = (-normal[0], -normal[1], -normal[2])
        normal_tip = (
            center[0] + normal[0] * 0.8,
            center[1] + normal[1] * 0.8,
            center[2] + normal[2] * 0.8,
        )
        center_2d = project(center)
        tip_2d = project(normal_tip)
        if center_2d is not None and tip_2d is not None:
            draw_arrow(center_2d, tip_2d, (255, 220, 80), 3)

    note = font.render("Rotating Cube", True, (150, 150, 150))
    screen.blit(note, (18, 12))
  
    draw_toggle_button(x_button, "Rotate X", rotate_x_on)
    draw_toggle_button(y_button, "Rotate Y", rotate_y_on)
    draw_toggle_button(z_button, "Rotate Z", rotate_z_on)
    draw_toggle_button(axes_toggle_button, "Show Axes", show_axes)

    if rotate_x_on:
        angle_x += speed_x
    if rotate_y_on:
        angle_y += speed_y
    if rotate_z_on:
        angle_z += speed_z

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
