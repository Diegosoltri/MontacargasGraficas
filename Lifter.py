import pygame
from pygame.locals import *
from Cubo import Cubo

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from objloader import OBJ
import random
import math

class Lifter:
    def __init__(self, dim, vel, textures, drop_off_point):
        self.dim = dim
        # Se inicializa una posición aleatoria en el tablero
        self.Position = [random.randint(-dim, dim), 6, random.randint(-dim, dim)]
        # Inicializar las coordenadas (x,y,z) del cubo en el tablero
        # almacenándolas en el vector Position

        # Se inicializa un vector de dirección aleatorio
        dirX = random.randint(-10, 10) or 1
        dirZ = random.randint(-10, 10) or 1
        magnitude = math.sqrt(dirX**2 + dirZ**2)
        self.Direction = [(dirX / magnitude), 0, (dirZ / magnitude)]
        self.angle = 0
        self.vel = vel
        # El vector aleatorio debe de estar sobre el plano XZ (la altura en Y debe ser fija)
        # Se normaliza el vector de dirección

        # Arreglo de texturas
        self.textures = textures

        # Control variables for platform movement
        self.platformHeight = -1.5
        self.platformUp = False
        self.platformDown = False

        # Control variable for collisions
        self.radiusCol = 5

        # Control variables for animations
        self.status = 0
        self.trashID = -1
        # 0 = buscando
        # 1 = levantando
        # 2 = entregando
        # 3 = soltando
        # 4 = regresando

        # Nueva posición de entrega
        self.drop_off_point = drop_off_point
        self.lifter_model = OBJ('tinker.obj')

    def search(self):
        # Cambiar dirección a una aleatoria
        dirX = random.randint(-10, 10) or 1
        dirZ = random.randint(-10, 10) or 1
        magnitude = math.sqrt(dirX**2 + dirZ**2)
        self.Direction = [(dirX / magnitude), 0, (dirZ / magnitude)]

    def targetDropOff(self):
        # Establecer dirección hacia la posición de entrega
        dirX = self.drop_off_point[0] - self.Position[0]
        dirZ = self.drop_off_point[1] - self.Position[2]
        magnitude = math.sqrt(dirX**2 + dirZ**2)
        self.Direction = [(dirX / magnitude), 0, (dirZ / magnitude)]

    def update(self):
        if self.status == 1:
            delta = 0.01
            if self.platformHeight >= 0:
                self.targetDropOff()
                self.status = 2
            else:
                self.platformHeight += delta
        elif self.status == 2:
            # Verificar si el robot ha llegado a la posición de entrega
            dx = self.Position[0] - self.drop_off_point[0]
            dz = self.Position[2] - self.drop_off_point[1]
            distance_to_drop_off = math.sqrt(dx * dx + dz * dz)
            if distance_to_drop_off <= 10:
                self.status = 3
            else:
                # Mover hacia la posición de entrega
                newX = self.Position[0] + self.Direction[0] * self.vel
                newZ = self.Position[2] + self.Direction[2] * self.vel
                # Verificar límites del tablero
                if newX - 10 < -self.dim or newX + 10 > self.dim:
                    self.Direction[0] *= -1
                else:
                    self.Position[0] = newX
                if newZ - 10 < -self.dim or newZ + 10 > self.dim:
                    self.Direction[2] *= -1
                else:
                    self.Position[2] = newZ
                # Actualizar el ángulo de rotación
                self.angle = math.acos(self.Direction[0]) * 180 / math.pi
                if self.Direction[2] > 0:
                    self.angle = 360 - self.angle
        elif self.status == 3:
            delta = 0.01
            if self.platformHeight <= -1.5:
                self.status = 4
            else:
                self.platformHeight -= delta
        elif self.status == 4:
            # Regresar al estado de búsqueda
            dx = self.Position[0] - self.drop_off_point[0]
            dz = self.Position[2] - self.drop_off_point[1]
            distance_to_drop_off = math.sqrt(dx * dx + dz * dz)
            if distance_to_drop_off > 20:
                self.search()
                self.status = 0
            else:
                self.Position[0] -= (self.Direction[0] * (self.vel / 4))
                self.Position[2] -= (self.Direction[2] * (self.vel / 4))
        else:
            # Actualizar posición
            if random.randint(1, 1000) == 69:
                self.search()
            newX = self.Position[0] + self.Direction[0] * self.vel
            newZ = self.Position[2] + self.Direction[2] * self.vel
            if newX - 10 < -self.dim or newX + 10 > self.dim:
                self.Direction[0] *= -1
            else:
                self.Position[0] = newX
            if newZ - 10 < -self.dim or newZ + 10 > self.dim:
                self.Direction[2] *= -1
            else:
                self.Position[2] = newZ
            self.angle = math.acos(self.Direction[0]) * 180 / math.pi
            if self.Direction[2] > 0:
                self.angle = 360 - self.angle

            # Mover plataforma (opcional, si quieres animar la plataforma)
            delta = 0.01
            if self.platformUp:
                if self.platformHeight >= 0:
                    self.platformUp = False
                else:
                    self.platformHeight += delta
            elif self.platformDown:
                if self.platformHeight <= -1.5:
                    self.platformUp = True
                else:
                    self.platformHeight -= delta

    def draw(self):
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1] + 15, self.Position[2])
        glRotatef(self.angle, 0, 1, 0)
        glScaled(0.5, 0.5, 0.5)
        glColor3f(1.0, 1.0, 1.0)

        # Renderizar el modelo .obj
        self.lifter_model.render() 
             
        # Plataforma elevadora
        glPushMatrix()
        if self.status in [1, 2, 3]:
            self.drawTrash()
        glColor3f(0.0, 0.0, 0.0)
        glTranslatef(0, self.platformHeight, 0)  # Arriba y abajo
        glBegin(GL_QUADS)
        glVertex3d(1, 1, 1)
        glVertex3d(1, 1, -1)
        glVertex3d(3, 1, -1)
        glVertex3d(3, 1, 1)
        glEnd()
        glPopMatrix()
        glPopMatrix()

    def drawTrash(self):
        glPushMatrix()
        glTranslatef(2, (self.platformHeight + 1.5), 0)
        glScaled(0.5, 0.5, 0.5)
        glColor3f(1.0, 1.0, 1.0)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[3])

        glBegin(GL_QUADS)

        # Cara frontal
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-1, -1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, -1, 1)

        # Cara posterior
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-1, 1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, -1, -1)

        # Cara lateral izquierda
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-1, 1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-1, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-1, -1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, -1, 1)

        # Cara lateral derecha
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, -1, -1)

        # Cara superior
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-1, 1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, 1, -1)

        # Cara inferior
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-1, -1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, -1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, -1, -1)

        glEnd()
        glDisable(GL_TEXTURE_2D)

        glPopMatrix()