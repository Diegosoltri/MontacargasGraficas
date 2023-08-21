import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import math


class Cubo:
    def __init__(self, dim, vel):
        # Se inicializa las coordenadas de los vertices del cubo
        self.vertexCoords = [1,1,1,1,1,-1,1,-1,-1,1,-1,1,-1,1,1,-1,1,-1,-1,-1,-1,-1,-1,1,
        ]

        self.elementArray = [
            0,
            1,
            2,
            3,
            0,
            3,
            7,
            4,
            0,
            4,
            5,
            1,
            6,
            2,
            1,
            5,
            6,
            5,
            4,
            7,
            6,
            7,
            3,
            2,
        ]

        self.vertexColors = [
            1,
            1,
            1,
            1,
            0,
            0,
            1,
            1,
            0,
            0,
            1,
            0,
            0,
            0,
            1,
            1,
            0,
            1,
            0,
            0,
            0,
            0,
            1,
            1,
        ]

        self.dim = dim
        # Se inicializa una posicion aleatoria en el tablero
        self.Position = [random.randint(-dim, dim), 2, random.randint(-dim, dim)]
        # Inicializar las coordenadas (x,y,z) del cubo en el tablero
        # almacenandolas en el vector Position
        # ...
        # Se inicializa un vector de direccion aleatorio
        dirX = random.randint(-10, 10) or 1
        dirZ = random.randint(-1, 1) or 1
        magnitude = math.sqrt(dirX * dirX + dirZ * dirZ) * vel
        self.Direction = [dirX / magnitude, 0, dirZ / magnitude]
        # El vector aleatorio debe de estar sobre el plano XZ (la altura en Y debe ser fija)
        # Se normaliza el vector de direccion
        # ...
        # Se cambia la maginitud del vector direccion con la variable vel
        # ...

    def update(self):
        # Se debe de calcular la posible nueva posicion del cubo a partir de su
        # posicion acutual (Position) y el vector de direccion (Direction)
        # ...
        newX = self.Position[0] + self.Direction[0]
        newZ = self.Position[2] + self.Direction[2]
        if newX < -self.dim or newX > self.dim:
            self.Direction[0] *= -1
        else:
            self.Position[0] = newX
        if newZ < -self.dim or newZ > self.dim:
            self.Direction[2] *= -1
        else:
            self.Position[2] = newZ

        # Se debe verificar que el objeto cubo, con su nueva posible direccion
        # no se salga del plano actual (DimBoard)
        # ...

    def draw(self):
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1], self.Position[2])
        glScaled(5, 5, 5)
        # Se dibuja el cubo
        # ...
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertexCoords)
        glColorPointer(3, GL_FLOAT, 0, self.vertexColors)
        glDrawElements(GL_QUADS, 24, GL_UNSIGNED_INT, self.elementArray)
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glPopMatrix()