\
import pygame
from world import World
from config import *
import json
import os


with open("src/data/worldGrid.json", "r") as file:
    worldGrid = json.load(file)

pygame.init()
screen = pygame.display.set_mode((screenw, screenh))
isRunning = True
while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                isRunning = False


    World.drawAerialView(screen, worldGrid, 400, 400)
    pygame.display.flip()
    pygame.time.Clock().tick(60)
pygame.quit()
os.remove(os.path.abspath(__file__))

