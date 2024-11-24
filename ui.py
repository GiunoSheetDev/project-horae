from animal import Animal
import pygame
 
class AnimalInspector:
    def __init__(self, animal : Animal):
        self.animal = animal
        self.display = pygame.Surface((300, 200), pygame.SRCALPHA)
        self.font = pygame.font.SysFont("Arial", 24)
        
    def createDisplay(self):
        self.display.fill((0,0,0, 128))
        self.currentStateText = self.font.render(f"State: {self.animal.currentState}--{self.animal.currentMovementState}", True, (255, 255, 255))
        self.currentDirectionText = self.font.render(f"Direction: {self.animal.currentDirection}", True ,(255, 255, 255))
        self.hungerText = self.font.render(f"Hunger: {int(self.animal.hunger)}/{self.animal.maxHunger}", True,(255, 255, 255))
        self.thirstText = self.font.render(f"Thirst:: {int(self.animal.thirst)}/{self.animal.maxThirst}", True,(255, 255, 255))

        self.display.blit(self.currentStateText, (0, 40))
        self.display.blit(self.currentDirectionText, (0, 70))
        self.display.blit(self.hungerText, (0, 100))
        self.display.blit(self.thirstText, (0, 130))
        
    def update(self, screen):
        if self.animal != None:
            self.createDisplay()
            self.draw(screen=screen)


    def draw(self, screen):
        screen.blit(self.display, (self.animal.rect.x, self.animal.rect.y))
    