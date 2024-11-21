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

# Configuración de pantalla
screen_width = 1000
screen_height = 800

# Configuración de la cámara en primera persona
camera_pos = [0.0, 20.0, 0.0]  # Posición inicial de la cámara
camera_front = [0.0, 0.0, -1.0]  # Dirección hacia la que mira la cámara
camera_up = [0.0, 1.0, 0.0]  # Vector hacia arriba
camera_speed = 5.0  # Velocidad de movimiento de la cámara
yaw = -90.0  # Rotación horizontal
pitch = 0.0  # Rotación vertical
sensitivity = 0.4  # Sensibilidad del mouse

# Dimensiones del entorno
DimBoard = 500
drop_off_point = [-50, -100]

# Lifters y basura
lifters = []
nlifters = 1
basuras = []
nbasuras = random.randint(10, 20)

# Crear una variable global para el tráiler
trailer = None
building = None

# Texturas
textures = []
filenames = ["img1.bmp", "wheel.jpeg", "walle.jpeg", "basura.bmp"]

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
    global trailer # Asegúrate de que `trailer` sea global
    global building
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: Primera Persona")
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

    # Generar lifters
    for _ in range(nlifters):
        lifters.append(Lifter(DimBoard, 0.7, textures, drop_off_point))

    # Generar basuras solo en la carretera horizontal
    for _ in range(nbasuras):
        x = random.uniform(-800, 800)  # Carretera horizontal en eje X
        z = random.uniform(480, 500)  # Carretera horizontal en eje Z
        basuras.append(Basura(DimBoard, 1, textures, 3, texture_id))
        basuras[-1].Position = [x, 0, z]  # Asignar posición ajustada

    # Crear una instancia del tráiler con posición y rotación específicas
    trailer = Trailer(
        obj_file="camion.obj",
        scale=0.5,
        position=(0, 0, -DimBoard),  # Posición fija en X, Y, Z
        rotation=(270, 1, 0, 0)  # Rotar 90 grados sobre el eje X
    )


    # Crear una instancia del tráiler con posición y rotación específicas
    building = Building(
        obj_file="building.obj",
        scale=0.2,
        position=(0, 0, 80),  # Posición fija en X, Y, Z
        rotation=(270, 1, 0, 0)  # Rotar 90 grados sobre el eje X
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

def display():
    global trailer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    planoText()
    for obj in lifters:
        obj.draw()
        obj.update()
    for obj in basuras:
        obj.draw()

     # Dibujar el tráiler
    if trailer:
        trailer.set_additional_rotation(90, 0, 0, 1)  # Rotar 90 grados sobre el eje z
        glPushMatrix()
        glTranslatef(10, 0, 70)  # Posicionar el tráiler en la carretera horizontal
        trailer.draw()
        glPopMatrix()



    # Dibujar el tráiler
    if building:
        building.set_additional_rotation(90, 0, 0, 1)  # Rotar 90 grados sobre el eje z
        glPushMatrix()
        glTranslatef(10, 0, 70)  # Posicionar el tráiler en la carretera horizontal
        building.draw()
        glPopMatrix()
    pygame.display.flip()

# AQUI SE DIBUJA EL PLANO

def planoText():
    glColor3f(0.0, 0.0, 1.0)  # Color azul para el resto del terreno
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glVertex3d(-DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, -DimBoard)
    glEnd()

    # Carretera vertical (parte de la T)
    glColor3f(0.3, 0.3, 0.3)  # Color gris para la carretera
    glBegin(GL_QUADS)
    glVertex3d(-20, 0.1, -DimBoard)  # Añadir un leve "0.1" en altura para evitar z-fighting
    glVertex3d(20, 0.1, -DimBoard)
    glVertex3d(20, 0.1, DimBoard)
    glVertex3d(-20, 0.1, DimBoard)
    glEnd()

    # Carretera horizontal (parte superior de la T)
    glBegin(GL_QUADS)
    glVertex3d(-800, 0.1, 480)  # La parte superior de la T está en z = 100
    glVertex3d(800, 0.1, 480)
    glVertex3d(800, 0.1, 500)
    glVertex3d(-800, 0.1, 500)
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
    if keys[pygame.K_w]:  # Avanzar
        camera_pos[0] += camera_speed * camera_front[0]
        camera_pos[1] += camera_speed * camera_front[1]
        camera_pos[2] += camera_speed * camera_front[2]
    if keys[pygame.K_s]:  # Retroceder
        camera_pos[0] -= camera_speed * camera_front[0]
        camera_pos[1] -= camera_speed * camera_front[1]
        camera_pos[2] -= camera_speed * camera_front[2]
    if keys[pygame.K_a]:  # Izquierda
        right = [
            camera_front[1] * camera_up[2] - camera_front[2] * camera_up[1],
            camera_front[2] * camera_up[0] - camera_front[0] * camera_up[2],
            camera_front[0] * camera_up[1] - camera_front[1] * camera_up[0]
        ]
        camera_pos[0] -= camera_speed * right[0]
        camera_pos[2] -= camera_speed * right[2]
    if keys[pygame.K_d]:  # Derecha
        right = [
            camera_front[1] * camera_up[2] - camera_front[2] * camera_up[1],
            camera_front[2] * camera_up[0] - camera_front[0] * camera_up[2],
            camera_front[0] * camera_up[1] - camera_front[1] * camera_up[0]
        ]
        camera_pos[0] += camera_speed * right[0]
        camera_pos[2] += camera_speed * right[2]
    lookAt()
    display()
    pygame.time.wait(10)

pygame.quit()