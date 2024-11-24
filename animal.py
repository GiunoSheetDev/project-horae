import os
import pygame
import random

class Animal:
    def __init__(self, id : int):
        self.animal : str 
        self.id = id
        
        self.pathData = []
        
        self.directions = ["north-east", "north-west", "south-east", "south-west"]
        

        self.path = (0, 0)
        self.pathData = []

        self.scale = 1 #change self.scale also in self.loadAnimations
        self.maxRandomPositionLimit = 9 + 10 *(self.scale) -1
        self.minRandomPositionLimit = 1
        self.position = (random.randint(self.minRandomPositionLimit, self.maxRandomPositionLimit), random.randint(self.minRandomPositionLimit, self.maxRandomPositionLimit))
        self.animationDict = self.loadAnimations()
        self.currentMovementState = "idle"
        self.currentState = "wandering"
        self.currentDirection = "north-east"
        self.currentFrame = 0

        self.updateTime = pygame.time.get_ticks()
        self.animationCooldown = 100
        self.isClicked = False

        self.speed = 0.02
        self.maxHunger = 400
        self.maxThirst = 400
        self.hunger = self.maxHunger
        self.thirst = self.maxThirst
        


    def loadAnimations(self) -> dict:
        animationDict = {}
        for animation in self.states:
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
    
    def checkNeeds(self) -> None:
        #checks for thirst and hunger and determines if the state 
        # is looking for food or not
        if self.hunger < 20 or self.thirst < 20:
            self.currentState = "looking-for-resources"
        else:
            self.currentState = "wandering"

    def updateNeeds(self) -> None:
        self.hunger -= 0.2
        self.thirst -= 0.2

        if self.hunger <= 0:
            self.hunger = 0
        if self.thirst <= 0:
            self.thirst = 0



    def setMovementStateAndSpeed(self, newMovementState : str = "temp") -> None:
        if newMovementState != "temp":
            self.currentMovementState = newMovementState
            match self.currentMovementState:
                case "walk": self.speed = 0.02
                case "run" : self.speed = 0.05
                case "idle": self.speed = 1
            self.pathData = []
            return

        

        match self.currentState:
            case "looking-for-resources":
                self.currentMovementState = "run"
                self.speed = 0.05
                
            case "wandering":
                
                if random.randint(0, 4) < 3: #3 in 5 chances of being idle.
                    self.currentMovementState = "idle"
                    self.speed = 1
                    
                    
                else:
                    self.currentMovementState = "walk"
                    self.speed = 0.02


    def generatePath(self, optionalEndPosition = (-1, -1)) -> None:

        if optionalEndPosition != (-1, -1): #move animal to specific tile
            self.pathData = []
            self.endPosition = optionalEndPosition
            self.path = ((int(self.endPosition[0] - self.position[0]), int(self.endPosition[1] - self.position[1])))
            return 

        #generate a tuple with dx and dy as components
        self.currentPosition = (int(self.position[0]), int(self.position[1]))
        if self.currentMovementState == "idle":
            self.endPosition = self.currentPosition
            self.path = "idle"
            return

        if self.pathData != []:
            return
        
        match self.currentState:
            case "wandering":

                self.currentPosition = (int(self.position[0]), int(self.position[1]))
                self.endPosition = (random.randint(self.minRandomPositionLimit, self.maxRandomPositionLimit), random.randint(self.minRandomPositionLimit, self.maxRandomPositionLimit))
                self.path = (int(self.endPosition[0] - self.currentPosition[0]), int(self.endPosition[1] - self.currentPosition[1]))

            case "looking-for-resources":
                #TODO create logic to look for closest resource

                self.currentPosition = (int(self.position[0]), int(self.position[1]))
                self.endPosition = (random.randint(self.minRandomPositionLimit, self.maxRandomPositionLimit), random.randint(self.minRandomPositionLimit, self.maxRandomPositionLimit))
                self.path = (int(self.endPosition[0] - self.currentPosition[0]), int(self.endPosition[1] - self.currentPosition[1]))
        
        
        


    def translatePath(self) -> None:
        #given the path modify the pathData to adjust for speed
        if self.path == "idle":
            self.pathData.extend(["idle"] * len(self.animationDict["idle"][self.currentDirection])*6)  #dunno why but 6 seems to work best)
            return
        
        

        if self.path[0] < 0:
            self.pathData.extend(["north-west"] * abs(self.path[0]) * int(1/self.speed))
        elif self.path[0] > 0:
            self.pathData.extend(["south-east"] * abs(self.path[0]) * int(1/self.speed))

        if self.path[1] < 0:
            self.pathData.extend(["north-east"] * abs(self.path[1]) * int(1/self.speed))
        elif self.path[1] >0:
            self.pathData.extend(["south-west"] * abs(self.path[1]) * int(1/self.speed))


    def updatePath(self) -> None:

        if not self.pathData:
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


    def handleDirectionChanges(self) -> None:
        if self.pathData[0] == self.currentDirection:
            return

        if self.pathData[0] == "idle":
            return
        
        self.currentDirection = self.pathData[0]
        self.currentFrame = 0

    

    def updateAnimation(self) -> None:

        if self.pathData != []:
            self.handleDirectionChanges()

        try:
            self.image = self.animationDict[self.currentMovementState][self.currentDirection][self.currentFrame]
            self.rect = self.image.get_rect(topleft= self.position)
        except:
            pass

        if pygame.time.get_ticks() - self.updateTime > self.animationCooldown:
            self.updateTime = pygame.time.get_ticks()
            self.currentFrame += 1

        if self.currentFrame >= len(self.animationDict[self.currentMovementState][self.currentDirection]):
            self.currentFrame = 0

    def isBeingClicked(self, mousePos : tuple[int, int]) -> bool:
        return self.rect.collidepoint(mousePos)

    def update(self, screen, backgroundStartingX, backgroundStartingY, mousePos) -> None:
        self.currentPosition = (int(self.position[0]), int(self.position[1]))
        
        
        self.updateNeeds()
        if self.pathData == []:
            self.checkNeeds() # -> set current state based on hunger / thirst
            self.setMovementStateAndSpeed() # -> based on current state set movement state and speed
            self.generatePath() # -> based on movement state generate a path and pathData
            self.translatePath() # -> adjust pathData based on speed
        
        self.updatePath() # -> make character move
        self.updateAnimation() # -> animate character
        self.draw(screen=screen, backgroundStartingX=backgroundStartingX, backgroundStartingY=backgroundStartingY)
        self.isClicked = self.isBeingClicked(mousePos=mousePos)
        
        

        
    def draw(self, screen, backgroundStartingX, backgroundStartingY) -> None:
        #first set the rect coords to the screen coords and not the grid coords then blit
        self.rect.x , self.rect.y = backgroundStartingX + self.position[0] * 15 * self.scale - self.position[1] * 15 * self.scale, backgroundStartingY -16 * self.scale + self.position[0] * 8 *self.scale + self.position[1]*8 *self.scale
        screen.blit(self.image, (backgroundStartingX + self.position[0] * 15 * self.scale - self.position[1] * 15 * self.scale, backgroundStartingY -16 * self.scale + self.position[0] * 8 *self.scale + self.position[1]*8 *self.scale))
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)



class Stag(Animal):
    def __init__(self, id):
        self.animal = "stag"
        self.states = ["idle", "walk", "run"]
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
    stag.update(1, 2, 3)