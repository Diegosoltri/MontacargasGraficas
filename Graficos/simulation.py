import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
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
from truck import Truck

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

# Configuración de la pantalla
screen_width = 800  # Aumentado para mejor visibilidad
screen_height = 600

# Configuración de la cámara en primera persona
camera_pos = [0.0, 20.0, 50.0]     # Posición inicial de la cámara más cerca en Z
camera_front = [0.0, -0.5, -1.0]   # Dirección inclinada hacia abajo
camera_up = [0.0, 1.0, 0.0]        # Vector arriba
camera_speed = 20.0                # Velocidad de movimiento de la cámara
yaw = -90.0                        # Rotación horizontal
pitch = -40.0                      # Rotación vertical inclinada hacia abajo
sensitivity = 0.5                 # Sensibilidad del ratón

# Dimensiones del entorno
DimBoard = 240
drop_off_point = [-50, -100]

# Lifters y basura
lifters = []
nlifters = 1

basuras = []
nbasuras = 15

# Variables globales para el tráiler y edificios
trailer = None
buildings = None

grass_texture = None  # Textura de césped
sky_texture = None    # Textura de cielo
wall_texture = None   # Textura de paredes
truck_texture = None  # Textura de camión
amazon = None
truck = None

# Texturas
textures = []
filenames = ["Graficos/img1.bmp", "Graficos/wheel.jpeg", "Graficos/walle.jpeg", "Graficos/texturacaja.jpg"]

# Obtener la dimensión máxima de las dimensiones recibidas
max_dimension = max(payload["dim"])  # En este caso, 49

# Calcular el factor de escala, dejando un margen del 50%
SCALE_FACTOR = (DimBoard * 0.5) / max_dimension  # Por ejemplo, (240 * 0.5) / 49 ≈ 2.448

# Definir el multiplicador de escala para las cajas
BOX_SCALE_MULTIPLIER = 5  # Puedes ajustar este valor según necesites

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
    mapped_x = (pos[0] * SCALE_FACTOR) - (DimBoard / 2)
    mapped_y = pos[1] * SCALE_FACTOR
    mapped_z = (pos[2] * SCALE_FACTOR) - (DimBoard / 2)
    return [mapped_x, mapped_y, mapped_z]

def update_camera_front():
    global camera_front
    front_x = math.cos(math.radians(yaw)) * math.cos(math.radians(pitch))
    front_y = math.sin(math.radians(pitch))
    front_z = math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
    camera_front = [front_x, front_y, front_z]
    # Normalizar el vector
    norm = math.sqrt(sum(f**2 for f in camera_front))
    camera_front = [f / norm for f in camera_front]

