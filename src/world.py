import pygame
import numpy as np
import numpy.typing as npt
import random

from noise import pnoise2
from multiprocessing import Pool


from config import *

'''
NAMING CONVENTION

create_*   → allocates/initialises empty structures
generate_* → fills with actual content (noise, images)
add_*      → public API for adding new chunks at runtime



'''


class World:
    def __init__(self, seed: int = None):
        self.gridw, self.gridh = GRIDW, GRIDH
        self.chunk_size = CHUNK_SIZE
        
        self.seed = seed if seed is not None else random.randint(1, 999999)

        self.background_assets = {}
        self._load_assets()

        self.chunk_biomes : dict[tuple[int, int], Biome] = {}
        self.world : dict[tuple[int, int], npt.NDArray] = {}
        self.world_images : dict[tuple[int, int], pygame.Surface] = {}

        self.biome_offset = (self.seed * 0.001, self.seed * 0.002)
        self.tile_offset = (self.seed * 0.003, self.seed * 0.007)

        self._create_initial_world()


    def _load_assets(self) -> None:
        for img in os.listdir(ASSET_PATH_BACKGROUND):
            load_img = pygame.image.load(f"{ASSET_PATH_BACKGROUND}\\{img}").convert_alpha()
            load_img = pygame.transform.scale_by(load_img, SCALE)
            name = img.replace(".png", "")
            self.background_assets[name] = load_img

    # -- Noise Helpers -- #

    def _biome_noise(self, wx: float, wy: float) -> float:
        ox, oy = self.biome_offset

        warp_strength = 18.0 #20-30 range means more fractal coast. #8-12 range gentler coastal curves
        warp_x = pnoise2(wx * 0.015 + ox + 1.7, wy * 0.015 + oy + 9.2, octaves=2)
        warp_y = pnoise2(wx * 0.015 + ox + 5.3, wy * 0.015 + oy + 3.1, octaves=2)

        return pnoise2(
            (wx + warp_x * warp_strength) * BIOME_SCALE + ox,
            (wy + warp_y * warp_strength) * BIOME_SCALE + oy,
            octaves=5,
            persistence=0.55,
            lacunarity=2.1
        )
        
    def _tile_noise(self, wx: float, wy: float) -> float:
        '''
        Fine scale noise that decides individual tiles
        '''
        ox, oy = self.tile_offset
        return pnoise2(
            wx * TILE_SCALE + ox,
            wy * TILE_SCALE + oy,
            octaves = 4,
            persistence = 0.5,
            lacunarity = 2.0
        )


    # -- Biome / Tile Mapping -- #

    def _noise_to_biome(self, value: float) -> Biome:
        if value < -0.05:   return Biome.OCEAN
        elif value < 0.10:  return Biome.PLAIN
        else:               return Biome.FOREST

    def _noise_to_tile(self, tile_value: float, biome_value: float) -> int:
        if biome_value < -0.05:      # OCEAN
            if tile_value < 0.30:    return Tile.WATER.value
            else:                    return Tile.PLAIN.value

        elif biome_value < 0.10:     # PLAIN
            if tile_value < -0.35:   return Tile.WATER.value
            elif tile_value < 0.40:  return Tile.PLAIN.value
            else:                    return Tile.FOREST.value

        else:                        # FOREST
            if tile_value < -0.30:   return Tile.WATER.value
            elif tile_value < 0.0:   return Tile.PLAIN.value
            else:                    return Tile.FOREST.value

    
    # -- Chunk Generation -- #

    def _assign_biome(self, chunk_index: tuple[int, int]) -> None:
        y0, x0 = chunk_index

        #sample noise at chunk center
        cx, cy = (x0 + self.chunk_size/2), (y0 + self.chunk_size/2)
        value = self._biome_noise(cx, cy)
        self.chunk_biomes[chunk_index] = self._noise_to_biome(value)

    def _generate_tiles(self, chunk_index: tuple[int, int]) -> None:
        y0, x0 = chunk_index
        chunk = self.world[chunk_index]

        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                wx, wy = x0 + x, y0 + y
                tile_value  = self._tile_noise(wx, wy)
                biome_value = self._biome_noise(wx, wy)
                chunk[y, x] = self._noise_to_tile(tile_value, biome_value)

        self.world[chunk_index] = chunk

    def _collapse_water(self, chunk_index: tuple[int, int]) -> None:
        """Classify raw WATER tiles into edge variants based on neighbors."""

        WATER_VAL = Tile.WATER.value

        def get_tile(y, x) -> int:
            """Read a tile, looking into neighbor chunks if needed."""
            cy = (y0 + (y // self.chunk_size) * self.chunk_size
                  if y >= self.chunk_size else
                  y0 - self.chunk_size if y < 0 else y0)
            cx = (x0 + (x // self.chunk_size) * self.chunk_size
                  if x >= self.chunk_size else
                  x0 - self.chunk_size if x < 0 else x0)

            # clamp local coords
            ly = y % self.chunk_size
            lx = x % self.chunk_size

            nidx = (cy, cx)
            if nidx in self.world:
                t = int(self.world[nidx][ly, lx])
                # treat specialized water variants as water for edge detection
                if t in (Tile.WATER_EXT.value, Tile.WATER_INT.value,
                         Tile.WATER_LEFT.value, Tile.WATER_RIGHT.value,
                         Tile.WATER_MID.value):
                    return WATER_VAL
                return t
            return Tile.PLAIN.value  # default for missing chunks

        y0, x0 = chunk_index
        chunk = self.world[chunk_index].copy()

        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                if chunk[y, x] != WATER_VAL:
                    continue

                n_above = get_tile(y - 1, x) == WATER_VAL  # row above
                n_left  = get_tile(y, x - 1) == WATER_VAL  # col left
                n_diag  = get_tile(y - 1, x - 1) == WATER_VAL  # diagonal

                if not n_above and not n_left:
                    chunk[y, x] = Tile.WATER_INT.value
                elif n_above and not n_left:
                    chunk[y, x] = Tile.WATER_LEFT.value
                elif not n_above and n_left:
                    chunk[y, x] = Tile.WATER_RIGHT.value
                elif n_diag and n_above and n_left:
                    chunk[y, x] = Tile.WATER_MID.value
                else:
                    chunk[y, x] = Tile.WATER_EXT.value

        self.world[chunk_index] = chunk

    def _generate_chunk(self, chunk_index: tuple[int, int]) -> None:
        self.world[chunk_index] = np.full((self.chunk_size, self.chunk_size), Tile.EMPTY.value)
        self._assign_biome(chunk_index)
        self._generate_tiles(chunk_index)   
        self._collapse_water(chunk_index)
        self._generate_chunk_image(chunk_index)
        
    def _create_initial_world(self) -> None:
        for y in range(0, self.gridh, self.chunk_size):
            for x in range(0, self.gridw, self.chunk_size):
                self._generate_chunk((y, x))

    
    # --  Rendering -- #

    def _generate_chunk_image(self, chunk_index: tuple[int, int]) -> None:
        chunk = self.world[chunk_index]

        TILE_W = 32 * SCALE
        TILE_H = 32 * SCALE  

        surf_w = 32 * self.chunk_size + TILE_W
        surf_h = 16 * self.chunk_size + TILE_H + 32
        surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)

        
        origin_x = TILE_W // 2

        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                tile = Tile(chunk[y, x])

                match tile:
                    case Tile.PLAIN:        img = self.background_assets["EMPTY"]
                    case Tile.FOREST:       img = self.background_assets["PLAIN_SUMMER"]
                    case Tile.WATER:        img = self.background_assets["WATER_MID_0"]
                    case Tile.WATER_EXT:    img = self.background_assets["WATER_EXT_0"]
                    case Tile.WATER_INT:    img = self.background_assets["WATER_INT_0"]
                    case Tile.WATER_LEFT:   img = self.background_assets["WATER_LEFT_0"]
                    case Tile.WATER_RIGHT:  img = self.background_assets["WATER_RIGHT_0"]
                    case Tile.WATER_MID:    img = self.background_assets["WATER_MID_0"]
                    case _:                 img = self.background_assets["rock"]

                blit_x = origin_x + (32 * self.chunk_size) // 2 + x * 16 - y * 16
                blit_y = x * 8 + y * 8
                surface.blit(img, (blit_x, blit_y))

        self.world_images[chunk_index] = surface

    def _generate_world_image(self, season: str) -> None:
        self.world_images.clear()
        for chunk_index in self.world:
            self._generate_chunk_image(chunk_index, season)

    def _draw(self, screen, camera_pos: tuple[int, int]) -> None:
        cam_x, cam_y = camera_pos
        TILE_W = 32 * SCALE
        origin_x = TILE_W // 2 

        sorted_chunks = sorted(self.world_images.items(), key=lambda kv: kv[0][0] + kv[0][1])

        for (y0, x0), surface in sorted_chunks:
            iso_x = (x0 - y0) * 16 - origin_x  
            iso_y = (x0 + y0) * 8
            screen.blit(surface, (iso_x - cam_x, iso_y - cam_y))
    
    
    # -- Public Methods -- #

    def add_chunk(self, pos: tuple[int, int], direction: str) -> None:
        y, x = pos
        index_x = (x // self.chunk_size) * self.chunk_size
        index_y = (y // self.chunk_size) * self.chunk_size

        match direction.lower():
            case "north": index_y -= self.chunk_size
            case "south": index_y += self.chunk_size
            case "east" : index_x += self.chunk_size
            case "west" : index_x -= self.chunk_size

        chunk_index = (index_y, index_x)
        if chunk_index not in self.world:
            self._generate_chunk(chunk_index)

    

if __name__ == "__main__":
    
    screen = pygame.display.set_mode((SCREENW, SCREENH))
    w = World()

    camerax, cameray = 0, 0


    is_moving_left = is_moving_right = is_moving_up = is_moving_down = False

    while True:
        screen.fill((0, 0, 0))
        w._draw(screen, (camerax, cameray))

        if is_moving_left:
            camerax -= 2
        if is_moving_right:
            camerax += 2
        if is_moving_up:
            cameray -= 2
        if is_moving_down:
            cameray += 2


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    is_moving_left = True
                elif event.key == pygame.K_d:
                    is_moving_right = True                
                if event.key == pygame.K_w:
                    is_moving_up = True
                elif event.key == pygame.K_s:
                    is_moving_down = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    is_moving_left = False
                elif event.key == pygame.K_d:
                    is_moving_right = False                
                if event.key == pygame.K_w:
                    is_moving_up = False
                elif event.key == pygame.K_s:
                    is_moving_down = False


        pygame.display.update()








