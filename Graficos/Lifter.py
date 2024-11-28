import pygame
from pygame.locals import *
from Cubo import Cubo

# Importar bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from objloader import OBJ
import random
import math

class Lifter:
    def __init__(self, dim, vel, textures, drop_off_point, position=None, direction=None):
        self.dim = dim
        # Usar la posición proporcionada o generar una aleatoria
        if position is not None:
            self.Position = position
        else:
            self.Position = [random.randint(-dim, dim), 6, random.randint(-dim, dim)]
        # Guardar el componente Y original
        self.original_y = self.Position[1]
        # Inicializar la posición anterior para el cálculo de movimiento
        self.previous_position = self.Position.copy()
        # Inicializar la dirección
        if direction is not None:
            self.Direction = direction
        else:
            self.Direction = [0, 0, 1]  # Dirección predeterminada
        # Inicializar la dirección anterior para el cálculo de rotación
        self.previous_direction = self.Direction.copy()
        
        # Ángulos para la rotación
        self.base_angle = 0            # Rotación basada en el movimiento
        self.carrying_angle = 0        # Rotación adicional por carrying_box
        self.carried_box = None        # Basura que se está transportando
        self.target_carrying_angle = 0 # Ángulo objetivo para la rotación por carrying_box

        self.carrying_box = False        # Inicialmente no está cargando una caja
        self.previous_carrying_box = False  # Para detectar cambios en carrying_box
        self.move_count = -1             # Inicializar move_count

        self.vel = vel * 2  # Velocidad de movimiento (no se usa actualmente, ya que el movimiento viene de la API)

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
        self.need_update_display_list = True  # Indicador para actualizar la lista de visualización
        self.create_display_list()

        self.max_rotation_speed = 5  # Velocidad máxima de rotación en grados por actualización

    def create_display_list(self):
        """Crea una lista de visualización para el Lifter."""
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        self.draw_model()
        glEndList()

    def update_display_list(self):
        """Actualiza la lista de visualización si las transformaciones cambian."""
        if self.display_list:
            glDeleteLists(self.display_list, 1)
        self.create_display_list()

    def set_position(self, new_position, move_count, carrying_box, direction=None):
        """
        Actualiza la posición del Lifter y calcula la dirección y rotación
        si la posición ha cambiado. También actualiza el estado de carrying_box.
        """
        # Detectar cambio en carrying_box
        if carrying_box != self.carrying_box:
            if carrying_box:
                # Iniciar rotación al recoger una caja
                self.start_rotation()
            else:
                # Volver a la posición original al dejar la caja
                self.reset_rotation()

        # Actualizar carrying_box
        self.previous_carrying_box = self.carrying_box
        self.carrying_box = carrying_box

        # Guardar la posición anterior
        self.previous_position = self.Position.copy()

        # Mantener Y constante al actualizar la posición
        current_y = self.original_y
        self.Position = [new_position[0], current_y, new_position[2]]

        # Verificar si la posición ha cambiado
        if self.Position != self.previous_position:
            # Guardar la dirección anterior
            self.previous_direction = self.Direction.copy()

            # Si se proporciona una dirección desde la API, usarla
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

            # Actualizar el ángulo de rotación de movimiento
            self.update_rotation()

            self.need_update_display_list = True

        # Actualizar move_count si es necesario
        if move_count != self.move_count:
            self.move_count = move_count

        # Actualizar la lista de visualización si es necesario
        if self.need_update_display_list:
            self.update_display_list()
            self.need_update_display_list = False

    def start_rotation(self):
        """Inicia la rotación del Lifter al recoger una caja."""
        self.target_carrying_angle = 90  # Rotar 90 grados adicionales

    def reset_rotation(self):
        """Restablece la rotación del Lifter al dejar una caja."""
        self.target_carrying_angle = 0  # Volver al ángulo original

    def update(self):
        """Actualiza la rotación del Lifter hacia el ángulo objetivo."""
        # Actualizar self.carrying_angle hacia self.target_carrying_angle
        angle_difference = self.target_carrying_angle - self.carrying_angle
        if abs(angle_difference) > 0.1:
            rotation_step = self.max_rotation_speed
            if abs(angle_difference) < rotation_step:
                rotation_step = abs(angle_difference)
            if angle_difference > 0:
                self.carrying_angle += rotation_step
            else:
                self.carrying_angle -= rotation_step
            self.need_update_display_list = True

    def update_rotation(self):
        """Actualiza self.base_angle basado en la dirección del movimiento."""
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

        # Actualizar el ángulo base del Lifter
        self.base_angle += angle_difference

        # Normalizar el ángulo
        self.base_angle = self.base_angle % 360

    def draw(self):
        """Renderiza el Lifter utilizando la lista de visualización."""
        self.update()
        glCallList(self.display_list)

    def draw_model(self):
        """Dibuja el modelo del Lifter y sus componentes."""
        glPushMatrix()
        # Posicionar el Lifter
        glTranslatef(self.Position[0], self.Position[1] + 5, self.Position[2])
        total_angle = self.base_angle + self.carrying_angle
        glRotatef(total_angle + 90, 0, 1, 0)
        glScaled(0.2, 0.2, 0.2)
        glColor3f(1.0, 1.0, 1.0)

        # Renderizar el modelo .obj
        self.lifter_model.render()

        glPopMatrix()

