from OpenGL.GL import *
from OpenGL.GLU import *

class Trailer:
    def __init__(self, scale=1.0, position=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0, 1.0), 
                 color=(1.0, 0.0, 0.0, 0.5), width=3.0, height=1.5, depth=7.0):
        """
        Inicializa el tráiler representado como un prisma rectangular.

        :param scale: Escala del tráiler.
        :param position: Posición del tráiler en el espacio.
        :param rotation: Tupla de rotación (ángulo, x, y, z).
        :param color: Color del tráiler con transparencia (RGBA).
        :param width: Ancho del tráiler.
        :param height: Alto del tráiler.
        :param depth: Profundidad del tráiler.
        """
        self.scale = scale
        self.position = position
        self.rotation = rotation
        self.additional_rotation = (0.0, 0.0, 0.0, 1.0)
        self.color = color
        self.width = width
        self.height = height
        self.depth = depth

    def draw_model(self):
        """Dibuja el tráiler aplicando las transformaciones necesarias."""
        glPushMatrix()

        # Aplicar posición
        glTranslatef(self.position[0]+ 20, self.position[1], self.position[2])

        # Aplicar rotación inicial
        glRotatef(self.rotation[0], self.rotation[1], self.rotation[2], self.rotation[3])

        # Aplicar rotación adicional
        glRotatef(self.additional_rotation[0], self.additional_rotation[1],
                  self.additional_rotation[2], self.additional_rotation[3])

        # Aplicar escalado
        glScalef(self.scale, self.scale, self.scale)

        # Configurar el color con transparencia
        glColor4f(*self.color)

        # Dibujar un prisma rectangular (6 caras con diferentes dimensiones)
        glBegin(GL_QUADS)

        # Front Face
        glVertex3f(-self.width / 2, -self.height / 2, self.depth / 2)
        glVertex3f(self.width / 2, -self.height / 2, self.depth / 2)
        glVertex3f(self.width / 2, self.height / 2, self.depth / 2)
        glVertex3f(-self.width / 2, self.height / 2, self.depth / 2)

        # Back Face
        glVertex3f(-self.width / 2, -self.height / 2, -self.depth / 2)
        glVertex3f(-self.width / 2, self.height / 2, -self.depth / 2)
        glVertex3f(self.width / 2, self.height / 2, -self.depth / 2)
        glVertex3f(self.width / 2, -self.height / 2, -self.depth / 2)

        # Left Face
        glVertex3f(-self.width / 2, -self.height / 2, -self.depth / 2)
        glVertex3f(-self.width / 2, -self.height / 2, self.depth / 2)
        glVertex3f(-self.width / 2, self.height / 2, self.depth / 2)
        glVertex3f(-self.width / 2, self.height / 2, -self.depth / 2)

        # Right Face
        glVertex3f(self.width / 2, -self.height / 2, self.depth / 2)
        glVertex3f(self.width / 2, -self.height / 2, -self.depth / 2)
        glVertex3f(self.width / 2, self.height / 2, -self.depth / 2)
        glVertex3f(self.width / 2, self.height / 2, self.depth / 2)

        # Top Face
        glVertex3f(-self.width / 2, self.height / 2, self.depth / 2)
        glVertex3f(self.width / 2, self.height / 2, self.depth / 2)
        glVertex3f(self.width / 2, self.height / 2, -self.depth / 2)
        glVertex3f(-self.width / 2, self.height / 2, -self.depth / 2)

        # Bottom Face
        glVertex3f(-self.width / 2, -self.height / 2, -self.depth / 2)
        glVertex3f(self.width / 2, -self.height / 2, -self.depth / 2)
        glVertex3f(self.width / 2, -self.height / 2, self.depth / 2)
        glVertex3f(-self.width / 2, -self.height / 2, self.depth / 2)

        glEnd()

        glPopMatrix()

    def draw(self):
        """Renderiza el tráiler."""
        self.draw_model()

    def set_additional_rotation(self, angle, x, y, z):
        """Define una rotación adicional y actualiza el modelo."""
        self.additional_rotation = (angle, x, y, z)