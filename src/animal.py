import pygame
import os
import json
import numpy as np
from collections import deque
from random import randint
from concurrent.futures import ProcessPoolExecutor
from config import *
from collections import deque

def findClosestWaterPath(startPos: tuple[int, int], waterGrid: list[list[int]]) -> list[tuple[int, int]]:
    startX, startY = startPos
    rows, cols = len(waterGrid), len(waterGrid[0])

    if not (0 <= startX < cols and 0 <= startY < rows):
        print(f"[ERROR] Start position out of bounds: {startPos}")
        return []

    queue = deque()
    visited = set()

    queue.append((startX, startY, [(startX, startY)]))
    visited.add((startX, startY))

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        x, y, path = queue.popleft()

        for dx, dy in directions:
            nextX, nextY = x + dx, y + dy

            if 0 <= nextX < cols and 0 <= nextY < rows and (nextX, nextY) not in visited:
                value = waterGrid[nextY][nextX]

                if value == 1:
                    return path

                elif value == 0:
                    queue.append((nextX, nextY, path + [(nextX, nextY)]))
                    visited.add((nextX, nextY))

    
    return []




from collections import deque
def findWalkablePath(startPos: tuple[int, int], endPos: tuple[int, int], walkableGrid: list[list[int]]) -> list[tuple[int, int]]:
    '''
    Changed from DFS to BFS since we restricted the endPos to be within 20 units of len in both axis from startPos 
    (DFS could have explored the whole grid, BFS explore tipically much closer to the start)
    '''

    

    startX, startY = startPos
    endX, endY = endPos
    
    rows, cols = len(walkableGrid), len(walkableGrid[0])
    visited = set()
    
    # Use a deque for BFS (queue)
    queue = deque([(startX, startY, [(startX, startY)])])
    visited.add((startX, startY))
    
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Movement directions (right, left, down, up)

    while queue:
        x, y, path = queue.popleft()  # Get the front element of the queue

        # If we've reached the end position, return the path
        if (x, y) == (endX, endY):
            return path

        # Explore all neighboring nodes
        for dx, dy in directions:
            nextX, nextY = x + dx, y + dy

            if 0 <= nextX < cols and 0 <= nextY < rows and (nextX, nextY) not in visited:
                # If the path is walkable, continue BFS
                if walkableGrid[nextY][nextX] == 1:
                    visited.add((nextX, nextY))
                    queue.append((nextX, nextY, path + [(nextX, nextY)]))

    return []  # Return empty if no path found



