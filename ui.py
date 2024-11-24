from animal import Animal
import pygame

class AnimalInspector:
    def __init__(self, animal : Animal):
        self.animal = animal
        self.display = pygame.Surface((100, 400))
        self.font = pygame.font.SysFont("Arial", 24)
        
    def createDisplay(self):
        self.display.fill((0,0,0))
        self.currentStateText = self.font.render(f"Current state: {self.animal.currentState}", True, (255, 255, 255))
        self.currentDirectionText = self.font.render(f"Current direction: {self.animal.currentDirection}", True ,(255, 255, 255))
        self.hungerText = self.font.render(f"Current hunger: {int(self.animal.hunger)}/{self.animal.maxHunger}", True,(255, 255, 255))
        self.thirstText = self.font.render(f"Current hunger: {int(self.animal.thirst)}/{self.animal.maxThirst}", True,(255, 255, 255))

        self.display.blit(self.currentStateText, (0, 200))
        self.display.blit(self.currentDirectionText, (0, 220))
        self.display.blit(self.hungerText, (0, 240))
        self.display.blit(self.thirstText, (0, 260))
        
    def update(self, screen):
        if self.animal != None:
            self.createDisplay()
            self.draw(screen=screen)


    def draw(self, screen):
        screen.blit(self.display, (self.animal.rect.x, self.animal.rect.y))
    