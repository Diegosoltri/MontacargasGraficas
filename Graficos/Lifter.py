import pygame
from pygame.locals import *
from Cubo import Cubo

# Load OpenGL libraries
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from objloader import OBJ
import random
import math

class Lifter:
    def __init__(self, dim, vel, textures, drop_off_point, position=None, direction=None):
        self.dim = dim
        # Use the provided position or generate a random one
        if position is not None:
            self.Position = position
        else:
            self.Position = [random.randint(-dim, dim), 6, random.randint(-dim, dim)]
        # Initialize previous position for movement calculation
        self.previous_position = self.Position.copy()
        # Initialize Direction
        if direction is not None:
            self.Direction = direction
        else:
            self.Direction = [0, 0, 1]  # Default direction
        # Initialize previous direction for rotation calculation
        self.previous_direction = self.Direction.copy()
        self.angle = 0

        self.carrying_box = False  # Inicialmente no está cargando una caja
        self.move_count = -1  # Inicializar move_count

        self.vel = vel * 2  # Movement speed (not used now since movement comes from API)

        self.textures = textures
        self.platformHeight = -1.5
        self.platformUp = False
        self.platformDown = False
        self.radiusCol = 5
        self.status = 0
        self.trashID = -1
        self.drop_off_point = drop_off_point
        self.lifter_model = OBJ('Graficos/tinker.obj')
        self.display_list = None
        self.need_update_display_list = True  # Indicator to update the display list
        self.create_display_list()

        self.max_rotation_speed = 10  # Maximum rotation speed in degrees per update

    def create_display_list(self):
        """Creates a display list for the Lifter."""
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        self.draw_model()
        glEndList()

    def update_display_list(self):
        """Updates the display list if transformations change."""
        if self.display_list:
            glDeleteLists(self.display_list, 1)
        self.create_display_list()

    def set_position(self, new_position, move_count, carrying_box, direction=None):
        """
        Actualiza la posición del Lifter y calcula la dirección y rotación
        si la posición ha cambiado. También actualiza el estado de carrying_box.
        """
        # Actualizar carrying_box
        self.carrying_box = carrying_box

        # Guardar la posición anterior
        self.previous_position = self.Position.copy()

        # Actualizar posición
        self.Position = new_position

        # Verificar si la posición ha cambiado
        if self.Position != self.previous_position:
            # Guardar la dirección anterior
            self.previous_direction = self.Direction.copy()

            # Si se proporciona una dirección desde la API, úsala
            if direction is not None:
                self.Direction = direction
            else:
                # Calcular el vector de movimiento
                movement = [
                    self.Position[0] - self.previous_position[0],
                    self.Position[1] - self.previous_position[1],
                    self.Position[2] - self.previous_position[2]
                ]

                # Calcular la nueva dirección basada en el movimiento
                magnitude = math.sqrt(sum(m**2 for m in movement))
                if magnitude != 0:
                    self.Direction = [m / magnitude for m in movement]
                else:
                    # Sin movimiento; mantener la dirección anterior
                    self.Direction = self.previous_direction

            # Actualizar el ángulo de rotación
            self.update_rotation()

            self.need_update_display_list = True

        # Actualizar la lista de visualización si es necesario
        if self.need_update_display_list:
            self.update_display_list()
            self.need_update_display_list = False

    def update_rotation(self):
        # Calcular el ángulo de rotación usando atan2 en el plano XZ
        dx = self.Direction[0]
        dz = self.Direction[2]
        angle_current = math.degrees(math.atan2(-dz, dx))

        dx_prev = self.previous_direction[0]
        dz_prev = self.previous_direction[2]
        angle_previous = math.degrees(math.atan2(-dz_prev, dx_prev))

        # Calcular la diferencia de ángulo
        angle_difference = angle_current - angle_previous

        # Ajustar la diferencia de ángulo para que esté entre -180 y 180
        if angle_difference > 180:
            angle_difference -= 360
        elif angle_difference < -180:
            angle_difference += 360

        # Limitar la rotación máxima por actualización
        if angle_difference > self.max_rotation_speed:
            angle_difference = self.max_rotation_speed
        elif angle_difference < -self.max_rotation_speed:
            angle_difference = -self.max_rotation_speed

        # Actualizar el ángulo total del Lifter
        self.angle += angle_difference

        # Normalizar el ángulo
        self.angle = self.angle % 360

    def draw(self):
        """Renders the Lifter using the display list."""
        glCallList(self.display_list)

    def draw_model(self):
        """Dibuja el modelo del Lifter y sus componentes."""
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1] + 15, self.Position[2])
        glRotatef(self.angle + 90, 0, 1, 0)
        glScaled(0.2, 0.2, 0.2)
        glColor3f(1.0, 1.0, 1.0)

        # Renderizar el modelo .obj
        self.lifter_model.render() 

        # Dibujar la caja si está cargando una
        if self.carrying_box:
            self.drawTrash()

        glPopMatrix()

    def drawTrash(self):
        glPushMatrix()
        glTranslatef(0, self.lifter_model, 0)
        glRotatef(270, 1, 0, 0) # Rotar la caja para que esté en la dirección correcta
        glScaled(0.5, 0.5, 0.5)
        glColor3f(1.0, 1.0, 1.0)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[3])

        glBegin(GL_QUADS)

        # (Define the faces of the cube with texture coordinates, as in your code)

        glEnd()
        glDisable(GL_TEXTURE_2D)

        glPopMatrix()