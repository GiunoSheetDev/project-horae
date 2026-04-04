import numpy as np
import numpy.typing as npt
import pygame

from config import *
from noise import pnoise2


class Chunk:
    def __init__(self, index: tuple[int, int], seed: int, background_assets : dict):
        self.index = index
        self.chunk_size = CHUNK_SIZE
        self.biome = Biome.EMPTY
        self.seed = seed
        self.background_assets = background_assets

        # -- Numpy Arrays -- #
        self.chunk : npt.NDArray = np.full((self.chunk_size, self.chunk_size), Tile.EMPTY.value)
        self.chunk_raw : npt.NDArray = np.full((self.chunk_size, self.chunk_size), Tile.EMPTY.value)
        self.tree_probs : npt.NDArray = np.random.random((self.chunk_size, self.chunk_size))
        self.tree_types : npt.NDArray = np.random.randint(0, 10, (self.chunk_size, self.chunk_size))

        # -- Pygame Surfaces -- #
        self.image : dict = {"summer" : None, "autumn" : None, "winter" : None}
        self.water : list[pygame.Surface] = []
        self.tree  : dict = {"summer" : None, "autumn" : None, "winter" : None}

        self.biome_offset = (self.seed * 0.001, self.seed * 0.002)
        self.tile_offset = (self.seed * 0.003, self.seed * 0.007)


        self._generate_chunk()

    
    # -- Noise Helpres -- #

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
        elif value < 0.05:  return Biome.PLAIN
        else:               return Biome.FOREST

    def _noise_to_tile(self, tile_value: float, biome_value: float) -> int:
        if biome_value < -0.05:      # OCEAN
            if tile_value < 0.30:    return Tile.WATER.value
            else:                    return Tile.PLAIN.value

        elif biome_value < 0.10:     # PLAIN
            if tile_value < -0.35:   return Tile.WATER.value
            elif tile_value < 0.15:  return Tile.PLAIN.value
            else:                    return Tile.FOREST.value

        else:                        # FOREST
            if tile_value < 0.0:     return Tile.PLAIN.value
            else:                    return Tile.FOREST.value


    # -- Chunk Generation -- #

    def _assign_biome(self) -> None:
        y0, x0 = self.index

        #sample noise at chunk center
        cx, cy = (x0 + self.chunk_size/2), (y0 + self.chunk_size/2)
        value = self._biome_noise(cx, cy)
        self.biome = self._noise_to_biome(value)

    def _generate_tiles(self) -> None:
        y0, x0 = self.index
        chunk = self.chunk

        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                wx, wy = x0 + x, y0 + y
                tile_value  = self._tile_noise(wx, wy)
                biome_value = self._biome_noise(wx, wy)
                chunk[y, x] = self._noise_to_tile(tile_value, biome_value)

        self.chunk = chunk

    def _generate_tree_probabilities(self) -> None:
        self.tree_probs = np.random.random((self.chunk_size, self.chunk_size))
        self.tree_types = np.random.randint(0, 10, (self.chunk_size, self.chunk_size))

    def _collapse_water(self, neighbor_chunks: dict[tuple[int,int], "Chunk"]) -> None:
        '''Classify raw WATER tiles into edge variants based on neighbors.'''
        WATER_VAL = Tile.WATER.value
        y0, x0 = self.index

        def get_tile(y, x) -> int:
            cy = (y0 + (y // self.chunk_size) * self.chunk_size
                if y >= self.chunk_size else
                y0 - self.chunk_size if y < 0 else y0)
            cx = (x0 + (x // self.chunk_size) * self.chunk_size
                if x >= self.chunk_size else
                x0 - self.chunk_size if x < 0 else x0)
            ly = y % self.chunk_size
            lx = x % self.chunk_size
            nidx = (cy, cx)
            if nidx == (y0, x0):
                t = int(self.chunk[ly, lx])
            elif nidx in neighbor_chunks:
                t = int(neighbor_chunks[nidx].chunk[ly, lx])
            else:
                return Tile.PLAIN.value

            if t in (Tile.WATER_EXT.value, Tile.WATER_INT.value,
                    Tile.WATER_LEFT.value, Tile.WATER_RIGHT.value,
                    Tile.WATER_MID.value):
                return WATER_VAL
            return t

        chunk = self.chunk.copy()

        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                if chunk[y, x] != WATER_VAL:
                    continue

                above = get_tile(y - 1, x) == WATER_VAL
                left  = get_tile(y, x - 1) == WATER_VAL
                diag  = get_tile(y - 1, x - 1) == WATER_VAL

                if   not above and not left:             chunk[y, x] = Tile.WATER_INT.value
                elif not above and     left:             chunk[y, x] = Tile.WATER_LEFT.value
                elif     above and not left:             chunk[y, x] = Tile.WATER_RIGHT.value
                elif not diag  and     above and left:   chunk[y, x] = Tile.WATER_EXT.value
                else:                                    chunk[y, x] = Tile.WATER_MID.value

        self.chunk = chunk

    def _generate_chunk(self) -> None:
        self.chunk = np.full((self.chunk_size, self.chunk_size), Tile.EMPTY.value)
        self._generate_tree_probabilities()
        self._assign_biome()
        self._generate_tiles()
        self.chunk_raw = self.chunk.copy()


    # -- Surfaces Generation -- #

    def _generate_chunk_water_image(self) -> None:
        chunk = self.chunk

        TILE_W = 32 * SCALE
        TILE_H = 32 * SCALE  
        TREE_OVERHEAD = 96

        surf_w = 32 * self.chunk_size + TILE_W
        surf_h = 16 * self.chunk_size + TILE_H + 32 + TREE_OVERHEAD
        origin_x = TILE_W // 2
        out = []

        for i in range(8):
            surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            out.append(surface)

        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                tile = Tile(chunk[y, x])
                img = None

                blit_x = origin_x + (32 * self.chunk_size) // 2 + x * 16 - y * 16
                blit_y = x * 8 + y * 8 + TREE_OVERHEAD

                match tile:
                    case Tile.WATER_EXT:
                        for i in range(8):
                            img = self.background_assets[f"WATER_EXT_{i}"]
                            out[i].blit(img, (blit_x, blit_y))

                    case Tile.WATER_INT:
                        for i in range(8):
                            img = self.background_assets[f"WATER_INT_{i}"]
                            out[i].blit(img, (blit_x, blit_y))

                    case Tile.WATER_LEFT:
                        for i in range(8):
                            img = self.background_assets[f"WATER_LEFT_{i}"]
                            out[i].blit(img, (blit_x, blit_y))
                    
                    case Tile.WATER_RIGHT:
                        for i in range(8):
                            img = self.background_assets[f"WATER_RIGHT_{i}"]
                            out[i].blit(img, (blit_x, blit_y))
                        
                    case Tile.WATER_MID:
                        for i in range(8):
                            img = self.background_assets[f"WATER_MID_{i}"]
                            out[i].blit(img, (blit_x, blit_y))

                    case _:
                        continue

        self.water = out

    def _generate_chunk_image(self) -> None:
        chunk = self.chunk
        TILE_W = 32 * SCALE
        TILE_H = 32 * SCALE  
        TREE_OVERHEAD = 96

        surf_w = 32 * self.chunk_size + TILE_W
        surf_h = 16 * self.chunk_size + TILE_H + 32 + TREE_OVERHEAD


        summer_surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        autumn_surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        winter_surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        tree_surface_summer = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        tree_surface_autumn = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        tree_surface_winter = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)

        origin_x = TILE_W // 2

        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                tile = Tile(chunk[y, x])
                tree_img_summer = None
                tree_img_autumn = None
                tree_img_winter = None

                match tile:
                    case Tile.PLAIN:        
                        img_summer = self.background_assets[f"PLAIN_SUMMER"]
                        img_autumn = self.background_assets[f"PLAIN_AUTUMN"]
                        img_winter = self.background_assets[f"PLAIN_WINTER"]
                    case Tile.FOREST:       
                        img_summer = self.background_assets[f"PLAIN_SUMMER"]
                        img_autumn = self.background_assets[f"PLAIN_AUTUMN"]
                        img_winter = self.background_assets[f"PLAIN_WINTER"]
                        tree_prob = self.tree_probs[y, x]
                        if tree_prob <= TREE_PROBABILITY:
                            tree_img_summer = self.background_assets[f"tree_{self.tree_types[y, x]}_summer"]
                            tree_img_autumn = self.background_assets[f"tree_{self.tree_types[y, x]}_autumn"]
                            tree_img_winter = self.background_assets[f"tree_{self.tree_types[y, x]}_winter"]
                    case _:                 
                        continue

                blit_x = origin_x + (32 * self.chunk_size) // 2 + x * 16 - y * 16
                blit_y = x * 8 + y * 8 + TREE_OVERHEAD
                summer_surface.blit(img_summer, (blit_x, blit_y))
                autumn_surface.blit(img_autumn, (blit_x, blit_y))
                winter_surface.blit(img_winter, (blit_x, blit_y))
                
                

                if tree_img_summer is not None:
                    anchor_x, anchor_y = TREE_ANCHORS.get(self.tree_types[y, x], (tree_img_summer.get_width() // 2, tree_img_summer.get_height()))

                    tile_center_x = origin_x + (32 * self.chunk_size) // 2 + x * 16 - y * 16 + 16
                    tile_base_y   = x * 8 + y * 8 + 16 * SCALE + TREE_OVERHEAD

                    tree_blit_x = tile_center_x - anchor_x
                    tree_blit_y = tile_base_y - anchor_y

                    tree_surface_summer.blit(tree_img_summer, (tree_blit_x, tree_blit_y))
                    tree_surface_autumn.blit(tree_img_autumn, (tree_blit_x, tree_blit_y))
                    tree_surface_winter.blit(tree_img_winter, (tree_blit_x, tree_blit_y))
                    


        self.image["summer"] = summer_surface
        self.image["autumn"] = autumn_surface
        self.image["winter"] = winter_surface

        self.tree["summer"] = tree_surface_summer
        self.tree["autumn"] = tree_surface_autumn
        self.tree["winter"] = tree_surface_winter

        self._generate_chunk_water_image()


    # -- Rendering -- #

    def _draw_background_layer(self, screen : pygame.Surface, camera_pos: tuple[int, int], season: str) -> None: 
        cam_x, cam_y = camera_pos
        TILE_W = 32 * SCALE
        TILE_H = 16 * SCALE
        
        half_w = TILE_W // 2
        half_h = TILE_H // 2

        origin_x = half_w

        y0, x0 = self.index

        surface = self.image[season]
        iso_x = (x0 - y0) * half_w - origin_x
        iso_y = (x0 + y0) * half_h

        draw_x = iso_x - cam_x
        draw_y = iso_y - cam_y

        screen.blit(surface, (draw_x, draw_y))

    def _draw_tree_layer(self, screen : pygame.Surface, camera_pos: tuple[int, int], season: str) -> None:
        cam_x, cam_y = camera_pos
        TILE_W = 32 * SCALE
        TILE_H = 16 * SCALE
        
        half_w = TILE_W // 2
        half_h = TILE_H // 2

        origin_x = half_w

        y0, x0 = self.index


        surface = self.tree[season]

        iso_x = (x0 - y0) * half_w - origin_x
        iso_y = (x0 + y0) * half_h

        draw_x = iso_x - cam_x
        draw_y = iso_y - cam_y

        screen.blit(surface, (draw_x, draw_y))

    def _draw_water_layer(self, screen: pygame.Surface, camera_pos: tuple[int, int], frame: int) -> None:
        cam_x, cam_y = camera_pos
        TILE_W = 32 * SCALE
        TILE_H = 16 * SCALE
        
        half_w = TILE_W // 2
        half_h = TILE_H // 2

        origin_x = half_w

        y0, x0 = self.index

        
        surface = self.water[frame]
        iso_x = (x0 - y0) * half_w - origin_x
        iso_y = (x0 + y0) * half_h

        draw_x = iso_x - cam_x
        draw_y = iso_y - cam_y

        screen.blit(surface, (draw_x, draw_y))

    def _draw(self, screen: pygame.Surface, camera_pos : tuple[int, int], season: str, frame : int) -> None:
        self._draw_background_layer(screen, camera_pos, season)
        self._draw_water_layer(screen, camera_pos, frame)

        #FIXME here should be drawn the animals for z indexing

        self._draw_tree_layer(screen, camera_pos, season)






