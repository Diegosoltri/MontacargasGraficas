import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import sys
import requests
import json
sys.path.append('..')
from Lifter import Lifter
from Basura import Basura
from trailer import Trailer
from building import Building
from amazon import Amazon

# URL base de la API y obtención de datos
URL_BASE = "http://localhost:8000"
payload = {"dim": [49, 49, 49]}  # Define la dimensión esperada en el servidor

try:
    r = requests.post(URL_BASE + "/simulations", json=payload, allow_redirects=False)
    datos = r.json()
    print("Datos iniciales:", datos)
except requests.exceptions.RequestException as e:
    print(f"Error al iniciar la simulación: {e}")
    sys.exit()

LOCATION = datos.get("Location")
if not LOCATION:
    print("No se encontró la ubicación de la simulación.")
    sys.exit()

DIRECTION_MAP = {
    "north": [0, 0, 1],
    "south": [0, 0, -1],
    "east": [1, 0, 0],
    "west": [-1, 0, 0]
}

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
filenames = ["Graficos/img1.bmp", "Graficos/wheel.jpeg", "Graficos/walle.jpeg", "Graficos/texturacaja.jpg"]

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

def map_position(pos):
    # Con dimensiones ajustadas, el factor de escala es 1
    mapped_x = pos[0] - DimBoard / 2
    mapped_y = pos[1]
    mapped_z = pos[2] - DimBoard / 2
    return [mapped_x, mapped_y, mapped_z]

