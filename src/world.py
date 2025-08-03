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
import time


from animal import Animal
from inspectorWindow import InspectorWindow


class World:
    def __init__(self, seed:int=None, createNewImages:bool = True):
        pygame.init()
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        warnings.filterwarnings("ignore", category=UserWarning, message="libpng warning: bKGD: invalid")
        


        self.width, self.heigth = gridw, gridh
        self.seed = seed
         
        
        
        self.isShowingAerialView = False
        self.aerialViewProcess = None
        
        #images arent loaded with convert_alpha since a screen is not initialized, 
        #once a screen is set up make sure to call self.dictConvertAlpha to make images transparent
        #make sure to set the screen with pygame.SCRALPHA
        self.dicts = [] 
        self.backgroundAssetDict = self.loadBackgroundAssets()

        self.clock = pygame.time.Clock()
    
        if createNewImages:
            self.grid = self.createGrid()
            self.clearDirectory("src/data/Summer")
            self.clearDirectory("src/data/Autumn")
            self.clearDirectory("src/data/Winter")
            self.surfaceList, self.treeList = self.createSurfaceList()

        else:
            with open("src\\data\\worldGrid.json", "r") as file:
                self.grid = json.load(file)
            self.surfaceList, self.treeList = self.loadImages()

        
        self.surfaceSeasonIndex = 0
        self.surfaceFrameIndex = 0
        if isinstance(self.surfaceList[self.surfaceSeasonIndex][self.surfaceFrameIndex], pygame.Surface): 
            self.surface = self.surfaceList[self.surfaceSeasonIndex][self.surfaceFrameIndex]
            self.treeSurface = self.treeList[self.surfaceSeasonIndex][0]
        else:
            self.surface = pygame.Surface((gridw, gridh))
        
        self.surfaceAnimationCooldown = 250
        self.surfaceUpdateTime = pygame.time.get_ticks()
        self.seasonAnimationCooldown = 60 * 3 * 1000 #3 minutes
        self.seasonUpdateTime = pygame.time.get_ticks()
        

        self.isMovingLeft, self.isMovingRight, self.isMovingUp, self.isMovingDown = False, False, False, False
        self.isFastMoving = False
        self.isRunning = True
        
        self.fontPath = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), "assets")
        self.font = pygame.font.Font(os.path.join(self.fontPath, "kingdomFont.otf"), 48)
        self.seasonText = None
        self.isShowingText = False
        self.alphaFloat = 255.0
        self.alphaStep = 255 / 300
        self.textColor = (255, 206, 120)
        self.hasDisplayedApproachingText = False

        self.animalList = []
        self.selectedAnimal = None
        self.inspectorWindow = None
        
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
            loadImg = pygame.image.load(f"{path}\\{img}")
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
                pass
    
    def loadImages(self) -> tuple[list[pygame.Surface], list[pygame.Surface]]:

        out1 = [] #terrain surface
        out2 = [] #tree surface
        for season in ["Summer", "Autumn", "Winter"]:
            path = f"src/data/{season}"
            tempout1 = []
            tempout2 = []
            for filename in os.listdir(path):
                imgname = os.path.join(path, filename)
                img = pygame.image.load(imgname).convert_alpha()
                if "tree" in imgname:
                    
                    tempout2.append(img)
                else:
                    
                    tempout1.append(img)
            out1.append(tempout1)
            out2.append(tempout2)


        return (out1, out2)

    ################################################################### END LOAD ASSETS ###################################################################

    ################################################################### GRID GENERATION ###################################################################


  
    def generateGrid(self, seed: int = None) -> list[list[int]]:
        '''
        Terrain encoding:
        0  = background / initial default (should be overwritten)
        1  = plains
        2  = tree areas without actual tree tiles
        3-7  = water tiles (classified into types)
        10-19 = tree tiles
        20-26 = grass tiles
        27-36 = foliage / misc tiles
        '''

        def normalize(num):
            # Normalize noise value from [-1, 1] to [0, 1]
            return (num + 1) / 2

        width, heigth = self.width, self.heigth

        # Use provided seed or generate a random one
        if seed is None:
            seed = np.random.randint(0, 1000)
        rng = np.random.default_rng(seed)

        # Initialize data arrays
        normalizedNoise = np.zeros((width, heigth), dtype=np.float32)
        grid = np.zeros((width, heigth), dtype=int)

        # Pre-generate tile values and probabilities for forests, grass, and foliage
        forestList = rng.integers(10, 20, size=(width, heigth))
        forestProbability = rng.integers(0, 3, size=(width, heigth))  # ~33% chance

        grassList = rng.integers(20, 26, size=(width, heigth), endpoint=True)
        grassProbability = rng.integers(0, 10, size=(width, heigth), endpoint=True)  # ~70% if < 7

        foilageMiscList = rng.integers(27, 33, size=(width, heigth), endpoint=True)
        foilageMiscProbability = rng.integers(0, 60, size=(width, heigth))  # ~1 in 60 chance

        # Generate layered Perlin noise for terrain base
        for y in range(width):
            coord_y = (y / heigth) * 4
            for x in range(heigth):
                coord_x = (x / width) * 4

                val = (
                    pnoise2(coord_x, coord_y, octaves=3, base=seed)
                    + 0.5 * pnoise2(coord_x, coord_y, octaves=6, base=seed)
                    + 0.25 * pnoise2(coord_x, coord_y, octaves=12, base=seed)
                    + 0.125 * pnoise2(coord_x, coord_y, octaves=24, base=seed)
                )

                normalizedNoise[y, x] = normalize(val)

        # Determine base terrain types based on noise
        plains_mask = (normalizedNoise >= 0.4) & (normalizedNoise < 0.6)  # Moderate terrain
        forest_mask = (normalizedNoise >= 0.6) & (forestProbability == 0)  # Higher terrain with forest probability
        terrain_mask = (normalizedNoise >= 0.6) & ~forest_mask  # Higher terrain but no forest
        water_mask = normalizedNoise < 0.4  # Low terrain → water

        # Assign basic terrain types
        grid[plains_mask] = 1  # Plains
        grid[forest_mask] = forestList[forest_mask]  # Forest tiles (actual tree tiles)
        grid[terrain_mask] = 2  # Tree area without specific trees

        # Helper function to shift arrays for adjacency checks
        def shift(arr, dy, dx):
            padded = np.pad(arr, ((1, 1), (1, 1)), constant_values=False)
            return padded[1 + dy : 1 + dy + arr.shape[0], 1 + dx : 1 + dx + arr.shape[1]]

        # Spread tree-area terrain (2) into adjacent plains to blend biome edges
        for _ in range(4):  # Apply 4 times for gradual spread
            plains_to_upgrade = np.zeros_like(grid, dtype=bool)
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                shifted = shift(grid == 2, dy, dx)
                plains_to_upgrade |= (grid == 1) & shifted
            grid[plains_to_upgrade] = 2

        # Recalculate mask for remaining plains after terrain spreading
        newTerrainMask = (grid == 1)

        # Apply grass tiles on plains with high probability (~70%)
        grassTerrainMask = newTerrainMask & (grassProbability < 7)
        grid[grassTerrainMask] = grassList[grassTerrainMask]

        # Apply foliage/misc tiles on plains with very low probability (~1 in 60)
        foilageTerrainMask = newTerrainMask & (foilageMiscProbability == 1)
        grid[foilageTerrainMask] = foilageMiscList[foilageTerrainMask]

        # --- Water type classification ---
        # Determine type of water tile based on adjacency for visual variety
        top = shift(water_mask, -1, 0)
        left = shift(water_mask, 0, -1)
        top_left = shift(water_mask, -1, -1)

        water_type = np.zeros_like(grid)

        # Water type classification based on neighbor patterns
        water_type[(~top_left & top & left)] = 3
        water_type[(~top_left & ~top & ~left) | (top_left & ~top & ~left)] = 4
        water_type[(~top_left & ~top & left) | (top_left & ~top & left)] = 5
        water_type[(~top_left & top & ~left) | (top_left & top & ~left)] = 6
        water_type[(top_left & top & left)] = 7

        # Apply classified water tiles
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
                    
                elif 10 <= value <= 34 or value == 2:
                    pygame.draw.rect(screen, (31, 82, 6), pygame.Rect(x * screenw / width , y* screenh / heigth, screenw / width, screenh / heigth))     
                    
                else:
                    pygame.draw.rect(screen, (13, 132, 201), pygame.Rect(x  * screenw / width , y* screenh / heigth, screenw / width, screenh / heigth))
                    
    def showAerialView(self) -> None:
        self.isShowingAerialView = True
        with open("src\\aerialView.pyw", "w") as file:
            file.write(textwrap.dedent('''\\
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

    def createTreeSurface(self, season:str) -> None:
        with open(f"src\\create{season}TreeSurface.pyw", "w") as file:
            file.write(textwrap.dedent('''\\
                                       
import pygame
import os
import json
from config import *
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message="libpng warning: bKGD: invalid")

os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
pygame.display.set_mode((1, 1))
surface = pygame.Surface((32*gridw, 16*gridh + 32), pygame.SRCALPHA)

name = os.path.basename(__file__)
                                       
if "Winter" in name:
    season = "Winter"
    mseason = "winter"
if "Autumn" in name:
    season = "Autumn"
    mseason = "autumn"
if "Summer" in name:
    season = "Summer"
    mseason = "summer"


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
        loadimg = pygame.image.load(f"{path}\\{img}").convert_alpha()
        name = img.replace(".png", "")
        d[name] = loadimg
    
    return d

backgroundAssetDict = loadAssets()

for y in range(gridw):
    for x in range(gridh):
        value = grid[y][x]
        treeImg = None
        miscImg = None
        match value:
            case 10:
                treeImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 11:
                treeImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 12:
                treeImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 13:
                treeImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 14:
                treeImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 15:
                treeImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 16:
                treeImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 17:
                treeImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 18:
                treeImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            case 19:
                treeImg = backgroundAssetDict[f"treeG{value-10}{season}"]
            
            
        if treeImg != None:
            surface.blit(treeImg, ((32*gridw)/2 +x*16 - y*16, x*8+y*8 -70))
        
                            


pygame.image.save(surface, f"src/data/{season}/{season}treeSurface.png")
pygame.quit()
os.remove(os.path.abspath(__file__))



'''))
            

        createSurfaceProcess = subprocess.Popen([sys.executable, f"src\\create{season}treeSurface.pyw"])
        return createSurfaceProcess
                               
    def createSeasonSurface(self, season:str, framenum: int) -> None:
        with open(f"src\\create{season}{framenum}Surface.pyw", "w") as file:
            file.write(textwrap.dedent('''\\
        
import pygame
import os
import json
from config import *
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message="libpng warning: bKGD: invalid")

