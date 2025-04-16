from noise import pnoise2
from config import *
import pygame
import os
import sys 
import subprocess
import textwrap
import json
import numpy as np
import shutil
import warnings


class World:
    def __init__(self, seed:int=None):
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        warnings.filterwarnings("ignore", category=UserWarning, message="libpng warning: bKGD: invalid")
        
        self.clearDirectory("src/data/Summer")
        self.clearDirectory("src/data/Autumn")
        self.clearDirectory("src/data/Winter")



        self.width, self.heigth = gridw, gridh
        self.seed = seed
        self.grid = self.createGrid() #[0] * self.width * self.heigth
        
        
        self.isShowingAerialView = False
        self.aerialViewProcess = None
        
        #images arent loaded with convert_alpha since a screen is not initialized, 
        #once a screen is set up make sure to call self.dictConvertAlpha to make images transparent
        self.dicts = [] 
        self.backgroundAssetDict = self.loadBackgroundAssets()

        self.clock = pygame.time.Clock().tick(60)

        self.createSurfaceList("Summer")
        #self.createSurfaceList("Autumn")
        #self.createSurfaceList("Winter")

        self.surfaceList = [self.loadSurfaceList("Summer")]#, self.createSurfaceList("Autumn"), self.createSurfaceList("Winter")]
        print(self.surfaceList)
        self.surfaceSeasonIndex = 0
        self.surfaceFrameIndex = 0
        if isinstance(self.surfaceList[self.surfaceSeasonIndex][self.surfaceFrameIndex], pygame.Surface): 
            self.surface = self.surfaceList[self.surfaceSeasonIndex][self.surfaceFrameIndex]
        else:
            self.surface = pygame.Surface((gridw, gridh))
        self.surfaceAnimationCooldown = 250
        self.surfaceUpdateTime = pygame.time.get_ticks()


        self.isMovingLeft, self.isMovingRight, self.isMovingUp, self.isMovingDown = False, False, False, False
        
        
    ################################################################### LOAD ASSETS ###################################################################
    
    def loadBackgroundAssets(self) -> dict:
        d = {}
        path =  os.path.join(
                os.path.dirname(os.path.abspath(__file__)),  # Gets src directory
                os.pardir,                                  
                'assets',                                 
                'Isometric Environment',
                'Tiles'
        )
        for img in os.listdir(path):
            loadImg = pygame.image.load(f"{path}\{img}")
            name = img.replace(".png", "")
            d[name] = loadImg

        self.dicts.append(d)
        return d 
        
    def dictConvertAlpha(self) -> None:
        for d in self.dicts:
            for name in d:
                d[name] = d[name].convert_alpha()
        
    def clearDirectory(self, path):
        for filename in os.listdir(path):
            filePath = os.path.join(path, filename)
            try:
                if os.path.isfile(filePath) or os.path.islink(filePath):
                    os.remove(filePath)  
                elif os.path.isdir(filePath):
                    shutil.rmtree(filePath)  
            except Exception as e:
                print(f"Failed to delete {filePath}. Reason: {e}")
    ################################################################### END LOAD ASSETS ###################################################################

    ################################################################### GRID GENERATION ###################################################################

    '''
    def generateNoise(self) -> list[list[float]]:
        noise1 = PerlinNoise(octaves=3)
        noise2 = PerlinNoise(octaves=6)
        noise3 = PerlinNoise(octaves=12)
        noise4 = PerlinNoise(octaves=24)

        def normalize(num):
            return (num+1)/2

        xpix, ypix = self.width, self.heigth
        pic = []
        for i in range(xpix):
            row = []
            for j in range(ypix):
                noise_val = noise1([i/xpix, j/ypix])
                noise_val += 0.5 * noise2([i/xpix, j/ypix])
                noise_val += 0.25 * noise3([i/xpix, j/ypix])
                noise_val += 0.125 * noise4([i/xpix, j/ypix])
                normalizedNoise = normalize(noise_val)
                row.append(normalizedNoise)
            pic.append(row)
        return pic

    def generateGridOld(self, noise: list[list[float]]) -> list[list[int]]:
        forestList = [random.randint(10, 20) for _ in range(len(noise) * len(noise[0]))] #type of tree chosen for that specific tile
        forestProbabilityList = [random.randint(0, 2) for _ in range(len(noise) * len(noise[0]))] #probability that chosen tree is rendered
        grid = []
        for y in range(len(noise)):
            row = []
            for x in range(len(noise[0])):
                currentNum = noise[y][x]
                if currentNum < 0.4:
                    row.append(0) #water

                elif 0.4 <= currentNum < 0.6: #plain
                    row.append(1)

                else:
                    if forestProbabilityList[y*len(noise[0])+x] == 0:
                        row.append(forestList[y * len(noise[0]) + x]) #forest
                    else:
                        row.append(2)

            grid.append(row)
        return grid
        
    def generateWaterTiles(self, grid: list[list[int]]) -> list[list[int]]:
        #process different water types
        #ext = 3
        #int = 4
        #left = 5
        #right = 6
        #middle = 7
        
        out = []
        

        for y in range(len(grid)):
            row = []
            for x in range(len(grid[y])):
                currentTile = grid[y][x]

                if currentTile != 0: #not water
                    row.append(currentTile)
                    continue

                

                topLeft = grid[y-1][x-1] == 0
                top = grid[y-1][x] == 0
                left = grid[y][x-1] == 0

               
                
                match [topLeft, top, left]:
                    #external
                    case [False, True, True]:   row.append(3) 
                    
                    #internal
                    case [False, False, False]: row.append(4)
                    
                    case [True, False, False]:  row.append(4)

                    #left
                    case [False, False, True]:  row.append(5)

                    case [True, False, True]:   row.append(5)

                    #right
                    case [False, True, False]:  row.append(6)

                    case [True, True, False]:   row.append(6)

                    #middle 
                    case [True, True, True]:    row.append(7)

            out.append(row)

        return out
    '''
    def generateGrid(self, seed:int = None) -> list[list[int]]:
        def normalize(num):
            return (num + 1) / 2

        
        width, height = self.width, self.heigth


        if seed is not None:
            np.random.seed(seed)
        
        normalizedNoise = np.zeros((width, height), dtype=np.float32)
        grid = np.zeros((width, height), dtype=int)

        
        forestList = np.random.randint(10, 20, size=(width, height))
        forestProbability = np.random.randint(0, 3, size=(width, height))
        
      

        
        for y in range(width):  
            coord_y = (y / height) *4 
            for x in range(height):
                coord_x = (x / width) * 4
                

                val = pnoise2(coord_x, coord_y, octaves=3, base=seed or 0)
                val += 0.5 * pnoise2(coord_x, coord_y, octaves=6, base=seed or 0)
                val += 0.25 * pnoise2(coord_x, coord_y, octaves=12, base=seed or 0)
                val += 0.125 * pnoise2(coord_x, coord_y, octaves=24, base=seed or 0)

                normalizedNoise[y, x] = normalize(val)

        # Assign terrain based on normalized noise values
        plains_mask = (normalizedNoise >= 0.4) & (normalizedNoise < 0.6)
        forest_mask = (normalizedNoise >= 0.6) & (forestProbability == 0)
        terrain_mask = (normalizedNoise >= 0.6) & ~forest_mask

        grid[plains_mask] = 1
        grid[forest_mask] = forestList[forest_mask]
        grid[terrain_mask] = 2

        # Water classification
        water_mask = normalizedNoise < 0.4

        def shift(arr, dy, dx):
            padded = np.pad(arr, ((1, 1), (1, 1)), constant_values=False)
            shifted = padded[1 + dy:1 + dy + arr.shape[0], 1 + dx:1 + dx + arr.shape[1]]
            return shifted

        top = shift(water_mask, -1, 0)
        left = shift(water_mask, 0, -1)
        top_left = shift(water_mask, -1, -1)

        water_type = np.zeros_like(grid)

        # Apply water type rules
        water_type[(~top_left & top & left)] = 3
        water_type[(~top_left & ~top & ~left) | (top_left & ~top & ~left)] = 4
        water_type[(~top_left & ~top & left) | (top_left & ~top & left)] = 5
        water_type[(~top_left & top & ~left) | (top_left & top & ~left)] = 6
        water_type[(top_left & top & left)] = 7

        grid[water_mask] = water_type[water_mask]

        return grid.tolist()

    def createGrid(self) -> list[list[int]]:        
        out = self.generateGrid(self.seed)
        with open("src/data/worldGrid.json", "w") as file:
            json.dump(out, file)
        
        return out

    @staticmethod
    def drawAerialView(screen, grid, width, heigth) -> None:
        
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                value = grid[y][x]
                if value == 1:
                    pygame.draw.rect(screen, (142, 214, 107), pygame.Rect(x * screenw / width , y* screenh / heigth, screenw / width, screenh / heigth))
                    
                elif 10 <= value <= 20 or value == 2:
                    pygame.draw.rect(screen, (31, 82, 6), pygame.Rect(x * screenw / width , y* screenh / heigth, screenw / width, screenh / heigth))     
                    
                else:
                    pygame.draw.rect(screen, (13, 132, 201), pygame.Rect(x  * screenw / width , y* screenh / heigth, screenw / width, screenh / heigth))
                    
    def showAerialView(self) -> None:
        self.isShowingAerialView = True
        with open("src\\aerialView.pyw", "w") as file:
            file.write(textwrap.dedent('''\
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

        '''))
        
        self.aerialViewProcess = subprocess.Popen([sys.executable, "src/aerialView.pyw"])
    
    def checkAerialViewProcess(self) -> int:
        if self.aerialViewProcess.poll() is None:
            return 0
        
        return 1


    ################################################################### END GRID GENERATION ###################################################################

    ################################################################### SURFACE CREATION ###################################################################

    
    def createSurface(self, frameNum: int, type:str="Summer") -> list[pygame.Surface, pygame.Surface]:
        surface = pygame.Surface((32 * self.width, 32 * self.heigth))
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                value = self.grid[y][x]
                foilageImg = None
                match value:
                    case 1:
                        img = self.backgroundAssetDict[f"grassyDirt{type}"]
                    case 2:
                        img = self.backgroundAssetDict[f"grassyDirt{type}"]
                    case 3:
                        img = self.backgroundAssetDict[f"waterExt{frameNum}"]
                    case 4:
                        img = self.backgroundAssetDict[f"waterInt{frameNum}"]
                    case 5:
                        img = self.backgroundAssetDict[f"waterL{frameNum}"]
                    case 6:
                        img = self.backgroundAssetDict[f"waterR{frameNum}"]
                    case 7:
                        img = self.backgroundAssetDict[f"waterMid{frameNum}"]
                    case 10:
                        img = self.backgroundAssetDict[f"grassyDirt{type}"]
                        
                        foilageImg = self.backgroundAssetDict[f"treeG{value-10}{type}"]
                    case 11:
                        img = self.backgroundAssetDict[f"grassyDirt{type}"]
                        foilageImg = self.backgroundAssetDict[f"treeG{value-10}{type}"]
                    case 12:
                        img = self.backgroundAssetDict[f"grassyDirt{type}"]
                        foilageImg = self.backgroundAssetDict[f"treeG{value-10}{type}"]
                    case 13:
                        img = self.backgroundAssetDict[f"grassyDirt{type}"]
                        foilageImg = self.backgroundAssetDict[f"treeG{value-10}{type}"]
                    case 14:
                        img = self.backgroundAssetDict[f"grassyDirt{type}"]
                        foilageImg = self.backgroundAssetDict[f"treeG{value-10}{type}"]
                    case 15:
                        img = self.backgroundAssetDict[f"grassyDirt{type}"]
                        foilageImg = self.backgroundAssetDict[f"treeG{value-10}{type}"]
                    case 16:
                        img = self.backgroundAssetDict[f"grassyDirt{type}"]
                        foilageImg = self.backgroundAssetDict[f"treeG{value-10}{type}"]
                    case 17:
                        img = self.backgroundAssetDict[f"grassyDirt{type}"]
                        foilageImg = self.backgroundAssetDict[f"treeG{value-10}{type}"]
                    case 18:
                        img = self.backgroundAssetDict[f"grassyDirt{type}"]
                        foilageImg = self.backgroundAssetDict[f"treeG{value-10}{type}"]
                    case 19:
                        img = self.backgroundAssetDict[f"grassyDirt{type}"]
                        foilageImg = self.backgroundAssetDict[f"treeG{value-10}{type}"]
                    case 20:
                        img = self.backgroundAssetDict[f"grassyDirt{type}"]
                        foilageImg = self.backgroundAssetDict[f"treeG{value-10}{type}"]

                surface.blit(img, ((32 * self.width)/2 + x *16 - y*16, x*8 +y*8))
                if foilageImg != None:
                    surface.blit(foilageImg, ((32 * self.width)/2 + x *16 - y*16, x*8 +y*8 - 70))

        return surface

    def createSeasonSurface(self, season:str, framenum: int) -> None:
        with open(f"src\\create{season}{framenum}Surface.pyw", "w") as file:
            file.write(textwrap.dedent('''\
        
import pygame
import os
import json
from config import *
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message="libpng warning: bKGD: invalid")

os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
pygame.display.set_mode((1, 1))
surface = pygame.Surface((32*gridw, 16*gridh))

name = os.path.basename(__file__)
                                       
if "Winter" in name:
    season = "Winter"
if "Autumn" in name:
    season = "Autumn"
if "Summer" in name:
    season = "Summer"
                                       
framenum = int(name[-12])



with open("src/data/worldGrid.json", "r") as file:
    grid = json.load(file)

def loadAssets() -> dict:
    d = {}
    path =  os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.pardir,
            "assets",
            "Isometric Environment",
            "Tiles")
    
    for img in os.listdir(path):
        loadimg = pygame.image.load(f"{path}\{img}").convert_alpha()
        name = img.replace(".png", "")
        d[name] = loadimg
    
    return d

backgroundAssetDict = loadAssets()





for y in range(gridw):
    for x in range(gridh):
        value = grid[y][x]
        foilageImg = None
        match value:
            case 1:
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 2:
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 3:
                img = backgroundAssetDict[f"waterExt{framenum}"]
            case 4:
                img = backgroundAssetDict[f"waterInt{framenum}"]
            case 5:
                img = backgroundAssetDict[f"waterL{framenum}"]
            case 6:
                img = backgroundAssetDict[f"waterR{framenum}"]
            case 7:
                img = backgroundAssetDict[f"waterMid{framenum}"]  
            case 10:
                img = backgroundAssetDict[f"grassyDirt{season}"]  
                foilageImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 11:
                img = backgroundAssetDict[f"grassyDirt{season}"] 
                foilageImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 12:
                img = backgroundAssetDict[f"grassyDirt{season}"]
                foilageImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 13:
                img = backgroundAssetDict[f"grassyDirt{season}"]  
                foilageImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 14:
                img = backgroundAssetDict[f"grassyDirt{season}"]  
                foilageImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 15:
                img = backgroundAssetDict[f"grassyDirt{season}"]  
                foilageImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 16:
                img = backgroundAssetDict[f"grassyDirt{season}"]  
                foilageImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 17:
                img = backgroundAssetDict[f"grassyDirt{season}"]  
                foilageImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 18:
                img = backgroundAssetDict[f"grassyDirt{season}"]  
                foilageImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 19:
                img = backgroundAssetDict[f"grassyDirt{season}"]  
                foilageImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 20:
                img = backgroundAssetDict[f"grassyDirt{season}"]  
                foilageImg = backgroundAssetDict[f"treeG{value-10}{season}"]
                            
        surface.blit(img, ((32*gridw)/2 +x*16 -y*16, x*8+y*8))
        if foilageImg != None:
            surface.blit(foilageImg, ((32*gridw)/2 +x*16 - y*16, x*8+y*8 -70))
                            


pygame.image.save(surface, f"src/data/{season}/{season}{framenum}Surface.png")
pygame.quit()
os.remove(os.path.abspath(__file__))

'''))
            
        self.createSurfaceProcess = subprocess.Popen([sys.executable, f"src\\create{season}{framenum}Surface.pyw"])
            
    def updateSurfacePosition(self, hoffsetPrevious: int, voffsetPrevious: int) -> tuple[int, int]:
        hoffset, voffset = hoffsetPrevious, voffsetPrevious
        if self.isMovingDown:
            voffset += 1
        if self.isMovingUp:
            voffset -= 1
        if self.isMovingLeft:
            hoffset -= 1
        if self.isMovingRight:
            hoffset += 1

        return (hoffset, voffset)
    
    

    def createSurfaceList(self, season) -> None:
        for i in range(8): #8 is the length of the water animation
            self.createSeasonSurface(season, i)

    def loadSurfaceList(self, season) -> list[pygame.Surface]:
        import time
        path =  os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "data",
                f"{season}"
               
        )
    
        while len(os.listdir(f'src/data/{season}')) != 8:
            print(os.listdir(path))
            pygame.time.wait(500)
        print(os.listdir(path))
        
        

        out = []
        
        
        for filename in os.listdir(path):
            print(path, filename, os.path.join(path, filename))
            img = pygame.image.load(os.path.join(path, filename))
            print(img)
            
            
        return out
           

       

        

            

    def updateSurfaceAnimation(self) -> None:
        if pygame.time.get_ticks() - self.surfaceUpdateTime > self.surfaceAnimationCooldown:
            self.surfaceUpdateTime = pygame.time.get_ticks()
            self.surfaceFrameIndex = (self.surfaceFrameIndex + 1) % len(self.surfaceList)
            self.surface = self.surfaceList[self.surfaceSeasonIndex][self.surfaceFrameIndex]
            
    def draw(self, screen: pygame.Surface, horizontalOffset: int, verticalOffset: int):
        if self.surface is None:
            return
        self.updateSurfaceAnimation()
        screen.blit(self.surface, (((-1*self.width*16)+screenw/2) - horizontalOffset, -1*self.heigth*8 - verticalOffset))


    ################################################################### END SURFACE CREATION ###################################################################
    
