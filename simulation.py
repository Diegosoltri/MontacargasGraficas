import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import sys
sys.path.append('..')
from Lifter import Lifter
from Basura import Basura
from trailer import Trailer
from building import Building
from amazon import Amazon

# Import your backend module
import base

# Screen configuration
screen_width = 500
screen_height = 500

# First-person camera configuration
camera_pos = [0.0, 20.0, 0.0]     # Initial camera position
camera_front = [0.0, 0.0, -1.0]   # Direction the camera is looking at
camera_up = [0.0, 1.0, 0.0]       # Up vector
camera_speed = 10.0                # Camera movement speed
yaw = -90.0                       # Horizontal rotation
pitch = 0.0                       # Vertical rotation
sensitivity = 0.4                 # Mouse sensitivity

# Environment dimensions
DimBoard = 240
drop_off_point = [-50, -100]

# Lifters and trash
lifters = []
nlifters = 1

basuras = []
nbasuras = 15

# Global variables for trailer and buildings
trailer = None
buildings = None

grass_texture = None  # Grass texture
sky_texture = None    # Sky texture
wall_texture = None   # Wall texture
amazon = None

# Textures
textures = []
filenames = ["img1.bmp", "wheel.jpeg", "walle.jpeg", "texturacaja.jpg"]

def load_texture(image_path):
    texture_surface = pygame.image.load(image_path)
    texture_data = pygame.image.tostring(texture_surface, "RGB", True)
    width, height = texture_surface.get_size()
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return texture_id

def Texturas(filepath):
    textures.append(glGenTextures(1))
    id = len(textures) - 1
    glBindTexture(GL_TEXTURE_2D, textures[id])
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    image = pygame.image.load(filepath).convert()
    w, h = image.get_size()
    image_data = pygame.image.tostring(image, "RGBA")
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    glGenerateMipmap(GL_TEXTURE_2D)

def Init():
    global trailer
    global buildings
    global grass_texture
    global sky_texture
    global amazon
    global wall_texture
    global lifters
    global basuras

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: First Person")
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, screen_width / screen_height, 0.01, 1800.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    for i in filenames:
        Texturas(i)
    texture_id = load_texture('texturacaja.jpg')

    # Load textures for grass, sky, and walls
    grass_texture = load_texture('cesped.jpg')
    sky_texture = load_texture('cielo.jpeg')
    wall_texture = load_texture('ciudad.jpg')

    # Get lifter data from base.py
    lifter_data = base.get_lifter_data(nlifters, DimBoard, drop_off_point)
    lifters = []
    for pos, dir in zip(lifter_data.positions, lifter_data.directions):
        lifter = Lifter(DimBoard, 0.7, textures, drop_off_point, position=pos, direction=dir)
        lifters.append(lifter)

    # Get trash data from base.py
    box_data = base.get_box_data(nbasuras, DimBoard)
    basuras = []
    for pos, size in zip(box_data.positions, box_data.sizes):
        basura = Basura(DimBoard, 1, textures, 3, size)
        basura.Position = list(pos)
        basuras.append(basura)

    # Get trailer data from base.py
    trailer_data = base.get_trailer_data(DimBoard)
    trailer = Trailer(
        obj_file="camion.obj",
        scale=0.5,
        position=trailer_data.position,
        rotation=(270, 1, 0, 0)
    )

    # Create multiple buildings
    buildings = [
        Building(
            obj_file="building.obj",
            scale=0.1,
            position=(40, 0, 0 + i * 40),  # Position in a row
            rotation=(270, 1, 0, 0)
        )
        for i in range(3)
    ]

    # Create an instance of Amazon
    amazon = Amazon(
        obj_file="amazon.obj",
        scale=0.5,
        position=(90, 0, 50),  # Fixed position in X, Y, Z
        rotation=(270, 1, 0, 0)
    )

def lookAt():
    glLoadIdentity()
    center_x = camera_pos[0] + camera_front[0]
    center_y = camera_pos[1] + camera_front[1]
    center_z = camera_pos[2] + camera_front[2]
    gluLookAt(
        camera_pos[0], camera_pos[1], camera_pos[2],
        center_x, center_y, center_z,
        camera_up[0], camera_up[1], camera_up[2]
    )

def process_mouse_motion(mouse_motion):
    global yaw, pitch, camera_front
    x_offset, y_offset = mouse_motion
    x_offset *= sensitivity
    y_offset *= sensitivity
    yaw += x_offset
    pitch -= y_offset
    pitch = max(-89.0, min(89.0, pitch))
    front_x = math.cos(math.radians(yaw)) * math.cos(math.radians(pitch))
    front_y = math.sin(math.radians(pitch))
    front_z = math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
    camera_front = [front_x, front_y, front_z]
    norm = math.sqrt(sum(f**2 for f in camera_front))
    camera_front = [f / norm for f in camera_front]

def draw_skybox():
    """Draws a sky with texture."""
    glBindTexture(GL_TEXTURE_2D, sky_texture)
    glEnable(GL_TEXTURE_2D)
    glColor3f(1.0, 1.0, 1.0)  # Ensure not to alter the texture color

    size = DimBoard * 2  # Ensure the sky wraps around the entire environment

    glBegin(GL_QUADS)
    # Top face (sky)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-size, size, -size)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(size, size, -size)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(size, size, size)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-size, size, size)
    glEnd()

    glDisable(GL_TEXTURE_2D)

