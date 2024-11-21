import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import math

from box import BoxModel  # Asegúrate de importar la clase BoxModel

class Basura:
    def __init__(self, dim, vel, textures, txtIndex, texture_id):
        self.dim = dim
        self.Position = [random.randint(-dim, dim), 2, random.randint(-dim, dim)]
        self.alive = True
        # Inicializar el modelo de la caja con la textura
        self.box_model = BoxModel('box.obj', texture_id=texture_id)

    def draw(self):
        if self.alive:
            glPushMatrix()
            glTranslatef(self.Position[0], self.Position[1], self.Position[2])
            glScaled(5, 5, 5)
            self.box_model.draw()
            glPopMatrix()