import pygame
from pygame.locals import *
from Cubo import Cubo

# Load OpenGL libraries
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from objloader import OBJ
import random
import math

class Lifter:
    def __init__(self, dim, vel, textures, drop_off_point, position=None, direction=None):
        self.dim = dim
        # Use the provided position or generate a random one
        if position is not None:
            self.Position = position
        else:
            self.Position = [random.randint(-dim, dim), 6, random.randint(-dim, dim)]
        # Use the provided direction or generate a random one
        if direction is not None:
            self.Direction = direction
        else:
            dirX = random.randint(-10, 10) or 1
            dirZ = random.randint(-10, 10) or 1
            magnitude = math.sqrt(dirX**2 + dirZ**2)
            self.Direction = [(dirX / magnitude), 0, (dirZ / magnitude)]
        self.previous_direction = self.Direction.copy()
        self.angle = 0

        # Increase movement speed
        self.vel = vel * 2  # Multiplicamos por 2 para hacerlo más rápido

        self.textures = textures
        self.platformHeight = -1.5
        self.platformUp = False
        self.platformDown = False
        self.radiusCol = 5
        self.status = 0
        self.trashID = -1
        self.drop_off_point = drop_off_point
        self.lifter_model = OBJ('tinker.obj')
        self.display_list = None
        self.need_update_display_list = True  # Indicator to update the display list
        self.create_display_list()

        # Increase maximum rotation speed
        self.max_rotation_speed = 100  # Incrementamos a 15 grados por frame

    def create_display_list(self):
        """Creates a display list for the Lifter."""
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        self.draw_model()
        glEndList()

    def update_display_list(self):
        """Updates the display list if transformations change."""
        if self.display_list:
            glDeleteLists(self.display_list, 1)
        self.create_display_list()

    def search(self):
        dirX = random.randint(-10, 10) or 1
        dirZ = random.randint(-10, 10) or 1
        magnitude = math.sqrt(dirX**2 + dirZ**2)
        self.Direction = [(dirX / magnitude), 0, (dirZ / magnitude)]
        self.need_update_display_list = True

    def targetDropOff(self):
        dirX = self.drop_off_point[0] - self.Position[0]
        dirZ = self.drop_off_point[1] - self.Position[2]
        magnitude = math.sqrt(dirX**2 + dirZ**2)
        self.Direction = [(dirX / magnitude), 0, (dirZ / magnitude)]
        self.need_update_display_list = True

    def update(self):
        # Save the previous direction
        self.previous_direction = self.Direction.copy()

        # Move the lifter in its current direction
        self.Position[0] += self.Direction[0] * self.vel
        self.Position[2] += self.Direction[2] * self.vel

        # Boundary checks and direction changes
        if abs(self.Position[0]) > self.dim:
            self.Direction[0] *= -1
            self.Position[0] = max(min(self.Position[0], self.dim), -self.dim)
        if abs(self.Position[2]) > self.dim:
            self.Direction[2] *= -1
            self.Position[2] = max(min(self.Position[2], self.dim), -self.dim)

        # Randomly change direction occasionally
        if random.randint(1, 50) == 1:
            self.search()

        # Calculate the rotation angle using atan2
        dx = self.Direction[0]
        dz = self.Direction[2]
        angle_current = math.degrees(math.atan2(-dz, dx))

        dx_prev = self.previous_direction[0]
        dz_prev = self.previous_direction[2]
        angle_previous = math.degrees(math.atan2(-dz_prev, dx_prev))

        # Calculate the angle difference
        angle_difference = angle_current - angle_previous

        # Adjust the angle difference to be between -180 and 180
        if angle_difference > 180:
            angle_difference -= 360
        elif angle_difference < -180:
            angle_difference += 360

        # Limit the maximum rotation per update
        if angle_difference > self.max_rotation_speed:
            angle_difference = self.max_rotation_speed
        elif angle_difference < -self.max_rotation_speed:
            angle_difference = -self.max_rotation_speed

        # Update the total angle of the lifter
        self.angle += angle_difference

        # Normalize the angle
        self.angle = self.angle % 360

        self.need_update_display_list = True

        # Update the display list if necessary
        if self.need_update_display_list:
            self.update_display_list()
            self.need_update_display_list = False

    def draw(self):
        """Renders the Lifter using the display list."""
        glCallList(self.display_list)

    def draw_model(self):
        """Draws the Lifter model and its components."""
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1] + 15, self.Position[2])
        glRotatef(self.angle, 0, 1, 0)
        glScaled(0.5, 0.5, 0.5)
        glColor3f(1.0, 1.0, 1.0)

        # Render the .obj model
        self.lifter_model.render() 

        # Lifting platform
        glPushMatrix()
        if self.status in [1, 2, 3]:
            self.drawTrash()
        glColor3f(0.0, 0.0, 0.0)
        glTranslatef(0, self.platformHeight, 0)  # Move up and down
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

        # Front face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-1, -1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, -1, 1)

        # Back face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-1, 1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, -1, -1)

        # Left face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-1, 1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-1, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-1, -1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, -1, 1)

        # Right face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, -1, -1)

        # Top face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-1, 1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, 1, -1)

        # Bottom face
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