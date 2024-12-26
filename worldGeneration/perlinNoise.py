from perlin_noise import PerlinNoise
from config import *


import matplotlib.pyplot as plt
import pygame



class World:
    def __init__(self):
        self.worldSurface = pygame.Surface((SCREEN_W, SCREEN_H))
        self.tileDimension = SCREEN_W / MAP_ROW_LEN
        self.waterPatternDicts = {
            "water_middle":             [True, True, True, True],          
            "water_nw":                 [True, False, True, True],
            "water_sw":                 [True, True, True, False],
            "water_se":                 [True, True, False, True],
            "water_ne":                 [False, True, True, True],
            "water_north":              [False, False, True, True],
            "water_south":              [True, False, True, False],
            "water_west":               [True, True, False, False],
            "water_east":               [False, True, False, True],
            "water_nw-se":              [True, False, False, True],
            "water_ne-sw":              [False, True, True, False],
            "water_west-ne":            [False, False, True, False],
            "water_east-nw":            [False, False, False, True],
            "water_east-sw":            [False, True, False, False],
            "water_west-se":            [True, False, False, False],
            "water_all":                [False, False, False, False],
        }

        self.tilesList = [key for key in self.waterPatternDicts.keys()]
        self.tilesList.extend(["plain", "mountain"])
        print(self.tilesList)
        self.imageDict = self.preloadImages()
        self.normalizedMap = self.perlinNoise()
        self.worldMap = self.generateWorld()
        self.worldSurface = self.generateSurface()



    def preloadImages(self) -> dict:
        imageDict = {}
        for key in self.tilesList:
            imageDict[key] = pygame.image.load(os.path.join(IMGPATH, f"{key}.png")).convert_alpha()

        return imageDict

    def normalizePerlinNoiseMap(self, map: list[list[float]]) -> list[list[float]]:
        minValue = min(min(row for row in map))
        maxValue = max(max(row for row in map))

        normalizedMap = [[(val  - minValue) / (maxValue - minValue) for val in row] for row in map]

        return normalizedMap


    def perlinNoise(self) -> list[list[float]]:
        noise1 = PerlinNoise(octaves=2)
        noise2 = PerlinNoise(octaves=4)
        noise3 = PerlinNoise(octaves=8)
        noise4 = PerlinNoise(octaves=12)

        map = []
        for i in range(MAP_ROW_LEN):
            row = []
            for j in range(MAP_ROW_LEN):
                noise_val = noise1([i/MAP_ROW_LEN, j/MAP_ROW_LEN])
                noise_val += 0.5 * noise2([i/MAP_ROW_LEN, j/MAP_ROW_LEN])
                noise_val += 0.25 * noise3([i/MAP_ROW_LEN, j/MAP_ROW_LEN])
                noise_val += 0.125 * noise4([i/MAP_ROW_LEN, j/MAP_ROW_LEN])

                row.append(noise_val)
            map.append(row)

        normalizedMap = self.normalizePerlinNoiseMap(map)
        
        return normalizedMap
    
    def generateWorld(self) -> list[list[str]]:
        perlinNoiseMap = self.normalizedMap

        worldMap = []

        for y in range(len(perlinNoiseMap)):
            if y == 0 or y == len(perlinNoiseMap)-1:
                tempRow = ["plain"] * len(perlinNoiseMap)
            else:
                tempRow = []
                for x in range(len(perlinNoiseMap)):
                    if x == 0 or x == len(perlinNoiseMap[y])-1:
                        tempRow.append("plain")
                    else:
                        if perlinNoiseMap[y][x] <= 0.45:
                            tempRow.append("water")
                        elif 0.45 < perlinNoiseMap[y][x] <= 0.9:
                            tempRow.append("plain")
                        else:
                            tempRow.append("mountain")

            worldMap.append(tempRow)

        waterBorderWorldMap = []
        #decide water borders
        for y in range(len(worldMap)):
            if y == 0 or y == len(worldMap)-1:
                tempRow = ["plain"] * len(worldMap)
            else:
                tempRow = []
                for x in range(len(worldMap[y])):
                    if x == 0 or x == len(worldMap)-1:
                        tempRow.append("plain")
                    else:
                        match worldMap[y][x]:
                            case "plain":
                                tempRow.append("plain")
                            case "mountain":
                                tempRow.append("mountain")
                            case "water":
                                top = worldMap[y-1][x] == "water"
                                left = worldMap[y][x-1] == "water"
                                right = worldMap[y][x+1] == "water"
                                bottom = worldMap[y+1][x] == "water"

                                neighbors = [top, left, right, bottom]


                                for key, pattern in self.waterPatternDicts.items():
                                    if pattern == neighbors:
                                        tempRow.append(key)
                                        break




            waterBorderWorldMap.append(tempRow)

        
        return waterBorderWorldMap
            
    def showNoisePlot(self) -> None:
        plt.imshow(self.normalizedMap, cmap="gray")
        plt.show()


    def generateSurface(self) -> pygame.Surface:
        for y, row in enumerate(self.worldMap):
            for x in range(len(row)):
                self.worldSurface.blit(self.imageDict[self.worldMap[y][x]], (BACKGROUND_STARTING_X + x * 15 * SCALE -y *15 * SCALE, BACKGROUND_STARTING_Y + x * 8 * SCALE +y* 8 * SCALE))

        return self.worldSurface
    
    def draw(self, screen):
        screen.blit(self.worldSurface)

if __name__ == "__main__":
    screen = pygame.display.set_mode((800, 800))
    w = World()
    #w.showNoisePlot()
    run = True
    while run:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.type == pygame.K_ESCAPE:
                    run = False

                if event.key == pygame.K_f:
                    w = World()

                
        w.draw(screen)
        pygame.display.update()