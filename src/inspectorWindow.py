import pygame
import os
import typing

Animal = typing.TypeVar("Animal")

class InspectorWindow:
    def __init__(self, animal: Animal):
        self.width, self.height = 300, 200
        
        self.fontPath = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), "assets")
        self.font = pygame.font.Font(os.path.join(self.fontPath, "kingdomFont.otf"), 24)
        
        self.display = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.backgroundColor = (0, 0, 0, 128)
        self.textColor = (255, 206, 120)
        
        self.animal = animal

        self.isShowing = True

    def createWindow(self):
        self.display.fill(self.backgroundColor)

        self.hungerText = self.font.render(f"Hunger:" , True, self.textColor)
        self.thirstText = self.font.render(f"Thirst:" , True, self.textColor)

        self.hungerBar = Bar(80, 100, 200, self.animal.maxHunger, self.animal.currentHunger)
        self.thirstBar = Bar(80, 130, 200, self.animal.maxThirst, self.animal.currentThirst)

        self.display.blit(self.hungerText, (0, 100))
        self.display.blit(self.thirstText, (0, 130))

        self.hungerBar.update(self.display, self.animal.currentHunger, self.animal)
        self.thirstBar.update(self.display, self.animal.currentThirst, self.animal)

    def draw(self, screen):
        if self.isShowing:
            screen.blit(self.display, (self.animal.rect.x, self.animal.rect.y))

    def update(self, screen):
        if self.animal != None:
            self.createWindow()
            self.draw(screen=screen)


class Bar:
    def __init__(self, left, top, width, maxStat, currentStat):
        self.left = left
        self.top = top
        self.width = width
        self.maxStat = maxStat
        self.currentStat = currentStat
        self.unitWidth = self.width / self.maxStat
        self.maxStatRect = pygame.Rect(self.left, self.top, self.width, 24)
        self.currentStatRect = pygame.Rect(self.left, self.top, self.unitWidth * self.currentStat, 24)
        

    def update(self, screen,  currentStat, animal):
        self.currentStat = currentStat
        self.currentStatRect = pygame.Rect(self.left, self.top, self.unitWidth * self.currentStat, 24)
        self.draw(screen, animal)
    
    def draw(self, screen, animal):
        pygame.draw.rect(screen, (255, 0, 0), self.maxStatRect)
        pygame.draw.rect(screen, (0, 255, 0), self.currentStatRect)
        
        
        