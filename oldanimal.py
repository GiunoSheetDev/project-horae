import os
import pygame
import random

class Animal:
    def __init__(self, id : int):
        self.animal : str 
        self.id = id
        
        self.pathData = []
        
        self.directions = ["north-east", "north-west", "south-east", "south-west"]
        self.animationTypes = ["idle", "walk", "run"]


        self.scale = 1 #change self.scale also in self.loadAnimations
        self.position = (random.randint(0, 9 + 10 * (self.scale)), random.randint(0, 9 + 10 * (self.scale )))
        self.animationDict = self.loadAnimations()
        self.animationType = "run"
        self.currentDirection = "north-east"
        self.currentFrame = 0

        self.updateTime = pygame.time.get_ticks()
        self.animationCooldown = 100

        self.speed = 0.02
        self.hunger = 100
        self.thirst = 100


    def loadAnimations(self) -> dict:
        animationDict = {}
        for animation in self.animationTypes:
            animationDict[animation] = {}
            for direction in self.directions:
                tempList = []
                for image in os.listdir(f"assets/critters/{self.animal}/{animation}/{direction}"):
                    img = pygame.image.load(os.path.join(f"assets/critters/{self.animal}/{animation}/{direction}", image))
                    imgw, imgh = img.get_width(), img.get_height()
                    i = pygame.transform.scale(img, (imgw * self.scale, imgh * self.scale))
                    tempList.append(i)
            
                animationDict[animation][direction] = tempList
                
        return animationDict

    def translatePath(self, path : tuple[int, int]) -> None: #given the path length tuple modifies the pathData to adjust for speed
        if path[0] < 0:
                self.pathData.extend(["north-west"] * abs(path[0]) * int(1/self.speed))
        elif path[0] > 0:
            self.pathData.extend(["south-east"] * abs(path[0]) * int(1/self.speed))

        if path[1] < 0:
            self.pathData.extend(["north-east"] * abs(path[1]) * int(1/self.speed))
        elif path[1] > 0:
            self.pathData.extend(["south-west"] * abs(path[1]) * int(1/self.speed))



    def generatePath(self, optionalEndPoint = (-1, -1)) -> None:
        if optionalEndPoint != (-1, -1): #makes animal move to specific tile
            self.pathData = []
            path = (int(optionalEndPoint[0] - self.position[0]), int(optionalEndPoint[1] - self.position[1]))
            self.translatePath(path)
            return

        if self.pathData != []:
            return
        
        if random.randint(0, 4) < 3: #3 in 4 chance of staying idle
            self.animationType = "idle"
            self.pathData.extend(["idle"] * len(self.animationDict[self.animationType][self.currentDirection])*6)  #dunno why but 6 seems to work best
            
        else:
            self.changeSpeed("run") #TODO decide when to run or when to walk based on primary needs
            self.currentPosition = (int(self.position[0]), int(self.position[1]))
            self.endPosition = (random.randint(0, 9 + 10 * (self.scale )), random.randint(0, 9 + 10 * (self.scale )))
            path = (int(self.endPosition[0] - self.position[0]), int(self.endPosition[1] - self.position[1]))
            self.translatePath(path)

            
             

    def updatePath(self) -> None:
        if self.pathData == []:
            self.generatePath()
            return
    
        match self.pathData[0]:
            case "north-west":
                newPosition = (self.position[0]-self.speed, self.position[1])
            case "north-east":
                newPosition = (self.position[0], self.position[1]-self.speed)
            case "south-west":
                newPosition = (self.position[0], self.position[1]+self.speed)
            case "south-east":
                newPosition = (self.position[0]+self.speed, self.position[1])
            case "idle":
                newPosition = (self.position[0], self.position[1])

        self.position = newPosition
        self.pathData.pop(0)
        
    
    def updateAnimation(self) -> None:
        if self.pathData != []:
            self.handleDirectionChanges()
        try:
            self.image = self.animationDict[self.animationType][self.currentDirection][self.currentFrame]
            self.rect = self.image.get_rect(topleft= self.position)
        except:
            pass

        if pygame.time.get_ticks() - self.updateTime > self.animationCooldown:
            self.updateTime = pygame.time.get_ticks()
            self.currentFrame += 1

        if self.currentFrame >= len(self.animationDict[self.animationType][self.currentDirection]):
            self.currentFrame = 0


    def handleDirectionChanges(self) -> None:
        if self.pathData[0] == self.currentDirection:
            return

        if self.pathData[0] == "idle":
            return
        
        self.currentDirection = self.pathData[0]
        self.currentFrame = 0
        


    def changeSpeed(self, newSpeed:str) -> None:
        if newSpeed == self.animationType:
            return
        
        self.animationType = newSpeed
        match self.animationType:
            case "walk": self.speed = 0.02
            case "run" : self.speed = 0.05
            case _     : self.speed = 1

        self.pathData = []
        




        
    def update(self, screen, backgroundStartingX, backgroundStartingY) -> None:
        self.updatePath()
        self.updateAnimation()
        self.draw(screen, backgroundStartingX, backgroundStartingY)
    

    
    def draw(self, screen, backgroundStartingX, backgroundStartingY) -> None:
        screen.blit(self.image, (backgroundStartingX + self.position[0] * 15 * self.scale - self.position[1] * 15 * self.scale, backgroundStartingY -16 * self.scale + self.position[0] * 8 *self.scale + self.position[1]*8 *self.scale))
        



class Stag(Animal):
    def __init__(self, id):
        self.animal = "stag"
        super().__init__(id)

class Badger(Animal):
    def __init__(self, id):
        self.animal = "badger"
        super.__init__(id)

class Boar(Animal):
    def __init__(self, id):
        self.animal = "board"
        super.__init__(id)

class Wolf(Animal):
    def __init__(self, id):
        self.animal = "wolf"
        super.__init__(id)



        


if __name__ == "__main__":
    stag = Stag(0)
    stag.generatePath()
    
    

