import pygame
import random
import time
import os
 

from animal import *
from inputmanager import InputManager
from ui import AnimalInspector
from world import World

from config import *



pygame.init()

class Test:
    def __init__(self):
        self.screenw, self.screenh = SCREEN_W, SCREEN_H
        self.screen = pygame.display.set_mode((self.screenw, self.screenh), pygame.SCALED) 
        
        self.mapRowLen = MAP_ROW_LEN
        self.mapData = [[random.randint(0, 1) for c in range(self.mapRowLen)] for row in range(self.mapRowLen)]
        
        
        self.backgroundStartingX = 350
        self.backgroundStartingY = 200
        self.scale = 1
        self.backgroundAssetsDict = self.loadBackgroundAssets()
        self.backGroundSurface = self.createBackGroundSurface()

        self.clock = pygame.time.Clock()
        self.fps = 60

        self.selectedAnimal = None
        self.inspector = AnimalInspector(None)


    def createBackGroundSurface(self) -> pygame.Surface:
        backgroundSurface = pygame.Surface((800, 800))
        for y, row in enumerate(self.mapData):
            for x in range(len(row)):
                backgroundSurface.blit(self.backgroundAssetsDict["dark_grass_dirt.png"], (BACKGROUND_STARTING_X + x * 15 * SCALE -y *15 * SCALE, BACKGROUND_STARTING_Y + x * 8 * SCALE +y* 8 * SCALE))
                pass
        return backgroundSurface

    def loadBackgroundAssets(self) -> dict:
        assetsDict = {}
        currentDir = os.path.dirname(os.path.abspath(__file__))
        assetsDir = os.path.join(currentDir, "assets", "isometric Environment", "Tiles")
        for image in os.listdir(assetsDir):
            tempImg = pygame.image.load(os.path.join(assetsDir, image)).convert_alpha()
            tempImgW, tempImgH = tempImg.get_width(), tempImg.get_height()
            img = pygame.transform.scale(tempImg, (tempImgW * self.scale, tempImgH * self.scale))
            assetsDict[image] = img

        return assetsDict


    def run(self):
        animalList = []
        
        
        stag = Stag(0)
        stag2 = Stag(1)
        boar = Boar(2)
        wolf = Wolf(3)
            
        animalList.extend([stag, stag2, boar, wolf])
        run = True
        input = InputManager()
        world = World()
        world.generateSurface()

        while run:
            input.handleEvents()
            self.mousePos = pygame.mouse.get_pos()
            
            self.clock.tick(self.fps)
            world.draw(self.screen)
            #self.screen.blit(self.backGroundSurface, (0,0))


            for animal in animalList:
                animal.update(self.screen, backgroundStartingX=self.backgroundStartingX, backgroundStartingY=self.backgroundStartingY, mousePos=self.mousePos)
            
            #print(stagList[0].currentPosition, stagList[0].endPosition, stagList[0].path, stagList[0])
            
            if input.isActionPressed("escape"):
                run = False

            if input.isMouseButtonPressed("left"):
                for animal in animalList:
                    if animal.isClicked:
                        self.selectedAnimal = animal
                        self.inspector = AnimalInspector(self.selectedAnimal)
            
            if input.isMouseButtonPressed("right"):
                self.inspector.isShowing = False



            self.inspector.update(self.screen)

            pygame.display.update()



if __name__ == "__main__":
    test = Test()
    test.run()
    
    #test.loadBackgroundAssets()

    
    