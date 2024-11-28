import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *

class Basura:
    def __init__(self, position, textures, txtIndex, size, offset_x=0, offset_y=0, offset_z=0):
        self.Position = position
        self.textures = textures
        self.txtIndex = txtIndex
        self.size = size
        self.alive = True
        self.carried = False      # Indica si está siendo transportada
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.offset_z = offset_z

    def draw(self):
        """
        Renderiza la basura en su posición actual con su tamaño y textura.
        Si está siendo transportada, se dibujará en relación al montacargas.
        """
        if self.alive:
            glPushMatrix()
            # Trasladar a la posición de la basura.
            glTranslatef(self.Position[0]+ 20, self.Position[1], self.Position[2])

            # Escalar para reflejar el tamaño de la basura.
            glScalef(self.size[0] / 10.0, self.size[1] / 10.0, self.size[2] / 10.0)
            glColor3f(1.0, 1.0, 1.0)

            # Aplicar la textura correspondiente.
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textures[self.txtIndex])

            # Dibujar el cubo texturizado.
            glBegin(GL_QUADS)
            
            # Cara frontal.
            glTexCoord2f(0.0, 0.0)
            glVertex3d(1, 1, 1)
            glTexCoord2f(1.0, 0.0)
            glVertex3d(-1, 1, 1)
            glTexCoord2f(1.0, 1.0)
            glVertex3d(-1, -1, 1)
            glTexCoord2f(0.0, 1.0)
            glVertex3d(1, -1, 1)

            # Cara trasera.
            glTexCoord2f(0.0, 0.0)
            glVertex3d(-1, 1, -1)
            glTexCoord2f(1.0, 0.0)
            glVertex3d(1, 1, -1)
            glTexCoord2f(1.0, 1.0)
            glVertex3d(1, -1, -1)
            glTexCoord2f(0.0, 1.0)
            glVertex3d(-1, -1, -1)

            # Cara izquierda.
            glTexCoord2f(0.0, 0.0)
            glVertex3d(-1, 1, 1)
            glTexCoord2f(1.0, 0.0)
            glVertex3d(-1, 1, -1)
            glTexCoord2f(1.0, 1.0)
            glVertex3d(-1, -1, -1)
            glTexCoord2f(0.0, 1.0)
            glVertex3d(-1, -1, 1)

            # Cara derecha.
            glTexCoord2f(0.0, 0.0)
            glVertex3d(1, 1, -1)
            glTexCoord2f(1.0, 0.0)
            glVertex3d(1, 1, 1)
            glTexCoord2f(1.0, 1.0)
            glVertex3d(1, -1, 1)
            glTexCoord2f(0.0, 1.0)
            glVertex3d(1, -1, -1)

            # Cara superior.
            glTexCoord2f(0.0, 0.0)
            glVertex3d(-1, 1, 1)
            glTexCoord2f(1.0, 0.0)
            glVertex3d(1, 1, 1)
            glTexCoord2f(1.0, 1.0)
            glVertex3d(1, 1, -1)
            glTexCoord2f(0.0, 1.0)
            glVertex3d(-1, 1, -1)

            # Cara inferior.
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