def Init():
    global trailer
    global truck
    global buildings
    global grass_texture
    global sky_texture
    global amazon
    global wall_texture
    global lifters
    global basuras
    global datos  # Usar los datos iniciales ya obtenidos
    global drop_off_point_mapped  # Declarar la variable global
    global truck_texture

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: First Person")
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, screen_width / screen_height, 0.1, 1800.0)  # Aumentar near plane a 0.1 para mejor profundidad
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)

    # **Habilitar Blending para Transparencia**
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    for i in filenames:
        Texturas(i)
    texture_id = load_texture('Graficos/texturacaja.jpg')


    # Cargar textura específica para el camión
    truck_texture = load_texture('Graficos/walle.jpeg')
    grass_texture = load_texture('Graficos/cesped.jpg')
    sky_texture = load_texture('Graficos/cielo.jpeg')
    wall_texture = load_texture('Graficos/ciudad.jpg')

    # **Actualizar camera_front basado en yaw y pitch**
    update_camera_front()

    # Reutilizar datos iniciales
    sim_data = datos

    # Inicializar tráiler
    trailer_info = sim_data.get("trailers")[0] if sim_data.get("trailers") else None
    if trailer_info:
        print("Posición original del tráiler:", trailer_info["pos"])
        mapped_pos = map_position(trailer_info["pos"])  # Mapear posición
        print("Posición mapeada del tráiler:", mapped_pos)

        # **Eliminar o Ajustar el Offset en Y**
        y_offset = -2.0  # Ajusta este valor según sea necesario
        mapped_pos[1] += y_offset
        print(f"Posición mapeada del tráiler después de aplicar offset en Y: {mapped_pos}")

        # **Crear el Prisma Rectangular Translúcido para Depuración**
        trailer = Trailer(
            scale=SCALE_FACTOR * 10,  # Aumentar la escala a 24.48
            position=mapped_pos,
            rotation=(0.0, 0.0, 0.0, 1.0),  # Ajusta la rotación si es necesario
            color=(1.0, 0.0, 0.0, 0.5),  # Rojo translúcido
            width=1.0,    # Ancho del tráiler
            height=2.0,   # Alto del tráiler
            depth=1.5     # Profundidad del tráiler
        )

        # Mapear el punto de entrega usando la posición del tráiler
        drop_off_point_sim = trailer_info["pos"]
        drop_off_point_mapped = map_position(drop_off_point_sim)
        drop_off_point_mapped[1] += y_offset  # Asegurar alineación en Y
        print("Punto de entrega original:", drop_off_point_sim)
        print("Punto de entrega mapeado:", drop_off_point_mapped)

    else:
        print("No se encontró información del tráiler.")
        drop_off_point_mapped = [0, 0, 0]  # O algún valor por defecto

    # Inicializar los lifters
    lifters = []
    for lifter_info in sim_data.get("lifts", []):
        pos = lifter_info["pos"]
        mapped_pos = map_position(pos)  # Mapear posición
        dir_str = lifter_info.get("direction", "north")  # Dirección como string
        carry_box = lifter_info.get("carrying_box")  # Indica si lleva una caja
        move_count = lifter_info.get("move_count")  # Número de movimientos
        dir_vector = DIRECTION_MAP.get(dir_str.lower(), [0, 0, 1])  # Mapea cadenas a vectores
        lifter = Lifter(DimBoard, 0.7 * SCALE_FACTOR, textures, drop_off_point_mapped, position=mapped_pos, direction=dir_vector)
        lifters.append(lifter)

    # Inicializar las basuras
    basuras = []
    OFFSET_Y = 2 * SCALE_FACTOR  # Eleva las cajas en Y
    SPACING = 1 * SCALE_FACTOR   # Incrementa la separación en X y Z
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

        # Escalar tamaños de las cajas con un factor adicional
        scaled_size = [dimension * SCALE_FACTOR * BOX_SCALE_MULTIPLIER for dimension in size]

        # Crear la instancia de Basura con la posición y el tamaño escalado
        basura = Basura(
            position=mapped_pos,       # Posición mapeada de la caja
            textures=textures,         # Lista de texturas cargadas
            txtIndex=3,                # Índice de la textura en la lista
            size=scaled_size,          # Tamaño escalado de la caja
            offset_x=random_offset_x,  # Offset aleatorio en X
            offset_y=OFFSET_Y,         # Offset en Y
            offset_z=random_offset_z   # Offset aleatorio en Z
        )
        basuras.append(basura)

    # Crear múltiples edificios sin escalado
    buildings = [
        Building(
            obj_file="Graficos/building.obj",
            scale=0.1,  # No se aplica SCALE_FACTOR
            position=(40, 0, -60 + i * 20),  # Posición en una fila
            rotation=(270, 1, 0, 0)
        )
        for i in range(3)
    ]

    # Crear una instancia de Amazon sin escalado
    amazon = Amazon(
        obj_file="Graficos/amazon.obj",
        scale=0.6,  # No se aplica SCALE_FACTOR
        position=(40, 0, 45),  # Posición fija en X, Y, Z
        rotation=(270, 1, 0, 0)
    )

    # Crear una instancia de Amazon sin escalado
    truck = Truck(
        obj_file="Graficos/truck.obj",
        scale=0.05,  # No se aplica SCALE_FACTOR
        position=(-50, 0, -50),  # Posición fija en X, Y, Z
        rotation=(0, 1, 0, 0)
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
    global yaw, pitch
    x_offset, y_offset = mouse_motion
    x_offset *= sensitivity
    y_offset *= sensitivity
    yaw += x_offset
    pitch -= y_offset
    pitch = max(-89.0, min(89.0, pitch))
    update_camera_front()

def draw_skybox():
    """Dibuja un cielo con textura."""
    glBindTexture(GL_TEXTURE_2D, sky_texture)
    glEnable(GL_TEXTURE_2D)
    glColor3f(1.0, 1.0, 1.0)  # Asegura que el color no altere la textura

    size = DimBoard  # Asegura que el cielo envuelva todo el entorno

    glBegin(GL_QUADS)
    # Cara superior (cielo)
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
    glColor3f(1.0, 1.0, 1.0)  # Asegura que el color no altere la textura

    height = DimBoard // 2  # Altura de la pared
    size = DimBoard         # Longitud de la pared

    glBegin(GL_QUADS)
    # Pared frontal
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-size, 0, size)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(size, 0, size)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(size, height, size)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-size, height, size)

    # Pared trasera
    glTexCoord2f(0.0, 0.0)
    glVertex3d(size, 0, -size)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-size, 0, -size)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(-size, height, -size)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(size, height, -size)

    # Pared izquierda
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-size, 0, -size)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-size, 0, size)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(-size, height, size)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-size, height, -size)

    # Pared derecha
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
        return

    # Actualizar lifters
    lifter_data = sim_data.get('lifts', [])
    for lifter, lifter_info in zip(lifters, lifter_data):
        lifter_pos_mapped = map_position(lifter_info["pos"])
        move_count = lifter_info.get("move_count", lifter.move_count)
        carrying_box = lifter_info.get("carrying_box", False)  # Asegúrate de usar 'carrying_box'
        dir_str = lifter_info.get("direction", "north")
        dir_vector = DIRECTION_MAP.get(dir_str.lower(), [0, 0, 1])  # Mapea cadenas a vectores
        lifter.set_position(lifter_pos_mapped, move_count, carrying_box, direction=dir_vector)

    # Obtener la única dirección y posición del montacargas
    if lifters:
        lifter = lifters[0]
        lifter_position = lifter.Position
        lifter_direction = lifter.Direction
        lifter_angle = lifter.base_angle + lifter.carrying_angle
    else:
        lifter_position = [0, 0, 0]
        lifter_direction = [0, 0, 0]  # Dirección predeterminada
        lifter_angle = 0

    # Convertir el ángulo del montacargas a radianes
    lifter_angle_rad = math.radians(lifter_angle)

    # Calcular el frente visual basado en la rotación
    visual_direction = [
        math.cos(lifter_angle_rad),  # X
        0,                           # Y (no cambia para el frente)
        -math.sin(lifter_angle_rad)  # Z
    ]

    # Calcular el lateral visual (perpendicular al frente)
    perpendicular_direction = [
        -visual_direction[2],  # X
        0,                     # Y
        visual_direction[0]    # Z
    ]

    # Actualizar basuras
    box_data = sim_data.get('boxes', [])
    for basura, box_info in zip(basuras, box_data):
    # Actualizar el estado 'carried'
        carried = box_info.get('carried', False)
        basura.carried = carried

        if carried:
            # **Configurar el Offset**
            offset_distance_forward = 50  # Distancia hacia adelante (o hacia atrás)
            offset_distance_side = 0    # Distancia hacia los lados
            offset_height = 5           # Elevación en Y para la caja

            # **Calcular el Offset Basado en la Orientación**
            # Frente o atrás (dirección principal del montacargas)
            forward_offset = [
                visual_direction[0] * offset_distance_forward,
                0,
                visual_direction[2] * offset_distance_forward
            ]

            # Lados (perpendicular al frente)
            # Si el frente está en -X o +X, el eje perpendicular será Z. Si está en Z, será X.
            side_offset = [
                perpendicular_direction[0] * offset_distance_side,
                0,  # No cambiar la altura
                perpendicular_direction[2] * offset_distance_side
            ]

            # **Elegir la Posición Final**
            # Combinar el offset del frente con el offset lateral
            # Por ejemplo, si quieres que esté a la izquierda y al frente:
            offset = [
                forward_offset[0] + side_offset[0],
                offset_height ,  # Ajustar la altura de la caja
                forward_offset[2] + side_offset[2]
            ]

            # Actualizar la posición de la caja
            basura.Position = [
                lifter_position[0] + offset[0],
                lifter_position[1] + offset[1],
                lifter_position[2] + offset[2]
            ]
        else:
            # Si no está siendo transportada, mantener su posición en el suelo
            # Aplicar los offsets aleatorios
            basura.Position = [
                box_info["pos"][0] * SCALE_FACTOR - (DimBoard / 2) + basura.offset_x,
                box_info["pos"][1] * SCALE_FACTOR + basura.offset_y,
                box_info["pos"][2] * SCALE_FACTOR - (DimBoard / 2) + basura.offset_z
            ]
            

    # Actualizar tráiler
    trailer_data = sim_data.get('trailers', [])
    if trailer_data and trailer:
        # Mapear posición
        trailer_pos_mapped = map_position(trailer_data[0]["pos"])
        # Ajustar Y si es necesario
        trailer_pos_mapped[1] += -2.0  # Asegurar que esté alineado con el suelo
        trailer.position = trailer_pos_mapped

