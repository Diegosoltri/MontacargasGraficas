import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math
import random
# Se carga el archivo de la clase Cubo
import sys
sys.path.append('..')
from Lifter import Lifter
from Basura import Basura

import requests
import json

URL_BASE = "http://localhost:5000"
r = requests.post(URL_BASE+ "/games", allow_redirects=False)
LOCATION = r.headers["Location"]

garbageCells = json.loads(r.headers["garbageCells"])
McenterRobots = json.loads(r.headers["centerRobots"])
McornerRobots = json.loads(r.headers["cornerRobots"])

screen_width = 500
screen_height = 500
#vc para el obser.
FOVY=60.0
ZNEAR=0.01
ZFAR=5000.0
#Variables para definir la posicion del observador
#gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
EYE_X=0.0
EYE_Y=200.0
EYE_Z=0.01
CENTER_X=0
CENTER_Y=0
CENTER_Z=0
UP_X=0
UP_Y=1
UP_Z=0
#Variables para dibujar los ejes del sistema
X_MIN=-500
X_MAX=500
Y_MIN=-500
Y_MAX=500
Z_MIN=-500
Z_MAX=500
#Dimension del plano
DimBoard = 210//2

centerCoords = []
cornerCoords = []

# Se guardan las posiciones iniciales de los robots
for r in McenterRobots:
    x,z = r['x']*10 - DimBoard, r['z']*10 - DimBoard
    centerCoords.append((x,z))
    
for r in McornerRobots:
    x,z = r['x']*10 - DimBoard, r['z']*10 - DimBoard
    cornerCoords.append((x,z))

# Arreglos para almacenar los robots
rCorner = []
rCenter = []

basuras = []
nbasuras = len(garbageCells)
print(nbasuras)

# Variables para el control del observador
theta = 0.0

# Arreglo para el manejo de texturas
textures = []
filenames = ["img1.bmp","wheel.jpeg", "walle.jpeg","basura.bmp"]

def Axis():
    glShadeModel(GL_FLAT)
    glLineWidth(3.0)
    #X axis in red
    glColor3f(1.0,0.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(X_MIN,0.0,0.0)
    glVertex3f(X_MAX,0.0,0.0)
    glEnd()
    #Y axis in green
    glColor3f(0.0,1.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,Y_MIN,0.0)
    glVertex3f(0.0,Y_MAX,0.0)
    glEnd()
    #Z axis in blue
    glColor3f(0.0,0.0,1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,0.0,Z_MIN)
    glVertex3f(0.0,0.0,Z_MAX)
    glEnd()
    glLineWidth(1.0)

def Texturas(filepath):
    textures.append(glGenTextures(1))
    id = len(textures) - 1
    glBindTexture(GL_TEXTURE_2D, textures[id])
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    image = pygame.image.load(filepath).convert()
    w, h = image.get_rect().size
    image_data = pygame.image.tostring(image, "RGBA")
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    
def Init():
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: cubos")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width/screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
    glClearColor(0,0,0,0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    for i in filenames:
        Texturas(i)
    xtra = 10

    for i in range(4):
        rCorner.append(Lifter(DimBoard, 1, textures, i, cornerCoords[i]))
        
    for i in range(2):
        rCenter.append(Lifter(DimBoard, 1, textures, i, centerCoords[i]))
        
        
    for i in range(nbasuras):
        basuras.append(Basura(DimBoard,1,textures,3, (garbageCells[i]['x']*10 - DimBoard, garbageCells[i]['z']*10 - DimBoard)))
        
def planoText():
    # activate textures
    glColor(1.0, 1.0, 1.0)
    #glEnable(GL_TEXTURE_2D)
    # front face
    #glBindTexture(GL_TEXTURE_2D, textures[0])  # Use the first texture
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, -DimBoard)
    
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, 0, DimBoard)
    
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, 0, DimBoard)
    
    glTexCoord2f(1.0, 0.0)
    glVertex3d(DimBoard, 0, -DimBoard)
    
    glEnd()
    # glDisable(GL_TEXTURE_2D)
    
