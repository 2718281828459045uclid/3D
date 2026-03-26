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

# These are the 8 cube corners.
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

# These index pairs tell us which corners to connect with lines.
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

# These groups of four indexes describe each cube face.
faces = [
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (0, 1, 5, 4),
    (2, 3, 7, 6),
    (1, 2, 6, 5),
    (0, 3, 7, 4),
]

# We keep separate angles for x, y, and z rotation.
angle_x = 0.0
angle_y = 0.0
angle_z = 0.0

# These booleans say which axis is currently rotating.
rotate_x_on = True
rotate_y_on = True
rotate_z_on = False

# Different speeds make the motion easier to see.
speed_x = 0.014
speed_y = 0.020
speed_z = 0.012

# Bottom-row toggle buttons.
x_button = pygame.Rect(160, BUTTON_Y, 140, 32)
y_button = pygame.Rect(330, BUTTON_Y, 140, 32)
z_button = pygame.Rect(500, BUTTON_Y, 140, 32)

# Top-right button to draw axes.
axes_toggle_button = pygame.Rect(WIDTH - 180, 16, 164, 32)
show_axes = False


def rotate_x(point, theta):
    # Rotate around X axis.
    x, y, z = point
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return x, y * cos_t - z * sin_t, y * sin_t + z * cos_t


def rotate_y(point, theta):
    # Rotate around Y axis.
    x, y, z = point
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return x * cos_t + z * sin_t, y, -x * sin_t + z * cos_t


def rotate_z(point, theta):
    # Rotate around Z axis.
    x, y, z = point
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return x * cos_t - y * sin_t, x * sin_t + y * cos_t, z


def project(point):
    # Shift object forward so it sits in front of camera.
    x, y, z = point
    z += CAMERA_Z

    # Skip points too close or behind camera.
    if z <= 0.1:
        return None

    # Perspective projection to screen space.
    sx = WIDTH / 2 + (x * FOCAL_LENGTH) / z
    sy = HEIGHT / 2 - (y * FOCAL_LENGTH) / z
    return int(sx), int(sy)


def cross(a, b):
    # Cross product gives a vector perpendicular to both inputs.
    ax, ay, az = a
    bx, by, bz = b
    return ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx


def length(v):
    # Vector length formula.
    x, y, z = v
    return math.sqrt(x * x + y * y + z * z)


def normalize(v):
    # Normalizing means scaling vector length to be 1.
    v_len = length(v)
    if v_len == 0:
        return 0.0, 0.0, 0.0
    x, y, z = v
    return x / v_len, y / v_len, z / v_len


def draw_toggle_button(rect, text, enabled):
    # Green means on, gray means off.
    fill_color = (60, 150, 90) if enabled else (80, 80, 80)
    pygame.draw.rect(screen, fill_color, rect, border_radius=8)
    pygame.draw.rect(screen, (210, 210, 210), rect, 2, border_radius=8)
    label = button_font.render(text, True, (255, 255, 255))
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)


def draw_arrow(start, end, color, width=3):
    # Draw arrow body first.
    pygame.draw.line(screen, color, start, end, width)

    # Work out the direction from start to end.
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    mag = math.hypot(dx, dy)
    if mag < 1:
        return
    ux = dx / mag
    uy = dy / mag
    head_len = 12
    head_w = 7

    # Build the two side points of the arrowhead.
    left = (
        end[0] - ux * head_len + (-uy) * head_w,
        end[1] - uy * head_len + ux * head_w,
    )
    right = (
        end[0] - ux * head_len - (-uy) * head_w,
        end[1] - uy * head_len - ux * head_w,
    )

    # Draw the triangle tip.
    pygame.draw.polygon(screen, color, [end, left, right])


# Main loop: handle input, update math, draw frame.
running = True
while running:
    # Check events and button clicks.
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

    # Start with a black background each frame.
    screen.fill((0, 0, 0))

    # Optionally draw world X/Y/Z axes.
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

    # Rotate each cube vertex by current x/y/z angles.
    transformed = []
    for vertex in vertices:
        p = rotate_x(vertex, angle_x)
        p = rotate_y(p, angle_y)
        p = rotate_z(p, angle_z)
        transformed.append(p)

    # Convert all rotated 3D points to screen points.
    projected = [project(point) for point in transformed]

    # Draw cube wireframe edges.
    for edge in edges:
        # Tuple unpacking splits one pair into i and j.
        i, j = edge
        a = projected[i]
        b = projected[j]
        if a is not None and b is not None:
            pygame.draw.line(screen, (0, 255, 255), a, b, 2)

    # For each face, compute face center and outward normal arrow.
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

        # Two edges on the face let us compute a perpendicular normal.
        edge_a = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
        edge_b = (p3[0] - p0[0], p3[1] - p0[1], p3[2] - p0[2])
        normal = normalize(cross(edge_a, edge_b))

        # Flip if needed so each normal points outward, not inward.
        dot_to_center = normal[0] * center[0] + normal[1] * center[1] + normal[2] * center[2]
        if dot_to_center < 0:
            normal = (-normal[0], -normal[1], -normal[2])

        # Build a small arrow from face center in the normal direction.
        normal_tip = (
            center[0] + normal[0] * 0.8,
            center[1] + normal[1] * 0.8,
            center[2] + normal[2] * 0.8,
        )
        center_2d = project(center)
        tip_2d = project(normal_tip)
        if center_2d is not None and tip_2d is not None:
            draw_arrow(center_2d, tip_2d, (255, 220, 80), 3)

    # Draw title and all control buttons.
    note = font.render("Rotating Cube", True, (150, 150, 150))
    screen.blit(note, (18, 12))

    draw_toggle_button(x_button, "Rotate X", rotate_x_on)
    draw_toggle_button(y_button, "Rotate Y", rotate_y_on)
    draw_toggle_button(z_button, "Rotate Z", rotate_z_on)
    draw_toggle_button(axes_toggle_button, "Show Axes", show_axes)

    # Update only the angles that are currently enabled.
    if rotate_x_on:
        angle_x += speed_x
    if rotate_y_on:
        angle_y += speed_y
    if rotate_z_on:
        angle_z += speed_z

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
