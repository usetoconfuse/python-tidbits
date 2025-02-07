import math
import pygame
import sys
import random

#constants
BLACK = (0,0,0)
GREY = (40,40,40)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
MAGENTA = (255,0,255)
CYAN = (0,255,255)
PI = math.pi
ACC = 9.81/50

#set up a clock object
clock = pygame.time.Clock()

#variables and arrays
mousedown = False

pointsX = []
pointsY = []
times = []
colours = []

#defining window size and caption
screen = pygame.display.set_mode((1500,1000)) 
pygame.display.set_caption("Physics Tings") 

#FUNCTIONS
#draw a circle
def drawCircle(colour, centre1, centre2, radius):
    pygame.draw.circle(screen, colour, (centre1, centre2), radius)

#assign relevant values to arrays for a particle
def createParticle():
    (x,y) = pygame.mouse.get_pos()
    pointsX.append(x)
    pointsY.append(y)
    times.append(0)
    gen = random.randrange(6)
    if gen == 0: colours.append(RED)
    elif gen == 1: colours.append(BLUE)
    elif gen == 2: colours.append(GREEN)
    elif gen == 3: colours.append(YELLOW)
    elif gen == 4: colours.append(MAGENTA)
    else: colours.append(CYAN)

#main loop
while 1:
    #LOGIC
    #clear screen before drawing, draw floor
    screen.fill(WHITE)
    pygame.draw.rect(screen, GREY, ((-50,850), (2050,850)))

    #create a particle if m1 held
    if mousedown: createParticle()

    #draw circles to screen, update times since created, update positions
    for i in range(0, len(pointsX)):
        drawCircle(colours[i], pointsX[i], pointsY[i], 20)
        times[i] += 1
        pointsY[i] += times[i]*ACC
        if pointsY[i] > 830: pointsY[i] = 830

    #EVENT LOOP
    for event in pygame.event.get():
        if event.type==pygame.QUIT: sys.exit()
        elif event.type==pygame.MOUSEBUTTONDOWN: mousedown = True
        elif event.type==pygame.MOUSEBUTTONUP: mousedown = False

    # update the display 60 times per second
    pygame.display.flip()
    clock.tick(60)