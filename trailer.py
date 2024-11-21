from OpenGL.GL import *
from OpenGL.GLU import *
from objloader import OBJ

class Trailer:
    def __init__(self, obj_file="camion.obj", scale=1.0, position=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0, 0.0)):
        """
        Inicializa el tráiler utilizando un archivo OBJ.
        
        :param obj_file: Ruta al archivo OBJ del modelo del tráiler.
        :param scale: Escala del modelo para ajustar su tamaño.
        :param position: Posición fija (x, y, z) del tráiler.
        :param rotation: Rotación fija como (ángulo, x, y, z).
        """
        self.model = OBJ(obj_file)  # Cargar el modelo .obj
        self.scale = scale          # Escala para ajustar el tamaño del modelo
        self.position = position    # Posición fija (X, Y, Z)
        self.rotation = rotation    # Rotación fija inicial (ángulo, eje X, Y, Z)
        self.additional_rotation = (0.0, 0.0, 0.0, 0.0)  # Rotación adicional para el cuerpo

    def set_additional_rotation(self, angle, x, y, z):
        """Define una rotación adicional al cuerpo."""
        self.additional_rotation = (angle, x, y, z)

    def draw(self):
        """
        Renderiza el tráiler en la posición, rotación inicial y rotación adicional.
        """
        glPushMatrix()

        # Aplicar posición fija
        glTranslatef(*self.position)

        # Aplicar rotación inicial
        glRotatef(self.rotation[0], self.rotation[1], self.rotation[2], self.rotation[3])

        # Aplicar rotación adicional
        glRotatef(self.additional_rotation[0], self.additional_rotation[1], self.additional_rotation[2], self.additional_rotation[3])

        # Aplicar escalado
        glScalef(self.scale, self.scale, self.scale)

        # Renderizar el modelo
        self.model.render()

        glPopMatrix()