def display():
    global trailer, buildings, amazon

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_skybox()
    draw_walls()
    planoText()

    for obj in lifters:
        obj.draw()

    for obj in basuras:
        obj.draw()

    # Dibujar el tráiler (prisma rectangular translúcido)
    if trailer:
        trailer.set_additional_rotation(0, 0, 0, 1)  # Ajusta la rotación si es necesario
        trailer.draw()  # Sin glPushMatrix y glTranslatef

    # Dibujar todos los edificios (sin escalado)
    for building in buildings:
        building.set_additional_rotation(180, 0, 0, 1)
        glPushMatrix()
        glTranslatef(*building.position)  # Usar la posición específica de cada edificio
        building.draw()
        glPopMatrix()

    # Dibujar Amazon (sin escalado)
    if amazon:
        amazon.set_additional_rotation(180, 0, 0, 1)  # Rotar 180 grados alrededor del eje z
        glPushMatrix()
        glTranslatef(*amazon.position)  # Usar la posición asignada para Amazon
        amazon.draw()
        glPopMatrix()

    if truck:
        glBindTexture(GL_TEXTURE_2D, truck_texture)
        truck.set_additional_rotation(0, 90, 0, 1)  # Rotar 180 grados alrededor del eje z
        glPushMatrix()
        glTranslatef(*truck.position)  # Usar la posición asignada para Amazon
        truck.draw()
        glPopMatrix()

    pygame.display.flip()