os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
pygame.display.set_mode((1, 1))
surface = pygame.Surface((32*gridw, 16*gridh + 32), pygame.SRCALPHA)

name = os.path.basename(__file__)
                                       
if "Winter" in name:
    season = "Winter"
    mseason = "winter"
if "Autumn" in name:
    season = "Autumn"
    mseason = "autumn"
if "Summer" in name:
    season = "Summer"
    mseason = "summer"
                                       
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
        loadimg = pygame.image.load(f"{path}\\{img}").convert_alpha()
        name = img.replace(".png", "")
        d[name] = loadimg
    
    return d

backgroundAssetDict = loadAssets()





for y in range(gridw):
    for x in range(gridh):
        value = grid[y][x]
        miscImg = None
        img = None
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
            case 11:
                img = backgroundAssetDict[f"grassyDirt{season}"] 
            case 12:
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 13:
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 14:
                img = backgroundAssetDict[f"grassyDirt{season}"] 
            case 15:
                img = backgroundAssetDict[f"grassyDirt{season}"] 
            case 16:
                img = backgroundAssetDict[f"grassyDirt{season}"] 
            case 17:
                img = backgroundAssetDict[f"grassyDirt{season}"]  
            case 18:
                img = backgroundAssetDict[f"grassyDirt{season}"]  
            case 19:
                img = backgroundAssetDict[f"grassyDirt{season}"]                                         
            case 20:
                miscImg = backgroundAssetDict[f"{mseason}Grass{value-20}"]
                img = backgroundAssetDict[f"grassyDirt{season}"] 
            case 21:
                miscImg = backgroundAssetDict[f"{mseason}Grass{value-20}"]
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 22:
                miscImg = backgroundAssetDict[f"{mseason}Grass{value-20}"]
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 23:
                miscImg = backgroundAssetDict[f"{mseason}Grass{value-20}"]
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 24:
                miscImg = backgroundAssetDict[f"{mseason}Grass{value-20}"]
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 25:
                miscImg = backgroundAssetDict[f"{mseason}Grass{value-20}"]
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 26:
                miscImg = backgroundAssetDict[f"{mseason}Grass{value-20}"]
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 27:
                miscImg = backgroundAssetDict[f"{mseason}Grass{value-20}"]
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 28:
                miscImg = backgroundAssetDict[f"{mseason}Misc{value-28}"]
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 29:
                miscImg = backgroundAssetDict[f"{mseason}Misc{value-28}"]
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 30:
                miscImg = backgroundAssetDict[f"{mseason}Misc{value-28}"]
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 31:
                miscImg = backgroundAssetDict[f"{mseason}Misc{value-28}"]
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 32:
                miscImg = backgroundAssetDict[f"{mseason}Misc{value-28}"]
                img = backgroundAssetDict[f"grassyDirt{season}"]
            case 33:
                miscImg = backgroundAssetDict[f"{mseason}Misc{value-28}"]
                img = backgroundAssetDict[f"grassyDirt{season}"]
            
                            
        surface.blit(img, ((32*gridw)/2 +x*16 -y*16, x*8+y*8))
        if miscImg != None:
            surface.blit(miscImg, ((32*gridw)/2 +x*16 - y*16, x*8+y*8))               