def draw_walls():
    glBindTexture(GL_TEXTURE_2D, wall_texture)
    glEnable(GL_TEXTURE_2D)
    glColor3f(1.0, 1.0, 1.0)  # Ensure not to alter the texture color

    height = DimBoard // 2  # Wall height
    size = DimBoard         # Wall length

    glBegin(GL_QUADS)
        # Front wall
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-size, 0, size)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(size, 0, size)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(size, height, size)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-size, height, size)

        # Back wall
    glTexCoord2f(0.0, 0.0)
    glVertex3d(size, 0, -size)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-size, 0, -size)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(-size, height, -size)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(size, height, -size)

        # Left wall
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-size, 0, -size)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-size, 0, size)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(-size, height, size)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-size, height, -size)

        # Right wall
    glTexCoord2f(0.0, 0.0)
    glVertex3d(size, 0, size)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(size, 0, -size)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(size, height, -size)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(size, height, size)
    glEnd()

    glDisable(GL_TEXTURE_2D)

def display():
    global trailer, buildings, amazon

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_skybox()
    draw_walls()
    planoText()

    for obj in lifters:
        obj.draw()
        obj.update()

    for obj in basuras:
        obj.draw()

    # Draw the trailer
    if trailer:
        trailer.set_additional_rotation(90, 0, 0, 1)  # Rotate 90 degrees around the z-axis
        glPushMatrix()
        glTranslatef(10, 0, 70)  # Position the trailer on the horizontal road
        trailer.draw()
        glPopMatrix()

    # Draw all buildings
    for building in buildings:
        building.set_additional_rotation(180, 0, 0, 1)
        glPushMatrix()
        glTranslatef(*building.position)  # Use the specific position of each building
        building.draw()
        glPopMatrix()   

    # Draw Amazon
    if amazon:
        amazon.set_additional_rotation(180, 0, 0, 1)  # Rotate 180 degrees around the z-axis
        glPushMatrix()
        glTranslatef(*amazon.position)  # Use the assigned position for Amazon
        amazon.draw()
        glPopMatrix()

    pygame.display.flip()

# HERE WE DRAW THE PLANE

# Modification in the planoText function to apply the texture
def planoText():
    # Activate the grass texture
    glBindTexture(GL_TEXTURE_2D, grass_texture)
    glEnable(GL_TEXTURE_2D)
    glColor3f(1.0, 1.0, 1.0)  # Ensure the color doesn't modify the texture

    glBegin(GL_QUADS)
    # Assign texture coordinates with glTexCoord2f
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-DimBoard, 0, DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, 0, DimBoard)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(DimBoard, 0, -DimBoard)
    glEnd()

    glDisable(GL_TEXTURE_2D)

    # Vertical road (part of the T)
    glColor3f(0.3, 0.3, 0.3)  # Gray color for the road
    glBegin(GL_QUADS)
    glVertex3d(-20, 0.1, -DimBoard)  # Add a slight "0.1" in height to avoid z-fighting
    glVertex3d(20, 0.1, -DimBoard)
    glVertex3d(20, 0.1, DimBoard)
    glVertex3d(-20, 0.1, DimBoard)
    glEnd()

    # Horizontal road (top part of the T)
    glColor3f(0.3, 0.3, 0.3)  # Gray color for the road
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0.1, DimBoard - 20)
    glVertex3d(DimBoard, 0.1, DimBoard - 20)
    glVertex3d(DimBoard, 0.1, DimBoard)
    glVertex3d(-DimBoard, 0.1, DimBoard)
    glEnd()

done = False
Init()
pygame.event.set_grab(True)
pygame.mouse.set_visible(False)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEMOTION:
            process_mouse_motion(event.rel)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:  # Move forward
        camera_pos[0] += camera_speed * camera_front[0]
        camera_pos[1] += camera_speed * camera_front[1]
        camera_pos[2] += camera_speed * camera_front[2]
    if keys[pygame.K_s]:  # Move backward
        camera_pos[0] -= camera_speed * camera_front[0]
        camera_pos[1] -= camera_speed * camera_front[1]
        camera_pos[2] -= camera_speed * camera_front[2]
    if keys[pygame.K_a]:  # Move left
        right = [
            camera_front[1] * camera_up[2] - camera_front[2] * camera_up[1],
            camera_front[2] * camera_up[0] - camera_front[0] * camera_up[2],
            camera_front[0] * camera_up[1] - camera_front[1] * camera_up[0]
        ]
        camera_pos[0] -= camera_speed * right[0]
        camera_pos[2] -= camera_speed * right[2]
    if keys[pygame.K_d]:  # Move right
        right = [
            camera_front[1] * camera_up[2] - camera_front[2] * camera_up[1],
            camera_front[2] * camera_up[0] - camera_front[0] * camera_up[2],
            camera_front[0] * camera_up[1] - camera_front[1] * camera_up[0]
        ]
        camera_pos[0] += camera_speed * right[0]
        camera_pos[2] += camera_speed * right[2]

    lookAt()
    display()
    pygame.time.wait(16)

pygame.quit()