def Init():
    global trailer
    global buildings
    global grass_texture
    global sky_texture
    global amazon
    global wall_texture
    global lifters
    global basuras
    global datos  # Usar los datos iniciales ya obtenidos
    SCALE_FACTOR = 10

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
    texture_id = load_texture('Graficos/texturacaja.jpg')

    # Load textures for grass, sky, and walls
    grass_texture = load_texture('Graficos/cesped.jpg')
    sky_texture = load_texture('Graficos/cielo.jpeg')
    wall_texture = load_texture('Graficos/ciudad.jpg')

    # Reutilizar datos iniciales
    sim_data = datos

    # Inicializar lifters
    
    lifters = []
    for lifter_info in sim_data.get("lifts", []):
        pos = lifter_info["pos"]
        mapped_pos = map_position(pos)  # Mapear posición
        dir_str = lifter_info.get("direction", "north")  # Dirección como string
        carry_box = lifter_info.get("carrying_box")  # Indica si lleva una caja
        move_count = lifter_info.get("move_count")  # Número de movimientos
        dir_vector = DIRECTION_MAP.get(dir_str.lower(), [0, 0, 1])  # Mapea cadenas a vectores
        lifter = Lifter(DimBoard, 0.7, textures, drop_off_point, position=mapped_pos, direction=dir_vector)
        lifters.append(lifter)

    basuras = []
    OFFSET_Y = 2  # Eleva las cajas 5 unidades en Y
    SPACING = 20   # Incrementa la separación en X y Z
    for box_info in sim_data.get("boxes", []):
        pos = box_info["pos"]
        size = box_info["WHD"]  # Dimensiones originales de la caja

        # Mapear posición
        mapped_pos = map_position(pos)

        # Generar offsets aleatorios
        random_offset_x = random.uniform(-SPACING, SPACING)
        random_offset_z = random.uniform(-SPACING, SPACING)

        # Aplicar offsets a la posición mapeada
        mapped_pos[0] += random_offset_x
        mapped_pos[1] += OFFSET_Y
        mapped_pos[2] += random_offset_z

        # Escalar tamaños de las cajas
        scaled_size = [dimension * SCALE_FACTOR for dimension in size]

        # Crear la instancia de Basura con la posición y el tamaño escalado
        basura = Basura(
            position=mapped_pos,     # Posición mapeada de la caja
            textures=textures,       # Lista de texturas cargadas
            txtIndex=3,              # Índice de la textura en la lista
            size=scaled_size,       # Tamaño escalado de la caja
            offset_x=random_offset_x,  # Offset aleatorio en X
            offset_y=OFFSET_Y,         # Offset en Y
            offset_z=random_offset_z   # Offset aleatorio
        )
        basuras.append(basura)

    # Inicializar tráiler
    trailer_info = sim_data.get("trailers")[0] if sim_data.get("trailers") else None
    if trailer_info:
        mapped_pos = map_position(trailer_info["pos"])  # Mapear posición
        trailer = Trailer(
            obj_file="Graficos/camion.obj",
            scale=0.5,
            position=mapped_pos,
            rotation=(270, 1, 0, 0)
        )

    # Create multiple buildings
    buildings = [
        Building(
            obj_file="Graficos/building.obj",
            scale=0.1,
            position=(40, 0, -60 + i * 20),  # Position in a row
            rotation=(270, 1, 0, 0)
        )
        for i in range(3)
    ]

    # Create an instance of Amazon
    amazon = Amazon(
        obj_file="Graficos/amazon.obj",
        scale=0.6,
        position=(40, 0, 45),  # Fixed position in X, Y, Z
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

def update_from_api():
    global lifters, basuras, trailer, LOCATION

    try:
        sim_data = requests.get(URL_BASE + LOCATION).json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos de la simulación: {e}")
        return  # Puedes manejar este caso según tus necesidades

    # Actualizar lifters
    lifter_data = sim_data.get('lifts', [])
    for lifter, lifter_info in zip(lifters, lifter_data):
        lifter_pos_mapped = map_position(lifter_info["pos"])
        move_count = lifter_info.get("move_count", lifter.move_count)
        carry_box = lifter_info.get("carrying_box")
        dir_str = lifter_info.get("direction", "north")
        dir_vector = DIRECTION_MAP.get(dir_str.lower(), [0, 0, 1])
        lifter.set_position(lifter_pos_mapped, move_count, carry_box, direction=dir_vector)

        # Convertir dirección de string a vector
        dir_str = lifter_info.get("direction", "north")
        dir_vector = DIRECTION_MAP.get(dir_str.lower(), [0, 0, 1])
        lifter.Direction = dir_vector

        #lifter.update()

    # Actualizar basuras
    box_data = sim_data.get('boxes', [])
    for basura, box_info in zip(basuras, box_data):
        # Mapear posición
        basura_pos_mapped = map_position(box_info["pos"])
        # Re-aplicar los offsets almacenados
        basura_pos_mapped[0] += basura.offset_x
        basura_pos_mapped[1] += basura.offset_y
        basura_pos_mapped[2] += basura.offset_z
        basura.Position = basura_pos_mapped
        # Puedes actualizar otros atributos si es necesario

    # Actualizar tráiler
    trailer_data = sim_data.get('trailers', [])
    if trailer_data and trailer:
        # Mapear posición
        trailer_pos_mapped = map_position(trailer_data[0]["pos"])
        trailer.position = trailer_pos_mapped
        
        
def display():
    global trailer, buildings, amazon

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_skybox()
    draw_walls()
    planoText()

    for obj in lifters:
        obj.draw()
        #obj.update()

    for obj in basuras:
        obj.draw()
        

    # Draw the trailer
    if trailer:
        trailer.set_additional_rotation(90, 0, 0, 1)  # Rotate 90 degrees around the z-axis
        glPushMatrix()
        glTranslatef(*trailer.position)  # Mover el tráiler a su posición mapeada
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
    glVertex3d(-20, 0.5, -DimBoard)  # Add a slight "0.1" in height to avoid z-fighting
    glVertex3d(20, 0.1, -DimBoard)
    glVertex3d(20, 0.1, DimBoard)
    glVertex3d(-20, 0.1, DimBoard)
    glEnd()

    # Horizontal road (top part of the T)
    glColor3f(0.3, 0.3, 0.3)  # Gray color for the road
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0.5, DimBoard - 20)
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
    update_from_api()
    pygame.time.wait(16)

pygame.quit()