if __name__ == "__main_":
    path =  os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "data",
                f"Summer"
               
        )

    out = []
    print(os.listdir(path))
    
    for filename in os.listdir(path):
        print(path, filename, os.path.join(path, filename))
        img = pygame.image.load(os.path.join(path, filename))
        print(img)

if __name__ == "__main__":
    
    screen = pygame.display.set_mode((screenw, screenh))
    w = World(seed=42)
    w.dictConvertAlpha()
    hoffset, voffset = 0, 0


    isRunning = True
    
    while isRunning:
        screen.fill((0, 0, 0))

        hoffset, voffset = w.updateSurfacePosition(hoffset, voffset)
        w.draw(screen, hoffset, voffset)
        
        
        
        if w.isShowingAerialView:
            if w.checkAerialViewProcess():
                w.isShowingAerialView = False




        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    w.surfaceSeasonIndex +=1
                if event.key == pygame.K_ESCAPE:
                    isRunning = False
                if event.key == pygame.K_f and not w.isShowingAerialView:
                    w.showAerialView()

                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    w.isMovingLeft = True
                    
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    w.isMovingRight = True
                    
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    w.isMovingUp = True
                    

                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    w.isMovingDown = True
                    

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    w.isMovingLeft = False
                    
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    w.isMovingRight = False
                    
                
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    w.isMovingUp = False
                    

                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    w.isMovingDown = False
                    

        pygame.display.update()


    
    