def drawWalls():
    # Draw the walls bounding the plane
    wall_height = 50.0  # Adjust the wall height as needed
    
    glColor3f(0.8, 0.8, 0.8)  # Light gray color for walls
    # Draw the left wall
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glVertex3d(-DimBoard, 0, DimBoard)
    glVertex3d(-DimBoard, wall_height, DimBoard)
    glVertex3d(-DimBoard, wall_height, -DimBoard)
    glEnd()
    
    # Draw the right wall
    glBegin(GL_QUADS)
    glVertex3d(DimBoard, 0, -DimBoard)
    glVertex3d(DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, wall_height, DimBoard)
    glVertex3d(DimBoard, wall_height, -DimBoard)
    glEnd()
    
    # Draw the front wall
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, wall_height, DimBoard)
    glVertex3d(-DimBoard, wall_height, DimBoard)
    glEnd()
    
    # Draw the back wall
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glVertex3d(DimBoard, 0, -DimBoard)
    glVertex3d(DimBoard, wall_height, -DimBoard)
    glVertex3d(-DimBoard, wall_height, -DimBoard)
    glEnd()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    r = requests.get(URL_BASE+LOCATION)
    McenterRobots = json.loads(r.headers["centerRobots"])
    McornerRobots = json.loads(r.headers["cornerRobots"])
    incinerator = json.loads(r.headers["incinerator"])
    garbageCells = json.loads(r.headers["garbageCells"])
    
    # Se dibuja cubos
    # print("\T----CORNER ROBOTS----")
    for i in range(4):
        rCorner[i].draw()
        sect = McornerRobots[i]['section']
        
        rCorner[i].update(McornerRobots[i]['x']*10 - DimBoard, McornerRobots[i]['z']*10 - DimBoard, McornerRobots[i]['loaded'])
        # print("Section:", sect)    
        # print("\tMesa pos:", McornerRobots[i]['x'],McornerRobots[i]['z'])  
        # print("\tOpenGL pos:", McornerRobots[i]['x']*10 - DimBoard, McornerRobots[i]['z']*10 - DimBoard)
        # print()
        
    # print("\T----CENTER ROBOTS----")
    for i in range(2):
        rCenter[i].draw()
        sect = McenterRobots[i]['section']
        
        rCenter[i].update(McenterRobots[i]['x']*10 - DimBoard, McenterRobots[i]['z']*10 - DimBoard, McornerRobots[i]['loaded'])
        # print("Section:", sect)    
        # print("\tMesa pos:", McenterRobots[i]['x'],McenterRobots[i]['z'])  
        # print("\tOpenGL pos:", McenterRobots[i]['x']*10 - DimBoard, McenterRobots[i]['z']*10 - DimBoard)
        # print()
        
    # Draw the orange square on the XZ plane
    on = 0.0 if incinerator[0]['on:'] else 0.5
    glColor3f(1.0, on, 0.0)  # Orange color
    square_size = 10.0  # Adjust the square size as needed

    half_size = square_size / 2.0
    glBegin(GL_QUADS)
    glVertex3d(-half_size, 0.5, -half_size)
    glVertex3d(-half_size, 0.5, half_size)
    glVertex3d(half_size, 0.5, half_size)
    glVertex3d(half_size, 0.5, -half_size)
    glEnd()
    
    Axis()
    
    #Se dibujan basuras
    for obj in basuras:
        obj.draw()
        #obj.update()    
    
    #Se dibuja el plano gris
    planoText()
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glVertex3d(-DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, -DimBoard)
    glEnd()
    
    #drawWalls()
    
    
    
def lookAt():
    glLoadIdentity()
    rad = theta * math.pi / 180
    newX = EYE_X * math.cos(rad) + EYE_Z * math.sin(rad)
    newZ = -EYE_X * math.sin(rad) + EYE_Z * math.cos(rad)
    gluLookAt(newX,EYE_Y,newZ,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
    
done = False
Init()
while not done:
    keys = pygame.key.get_pressed()  # Checking pressed keys
    if keys[pygame.K_RIGHT]:
        if theta > 359.0:
            theta = 0
        else:
            theta += 1.0
        lookAt()
    if keys[pygame.K_LEFT]:
        if theta < 1.0:
            theta = 360.0
        else:
            theta -= 1.0
        lookAt()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
        if event.type == pygame.QUIT:
            done = True
    display()

    display()
    pygame.display.flip()
    pygame.time.wait(10)
pygame.quit()