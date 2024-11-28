from OpenGL.GL import *
from OpenGL.GLU import *
from objloader import OBJ

class Truck:
    def __init__(self, obj_file="Graficos/truck.obj", scale=1.0, position=(0.0, 0.0, 0.0),
                 rotation=(0.0, 0.0, 0.0, 0.0)):
        """
        Inicializa el edificio utilizando un archivo OBJ.
        
        :param obj_file: Ruta al archivo OBJ del modelo del edificio.
        :param scale: Escala del modelo para ajustar su tamaño.
        :param position: Posición fija (x, y, z) del edificio.
        :param rotation: Rotación fija como (ángulo, x, y, z).
        """
        self.model = OBJ(obj_file)  # Cargar el modelo .obj
        self.scale = scale          # Escala para ajustar el tamaño del modelo
        self.position = position    # Posición fija (X, Y, Z)
        self.rotation = rotation    # Rotación fija inicial (ángulo, eje X, Y, Z)
        self.additional_rotation = (0.0, 0.0, 0.0, 0.0)  # Rotación adicional para el cuerpo
        self.display_list = None    # Lista de visualización
        self.create_display_list()  # Crear la lista de visualización

    def create_display_list(self):
        """Crea una lista de visualización que compila las operaciones de dibujo."""
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        self.draw_model()
        glEndList()

    def update_display_list(self):
        """Actualiza la lista de visualización si las transformaciones cambian."""
        if self.display_list:
            glDeleteLists(self.display_list, 1)
        self.create_display_list()

    def draw_model(self):
        """Dibuja el modelo del edificio aplicando las transformaciones."""
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
        """Renderiza el edificio utilizando la lista de visualización."""
        glCallList(self.display_list)

    def set_position(self, position):
        """Establece una nueva posición y actualiza la lista de visualización."""
        self.position = position
        self.update_display_list()

    def set_rotation(self, rotation):
        """Establece una nueva rotación y actualiza la lista de visualización."""
        self.rotation = rotation
        self.update_display_list()

    def set_scale(self, scale):
        """Establece una nueva escala y actualiza la lista de visualización."""
        self.scale = scale
        self.update_display_list()

    def set_additional_rotation(self, angle, x, y, z):
        """Define una rotación adicional al cuerpo y actualiza la lista de visualización."""
        self.additional_rotation = (angle, x, y, z)
        self.update_display_list()

    def free(self):
        """Libera la lista de visualización y otros recursos."""
        if self.display_list:
            glDeleteLists(self.display_list, 1)
        self.model.free()