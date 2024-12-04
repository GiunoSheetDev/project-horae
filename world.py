import random
import pygame
import os


from config import *



class Stack:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        else:
            raise IndexError("pop from empty stack")

    def size(self):
        return len(self.items)



class Tile:
    def __init__(self, x, y):
        self.possibleTiles = list(tilesRules.keys())
        self.entropy = len(tilesRules.keys())
        self.neighbours = dict()

    def addNeighbour(self, direction, tile):
        self.neighbours[direction] = tile
    
    def getNeighbour(self, direction):
        return self.neighbours[direction]

    def getDirections(self):
        return list(self.neighbours.keys())

    def getPossibilities(self):
        return self.possibleTiles
        
    def collapse(self):
        weights = [tilesWeights[possibility] for possibility in self.possibleTiles]
        self.possibleTiles = random.choices(self.possibleTiles, weights=weights, k=1) 
        self.entropy = 0

    def constrain(self, neighbourPossibilities, direction):
        reduced = False
        if self.entropy > 0:
            possibleConnections = set()
            for tile in neighbourPossibilities: 
                for png in tilesRules[tile][direction]:
                    possibleConnections.add(png)
            possibleConnections = list(possibleConnections)

            for tile in self.possibleTiles.copy():
                if tile not in possibleConnections:
                    self.possibleTiles.remove(tile)
                    reduced = True

            if len(self.possibleTiles) == 0:
                self.possibleTiles.append('assets\\Isometric Environment\\Tiles\\light_grass_dirt.png')
            
            self.entropy = len(self.possibleTiles)
            

        return reduced
        




class World:
    def __init__(self):
        self.worldSurface = pygame.Surface((SCREEN_W, SCREEN_H))
        
        self.grid = [[Tile(x, y) for x in range(MAP_ROW_LEN)] for y in range(MAP_ROW_LEN)]

        for y in range(MAP_ROW_LEN):
            for x in range(MAP_ROW_LEN):
                tile = self.grid[y][x]
                if y > 0:
                    tile.addNeighbour(NORTH_EAST, self.grid[y - 1][x])
                if x < MAP_ROW_LEN - 1:
                    tile.addNeighbour(SOUTH_EAST, self.grid[y][x + 1])
                if y < MAP_ROW_LEN - 1:
                    tile.addNeighbour(SOUTH_WEST, self.grid[y + 1][x])
                if x > 0:
                    tile.addNeighbour(NORTH_WEST, self.grid[y][x - 1])

    def getEntropy(self, x, y):
        return self.grid[y][x].entropy
    
    def getType(self, x, y):
        return self.grid[y][x].possibleTiles[0]
    
    def getLowestEntropy(self):
        lowestEntropy = len(list(tilesRules.keys()))
        for y in range(MAP_ROW_LEN):
            for x in range(MAP_ROW_LEN):
                tileEntropy = self.grid[y][x].entropy
                if tileEntropy > 0:
                    if tileEntropy < lowestEntropy:
                        lowestEntropy = tileEntropy
        return lowestEntropy

    def getTilesWithLowestEntropy(self):
         
        lowestEntropy = len(list(tilesRules.keys()))
        tileList = []

        for y in range(MAP_ROW_LEN):
            for x in range(MAP_ROW_LEN):
                tileEntropy = self.grid[y][x].entropy
                if tileEntropy > 0:
                    if tileEntropy < lowestEntropy:
                        tileList.clear()
                        lowestEntropy = tileEntropy
                    if tileEntropy == lowestEntropy:
                        tileList.append(self.grid[y][x])
        return tileList

    def waveFunctionCollapse(self):

        tilesLowestEntropy = self.getTilesWithLowestEntropy()

        if tilesLowestEntropy == []:
            return 0

        tileToCollapse = random.choice(tilesLowestEntropy)
        tileToCollapse.collapse()

        stack = Stack()
        stack.push(tileToCollapse)

        while(stack.is_empty() == False):
            tile = stack.pop()
            tilePossibilities = tile.getPossibilities()
            directions = tile.getDirections()

            for direction in directions:
                neighbour = tile.getNeighbour(direction)
                if neighbour.entropy != 0:
                    reduced = neighbour.constrain(tilePossibilities, direction)
                    if reduced == True:
                        stack.push(neighbour)    # When possibilities were reduced need to propagate further

        return 1

    def generateSurface(self):
        done = False
        while done == False:
            print("DONE")
            result = self.waveFunctionCollapse()
            if result == 0:
                done = True
                print("CAIO")
                


        for y in range(MAP_ROW_LEN):
            for x in range(MAP_ROW_LEN):
                type = self.getType(x, y)
                img = pygame.image.load(type).convert_alpha()
                self.worldSurface.blit(img, (BACKGROUND_STARTING_X + x * 15 * SCALE -y *15 * SCALE, BACKGROUND_STARTING_Y + x * 8 * SCALE +y* 8 * SCALE))




    def draw(self, screen):
        screen.blit(self.worldSurface, (0,0))




if __name__ == "__main__":
    t = Tile(2, 3)
    t.constrain(['assets\\Isometric Environment\\Tiles\\dirt_full.png', 'assets\\Isometric Environment\\Tiles\\water_middle.png', 'assets\\Isometric Environment\\Tiles\\light_grass_rock.png'], SOUTH_EAST)
    print(t.possibleTiles, t.entropy)
    t.constrain(['assets\\Isometric Environment\\Tiles\\dirt_full.png'], SOUTH_EAST)
    print(t.possibleTiles, t.entropy)
    t.constrain(['assets\\Isometric Environment\\Tiles\\dirt_full.png'], NORTH_WEST)
    print(t.possibleTiles, t.entropy)
    w = World()

    
    
    test = {}
    for y in range(MAP_ROW_LEN):
        for x in range(MAP_ROW_LEN):
            if w.getType(y, x) in test.keys():
                test[w.getType(y, x)] += 1
            else:
                test[w.getType(y, x)] = 1


    print(test)
            

