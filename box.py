import pywavefront
from OpenGL.GL import *
import pygame

class BoxModel:
    def __init__(self, filename, texture_id=None):
        self.texture_id = texture_id
        # Cargar el modelo usando PyWavefront
        try:
            self.mesh = pywavefront.Wavefront(
                filename, collect_faces=True, create_materials=True)
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            return

        # Crear una lista de visualización (display list) para mejorar el rendimiento
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        self.draw_model()  # Asegúrate de que este método esté definido
        glEndList()

    def draw_model(self):
        # Habilitar texturas si se proporcionó un texture_id
        if self.texture_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
        else:
            glDisable(GL_TEXTURE_2D)

        # Dibujar el modelo cargado desde las mallas en mesh_list
        for mesh in self.mesh.mesh_list:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:  # Usar las caras de la malla
                for vertex_index in face:
                    # Obtener las coordenadas del vértice
                    vertex_coords = self.mesh.vertices[vertex_index]

                    # Manejar coordenadas de textura si están disponibles a nivel de malla
                    if hasattr(mesh, "tex_coords") and vertex_index < len(mesh.tex_coords):
                        tex_coord = mesh.tex_coords[vertex_index]
                        glTexCoord2f(tex_coord[0], tex_coord[1])
                    else:
                        # Coordenadas por defecto si no hay tex_coords
                        glTexCoord2f(0.0, 0.0)

                    # Especificar el vértice
                    glVertex3f(vertex_coords[0], vertex_coords[1], vertex_coords[2])
            glEnd()

        # Deshabilitar texturas después de dibujar
        if self.texture_id is not None:
            glDisable(GL_TEXTURE_2D)

    def draw(self):
        """Llama a la lista de visualización para dibujar el modelo."""
        glCallList(self.display_list)