# Función para dibujar el suelo y las carreteras
def planoText():
    # Activar la textura de césped
    glBindTexture(GL_TEXTURE_2D, grass_texture)
    glEnable(GL_TEXTURE_2D)
    glColor3f(1.0, 1.0, 1.0)  # Asegura que el color no altere la textura

    glBegin(GL_QUADS)
    # Asignar coordenadas de textura con glTexCoord2f
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

    # Carretera vertical (parte de la T)
    glColor3f(0.3, 0.3, 0.3)  # Color gris para la carretera
    glBegin(GL_QUADS)
    glVertex3d(-20, 0.1, -DimBoard)
    glVertex3d(20, 0.1, -DimBoard)
    glVertex3d(20, 0.1, DimBoard)
    glVertex3d(-20, 0.1, DimBoard)
    glEnd()

    # Carretera horizontal (parte superior de la T)
    glColor3f(0.3, 0.3, 0.3)  # Color gris para la carretera
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0.1, DimBoard - 20)
    glVertex3d(DimBoard, 0.1, DimBoard - 20)
    glVertex3d(DimBoard, 0.1, DimBoard)
    glVertex3d(-DimBoard, 0.1, DimBoard)
    glEnd()

def main():
    done = False
    Init()
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    # Ajustar la velocidad de la cámara según el factor de escala
   

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEMOTION:
                process_mouse_motion(event.rel)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:  # Mover hacia adelante
            camera_pos[0] += camera_speed * camera_front[0]
            camera_pos[1] += camera_speed * camera_front[1]
            camera_pos[2] += camera_speed * camera_front[2]
        if keys[pygame.K_s]:  # Mover hacia atrás
            camera_pos[0] -= camera_speed * camera_front[0]
            camera_pos[1] -= camera_speed * camera_front[1]
            camera_pos[2] -= camera_speed * camera_front[2]
        if keys[pygame.K_a]:  # Mover a la izquierda
            right = [
                camera_front[1] * camera_up[2] - camera_front[2] * camera_up[1],
                camera_front[2] * camera_up[0] - camera_front[0] * camera_up[2],
                camera_front[0] * camera_up[1] - camera_front[1] * camera_up[0]
            ]
            camera_pos[0] -= camera_speed * right[0]
            camera_pos[2] -= camera_speed * right[2]
        if keys[pygame.K_d]:  # Mover a la derecha
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
        pygame.time.wait(16)  # Aproximadamente 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
