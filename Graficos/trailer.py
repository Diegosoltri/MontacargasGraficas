from OpenGL.GL import *
from OpenGL.GLU import *
from objloader import OBJ

class Trailer:
    def __init__(self, obj_file="Graficos/camion.obj", scale=1.0, position=(0.0, 0.0, 0.0),
                 rotation=(0.0, 0.0, 0.0, 0.0)):
        self.model = OBJ(obj_file)
        self.scale = scale
        self.position = position
        self.rotation = rotation
        self.additional_rotation = (0.0, 0.0, 0.0, 0.0)
        self.display_list = None
        self.create_display_list()

    def create_display_list(self):
        """Crea una lista de visualización que compila las operaciones de dibujo."""
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        self.draw_model()
        glEndList()

    def draw_model(self):
        """Dibuja el modelo aplicando las transformaciones necesarias."""
        glPushMatrix()

        # Aplicar posición fija
        glTranslatef(*self.position)

        # Aplicar rotación inicial
        glRotatef(self.rotation[0], self.rotation[1], self.rotation[2], self.rotation[3])

        # Aplicar rotación adicional
        glRotatef(self.additional_rotation[0], self.additional_rotation[1],
                  self.additional_rotation[2], self.additional_rotation[3])

        # Aplicar escalado
        glScalef(self.scale, self.scale, self.scale)

        # Renderizar el modelo
        self.model.render()

        glPopMatrix()

    def draw(self):
        """Renderiza el tráiler utilizando la lista de visualización."""
        glCallList(self.display_list)

    def set_additional_rotation(self, angle, x, y, z):
        """Define una rotación adicional al cuerpo y actualiza la lista de visualización."""
        self.additional_rotation = (angle, x, y, z)
        self.update_display_list()

    def update_display_list(self):
        """Actualiza la lista de visualización si las transformaciones cambian."""
        if self.display_list:
            glDeleteLists(self.display_list, 1)
        self.create_display_list()