pygame.image.save(surface, f"src/data/{season}/{season}{framenum}Surface.png")
pygame.quit()
os.remove(os.path.abspath(__file__))

'''))
            
        createSurfaceProcess = subprocess.Popen([sys.executable, f"src\\create{season}{framenum}Surface.pyw"])
        return createSurfaceProcess

    def updateSurfacePosition(self, hoffsetPrevious: int, voffsetPrevious: int) -> tuple[int, int]:
        hoffset, voffset = hoffsetPrevious, voffsetPrevious
        delta = 1 * 240 #base movement at 60 fps

        if self.isFastMoving:
            delta = 2 * 240

        if self.isMovingDown:
            voffset += delta * self.deltaTime
        if self.isMovingUp:
            voffset -= delta * self.deltaTime
        if self.isMovingLeft:
            hoffset -= delta * self.deltaTime
        if self.isMovingRight:
            hoffset += delta * self.deltaTime
        
        return (hoffset, voffset)
    
    def createSurfaceList(self) -> tuple[list[pygame.Surface], list[pygame.Surface]]:
        
        createdProcesses = []
        processesProgress = [True] * (8*3 + 3)

        pfS = self.createTreeSurface("Summer")
        pfA = self.createTreeSurface("Autumn")
        pfW = self.createTreeSurface("Winter")

        createdProcesses.append(pfS)
        createdProcesses.append(pfA)
        createdProcesses.append(pfW)

        for i in range(8): #8 is the length of the water animation
            pS = self.createSeasonSurface("Summer", i)
            pA = self.createSeasonSurface("Autumn", i)
            pW = self.createSeasonSurface("Winter", i)
            createdProcesses.append(pS)
            createdProcesses.append(pA)
            createdProcesses.append(pW)

        while processesProgress != [False] *(8*3+3):
            time.sleep(0.1)
            for i in range(8*3+3):
                if createdProcesses[i].poll() is None:
                    continue
                else:
                    processesProgress[i] = False

        #all process are done
        out1 = [] #terrain surface
        out2 = [] #tree surface

        out1, out2 = self.loadImages()
        return (out1, out2)
           
    def updateSurfaceAnimation(self) -> None:
        
       
        ################################################################### CHANGE OF SEASON LOGIC ###################################################################
        #1 minute before the season it loads the images. 
        #only if the next season hasnt loaded yet
        
        
        if pygame.time.get_ticks() - self.seasonUpdateTime> (self.seasonAnimationCooldown - 60*1000) and not self.hasDisplayedApproachingText:
            
            nextIndex = (self.surfaceSeasonIndex +1) % 3
            match nextIndex:
                case 0: season = "Summer"
                case 1: season = "Autumn"
                case 2: season = "Winter"

           

            self.isShowingText = True
            self.hasDisplayedApproachingText = True
            self.alphaFloat = 255.0
            self.showingTextTime = pygame.time.get_ticks()

            self.seasonText = self.font.render(f"{season} is fast approaching.", True, self.textColor).convert_alpha()
            

        

            
        #update current season
        if pygame.time.get_ticks() - self.seasonUpdateTime > self.seasonAnimationCooldown:
            self.seasonUpdateTime = pygame.time.get_ticks()
            self.surfaceSeasonIndex = (self.surfaceSeasonIndex +1 ) % len(self.surfaceList)

            

            nextIndex = (self.surfaceSeasonIndex) % 3
            match nextIndex:
                case 0: season = "Summer"
                case 1: season = "Autumn"
                case 2: season = "Winter"

            self.seasonText = self.font.render(f"{season} is here.", True, self.textColor).convert_alpha()
            self.alphaFloat = 255.0
            self.isShowingText = True
            self.hasDisplayedApproachingText = False
            self.showingTextTime = pygame.time.get_ticks()


        ################################################################### END CHANGE OF SEASON LOGIC ###################################################################



        #update frame animation
        if pygame.time.get_ticks() - self.surfaceUpdateTime > self.surfaceAnimationCooldown:
            self.surfaceUpdateTime = pygame.time.get_ticks()
            self.surfaceFrameIndex = (self.surfaceFrameIndex + 1) % len(self.surfaceList[self.surfaceSeasonIndex])
            self.surface = self.surfaceList[self.surfaceSeasonIndex][self.surfaceFrameIndex]
            self.treeSurface = self.treeList[self.surfaceSeasonIndex][0]

        

        if self.isShowingText:
            self.alphaFloat = self.alphaFloat - self.alphaStep
            self.seasonText.set_alpha(max(0, int(self.alphaFloat)))

            if self.alphaFloat <= 0:
                self.isShowingText = False
                      
    def draw(self, screen: pygame.Surface, horizontalOffset: int, verticalOffset: int) -> None:
        screen.fill((0,0,0))
        if self.surface is None:
            return
        
        

        self.updateSurfaceAnimation()   

        #draws background terrain
        screen.blit(self.surface, (((-1*self.width*16)+screenw/2) - horizontalOffset, -1*self.heigth*8 - verticalOffset))

        #draws animals
        self.handleAnimals(screen, ((-1*self.width*16)+screenw/2) - horizontalOffset, -1*self.heigth*8 - verticalOffset)

        #draws tree 
        screen.blit(self.treeSurface, (((-1*self.width*16)+screenw/2) - horizontalOffset, -1*self.heigth*8 - verticalOffset))
        
        
        
        if self.seasonText != None:
            screen.blit(self.seasonText, (screenw / 2 - self.seasonText.width/2, screenh / 2) )

    ################################################################### END SURFACE CREATION ###################################################################

    ################################################################### ANIMAL HANDLING LOGIC ###################################################################

    def handleAnimals(self, screen, hoffset, voffset):
       
        sortedAnimalList = sorted(self.animalList, key= lambda animal: animal.position[0])
        self.animalList = sortedAnimalList
        animal: Animal
        for animal in self.animalList:
            animal.update(screen, hoffset, voffset, self.deltaTime)

            

            



    ################################################################### END ANIMAL HANDLING LOGIC###################################################################



    ################################################################### UPDATE METHOD ###################################################################
        
    def update(self, screen: pygame.Surface):
        self.dictConvertAlpha()
        hoffset, voffset = 0, 0
        #fill list

        for _ in range(100):
            self.animalList.append(Animal())

        
  

        while self.isRunning:
            

            mousePos = pygame.mouse.get_pos()
            self.deltaTime = self.clock.tick(60) / 1000
            
            hoffset, voffset = self.updateSurfacePosition(hoffset, voffset)
            self.draw(screen, hoffset, voffset)
            
            
            
            if self.isShowingAerialView:
                if self.checkAerialViewProcess():
                    self.isShowingAerialView = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.isRunning = False
                    if event.key == pygame.K_f and not self.isShowingAerialView:
                        self.showAerialView()
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.isMovingLeft = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.isMovingRight = True
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.isMovingUp = True
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.isMovingDown = True
                    if event.key == pygame.K_LSHIFT:
                        self.isFastMoving = True
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.isMovingLeft = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.isMovingRight = False
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.isMovingUp = False
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.isMovingDown = False
                    if event.key == pygame.K_LSHIFT:
                        self.isFastMoving = False





            if self.inspectorWindow != None:
                self.inspectorWindow.update(screen)

            if pygame.mouse.get_pressed()[0]:
                animal: Animal
                for animal in self.animalList:
                    animal.isClicked = animal.isBeingClicked(mousePos)
                    if animal.isClicked:
                        self.selectedAnimal = animal
                        self.inspectorWindow = InspectorWindow(self.selectedAnimal)

            if pygame.mouse.get_pressed()[2]: 
                #reset visibility of inspector window if right click is selected
                self.inspectorWindow.isShowing = False
                self.selectedAnimal = None


            #TODO pathing is fixed, now animals eat grass on water (probably a problem with masks)
            try:
                pass
                print(self.selectedAnimal.isHungry, self.selectedAnimal.isThirsty, self.selectedAnimal.isWalkingHungerPath, self.selectedAnimal.isWalkingThirstPath, self.selectedAnimal.position)
            except:
                pass
            
            pygame.display.update()
            


    ################################################################### END UPDATE METHOD ###################################################################





if __name__ == "__main__":
    
    def main():
        screen = pygame.display.set_mode((screenw, screenh), pygame.SRCALPHA | pygame.DOUBLEBUF)
        w = World(seed=69, createNewImages=True)
        w.update(screen)
    
    main()
    
    
    
    
    