class Animal:

    #max 1 background process per Animal
    executor = ProcessPoolExecutor(max_workers=1)

    def __init__(self):


        self.animationsList = []
        self.animationIndex = 0
        self.currentFrame = 0

        self.x, self.y = 0, 0        
        
        self.type = "stag"
        
        self.animationDict = self.loadAnimations()
        self.hasConvertedAssets = False

        self.animationCooldown = 100
        self.animationUpdateTime = pygame.time.get_ticks()
        self.currentFrame = 0
        self.currentAnimation = "idle"
        self.currentDirection = 0 #0 is north-east, 1 is north-west, 2 is south-east, 3 is south-west
        self.surface : pygame.Surface = self.animationDict[self.currentAnimation][self.currentDirection][self.currentFrame]
        self.rect = self.surface.get_rect()

        self.clock = pygame.time.Clock()
        self.deltaTime = self.clock.tick(60)

        self.walkableGrid = self.getWalkableMask()
        self.waterGrid = self.getWaterMask()
        self.foodGrid = self.getFoodMask()
        self.position = self.generateStartingPosition()
        self.path = []
        self.pathFuture = None #holds future obj for async process
        


        self.maxHunger = 400
        self.currentHunger = randint(200, self.maxHunger)
        self.isHungry = False
        self.maxThirst = 400
        self.currentThirst = randint(200, self.maxThirst)
        self.isThirsty = False
        self.isWalkingThirstPath = False
        self.isWalkingHungerPath = False


        self.moveTime = pygame.time.get_ticks()
        self.moveCooldown = 400 
        self.tileDuration = 20 / 60
        self.horizontalDelta = 16 / self.tileDuration
        self.horizontalProgress = 0
        self.verticalDelta = 8 / self.tileDuration 
        self.verticalProgress = 0
        self.timeProgress = 0
        self.nextPos = self.position


        self.isClicked = False


    ################################################################### LOAD ASSETS ###################################################################

    def loadAnimations(self) -> dict:
        d = {}
        path =  os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                os.pardir,
                "assets",
                "Isometric Animals",
                f"{self.type}")
        
        for anim in os.listdir(path):
            animList = []
            for direction in os.listdir(f"{path}\\{anim}"):
                imgList = []
                for img in os.listdir(f"{path}\\{anim}\\{direction}"):
                    tile = pygame.image.load(f"{path}\\{anim}\\{direction}\\{img}")
                    imgList.append(tile)
                animList.append(imgList)
            d[anim] = animList
        
        return d

    def dictConvertAlpha(self) -> None:
        self.hasConvertedAssets = True
        for anim_key in self.animationDict:
            for i, frame_list in enumerate(self.animationDict[anim_key]):
                for j, tile in enumerate(frame_list):
                    self.animationDict[anim_key][i][j] = tile.convert_alpha()

    ################################################################### END LOAD ASSETS ###################################################################

    ################################################################### ANIMATION LOGIC ###################################################################

    def setAnimationType(self, newAnim: str) -> None:
        if newAnim == self.currentAnimation:
            return
       
        self.currentAnimation = newAnim
        self.currentFrame = 0
        self.animationUpdateTime = pygame.time.get_ticks()
        self.surface = self.animationDict[self.currentAnimation][self.currentDirection][self.currentFrame]

    def setAnimationDirection(self, newDir: str) -> None:
        #0 is north-east, 1 is north-west, 2 is south-east, 3 is south-west

        match newDir:
            case "north-east": newDir = 0
            case "north-west": newDir = 1
            case "south-east": newDir = 2
            case "south-west": newDir = 3
        
        self.currentDirection = newDir
        self.surface = self.animationDict[self.currentAnimation][self.currentDirection][self.currentFrame]

    def updateAnimation(self) -> None:
        self.surface = self.animationDict[self.currentAnimation][self.currentDirection][self.currentFrame]
        
        #iterate through current animation
        if pygame.time.get_ticks() - self.animationUpdateTime > self.animationCooldown:
            self.currentFrame = (self.currentFrame + 1) % len(self.animationDict[self.currentAnimation][self.currentDirection]) 
            self.animationUpdateTime = pygame.time.get_ticks()

    def draw(self, screen, hoffset, voffset) -> None:
        #set rect coords to screen coords 
        
        x, y = self.position


        pixelPosX = (32 * gridw)/2 + x * 16 - y * 16 + hoffset + self.horizontalProgress
        pixelPosY = x * 8 + y * 8 - 24 + voffset + self.verticalProgress # -24 is to align with sprite's bottom


        self.rect.topleft = (pixelPosX, pixelPosY)
        screen.blit(self.surface, self.rect)

    ################################################################### END ANIMATION LOGIC ###################################################################


    ################################################################### MOVEMENT LOGIC ###################################################################
    
    def handleBasicNeeds(self) -> None:
        self.currentHunger -= 0.2
        self.currentThirst -= 0.2

        if self.currentThirst <= 0:
            self.currentThirst = 0
            self.isThirsty = True
        
        if self.currentHunger <= 0:
            self.currentHunger = 0
            self.isHungry = True

    def getWalkableMask(self) -> list[list[int]]:
        with open("src\\data\\worldGrid.json", "r") as file:
            worldGrid = json.load(file)

        terrain = np.array(worldGrid)
        mask = (terrain == 1) | (terrain == 20) | (terrain == 21) | (terrain == 22) | (terrain == 23) | (terrain == 24) | (terrain == 25) | (terrain == 26) | (terrain == 27) | (terrain == 28) | (terrain == 29) | (terrain == 30) | (terrain == 31) | (terrain == 32) | (terrain == 33) | (terrain == 34) | (terrain == 35) | (terrain == 36) 
        intMask = mask.astype(int)
        
        return intMask.tolist()
    
    def getWaterMask(self) -> list[list[int]]:
        with open("src\\data\\worldGrid.json", "r") as file:
            worldGrid = json.load(file)

        terrain = np.array(worldGrid)
        mask = (terrain == 3) | (terrain == 4) | (terrain == 5) | (terrain == 6) | (terrain == 7)
        intMask = mask.astype(int)

        return intMask.tolist()
 
    def getFoodMask(self) -> list[list[int]]:
        with open("src\\data\\worldGrid.json", "r") as file:
            worldGrid = json.load(file)
        
        terrain = np.array(worldGrid)
        mask = (terrain == 20) | (terrain == 21) | (terrain == 22) | (terrain == 23) | (terrain == 24) | (terrain == 25) | (terrain == 26)
        intMask = mask.astype(int)

        return intMask.tolist()



    def generateStartingPosition(self) -> tuple[int, int]:
        isSearching = True
        while isSearching:
            y = randint(0, len(self.walkableGrid)-1)
            x = randint(0, len(self.walkableGrid[0])-1)

            startingPos = self.walkableGrid[y][x]
            if startingPos == 1:
                isSearching = False

        return (x, y)

    def handleAnimalMovementLogic(self) -> None:
        # Already has a path -- do nothing
        if self.path:
            return

        # If path is computing, check if done
        if self.pathFuture is not None:
            if self.pathFuture.done():
                try:
                    result = self.pathFuture.result()
                except Exception as e:
                    result = []

                if result:
                    self.path = result
                    self.pathFuture = None
                    return
                else:
                    
                    if self.isWalkingThirstPath:
                        self.isThirsty = True
                        self.isWalkingThirstPath = False
                    if self.isWalkingHungerPath:
                        self.isHungry = True
                        self.isWalkingHungerPath = False

                    self.pathFuture = None
                    return
            else:
               
                return

        # If just finished a thirst path
        if self.isWalkingThirstPath:
            self.isWalkingThirstPath = False
            self.currentThirst = self.maxThirst
            self.isThirsty = False
            self.setAnimationType("idle")

            self.path = [self.position] * 30
            return

        # If just finished a hunger path
        if self.isWalkingHungerPath:
            self.isWalkingHungerPath = False
            self.currentHunger = self.maxHunger
            self.isHungry = False
            self.setAnimationType("idle")
            match self.currentDirection:
                case 0:
                    pos = (self.position[0], self.position[1]-1)
                case 1:
                    pos = (self.position[0]-1, self.position[1])
                case 2:
                    pos = (self.position[0]+1, self.position[1])
                case 3:
                    pos = (self.position[0], self.position[1]+1)

            self.path = [pos] * 30
            

            return
        



        # No path and nothing being computed — check needs
        if self.isThirsty:
            
            try:
                self.pathFuture = Animal.executor.submit(findClosestWaterPath, self.position, self.waterGrid)
                self.isWalkingThirstPath = True
            except Exception as e:
                print(f"[ERROR] Could not start thirst path task: {e}")
            return

        if self.isHungry:
            
            try:
                self.pathFuture = Animal.executor.submit(findClosestWaterPath, self.position, self.foodGrid)
                self.isWalkingHungerPath = True
            except Exception as e:
                print(f"[ERROR] Could not start hunger path task: {e}")
            return

        # All basic needs fulfilled — random movement
        
        isSearching = True
        while isSearching:
            y = randint(max(0, self.position[1] - 40), min(self.position[1] + 40, len(self.walkableGrid) - 1))
            x = randint(max(0, self.position[0] - 40), min(self.position[0] + 40, len(self.walkableGrid[0]) - 1))

            if self.walkableGrid[y][x] == 1:
                isSearching = False

        try:
            self.pathFuture = Animal.executor.submit(findWalkablePath, self.position, (x, y), self.walkableGrid)
        except Exception as e:
            print(f"[ERROR] Could not start random walk path task: {e}")
        return

                
    def move(self, deltaTime) -> None:
        if self.path == []:
            return #cant move, its idling till a path is generated
        
        
        if pygame.time.get_ticks() - self.moveTime >= self.moveCooldown:
            self.moveTime = pygame.time.get_ticks()

            # Commit the move: only now consider we’ve reached nextPos
            if self.nextPos is not None:
                self.position = self.nextPos

            # Clean up path: skip tile if it matches current position
            if self.path and self.path[0] == self.position:
                self.path.pop(0)

            # Set new nextPos, if available
            if self.path:
                self.nextPos = self.path.pop(0)
                if self.nextPos == self.position:
                    self.setAnimationType("idle")
                else:
                    self.setAnimationType("walk")


            # Reset animation progress
            self.horizontalProgress, self.verticalProgress = 0, 0


        # Determine direction and animate movement
        dx, dy = self.nextPos[0] - self.position[0], self.nextPos[1] - self.position[1]
        match (dx, dy):
            case (1, 0):
                direction = "south-east"
                xsign, ysign = 1, 1
            case (0, 1):
                direction = "south-west"
                xsign, ysign = -1, 1
            case (-1, 0):
                direction = "north-west"
                xsign, ysign = -1, -1
            case (0, -1):
                direction = "north-east"
                xsign, ysign = 1, -1
            case (0, 0):
                match self.currentDirection:
                    case 0: direction = "north-east"
                    case 1: direction = "north-west"
                    case 2: direction = "south-east"
                    case 3: direction = "south-west"
                xsign, ysign = 0, 0


        self.horizontalProgress += self.horizontalDelta * xsign * deltaTime
        self.verticalProgress += self.verticalDelta * ysign * deltaTime
        
        self.setAnimationDirection(direction)
        
        

        if abs(self.horizontalProgress) >= 16 and abs(self.verticalProgress) >= 8: #already reached nextPos
            self.position = self.nextPos
            self.nextPos = None
            self.moveTime = self.moveCooldown +1 #triggers nextPos assignment
            self.horizontalProgress = 0
            self.verticalProgress = 0

    ################################################################### END MOVEMENT LOGIC ###################################################################

    ################################################################### INSPECTOR WINDOW LOGIC ###################################################################
    def isBeingClicked(self, mousePos : tuple[int, int]) -> bool:
        return self.rect.collidepoint(mousePos)
    ################################################################### END INSPECTOR WINDOW LOGIC ###################################################################


    ################################################################### UPDATE METHOD ###################################################################
    def update(self, screen, hoffset, voffset, deltaTime) -> None:
        if not self.hasConvertedAssets:
            self.dictConvertAlpha()
        
        
        self.handleBasicNeeds()
        self.handleAnimalMovementLogic()
        self.move(deltaTime)
        self.updateAnimation()
        self.draw(screen, hoffset, voffset)  

        
    ################################################################### END UPDATE METHOD ###################################################################











if __name__ == "__main__":
    screen = pygame.display.set_mode((screenw, screenh))
    s = Animal()

    
    


    isRunning = True
    while isRunning:
        
        screen.fill((0,0,0))
        s.update(screen)
        
        
            
        
        
        
        
        



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    isRunning = False
                
                if event.key == pygame.K_t:
                    s.setAnimationType("run")
                if event.key == pygame.K_d:
                    s.setAnimationDirection("south-west")

        pygame.display.update()












