import pygame
import numpy as np
import numpy.typing as npt
import random

from noise import pnoise2

from config import *
from chunk import Chunk

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

        self.chunks : dict[tuple[int, int], Chunk] = {}

        self.clock = pygame.time.Clock().tick(60)

        self.season = "summer"
        self.season_update_time = pygame.time.get_ticks()
        self.season_cooldown = 5 * 60 * 1000 * 6

        self.is_day = True
        self.day_update_time = pygame.time.get_ticks()
        self.day_cooldown = 5 * 60 * 1000
        self.day_mask = pygame.Surface((SCREENW, SCREENH), pygame.SRCALPHA)

        self.water_update_time = pygame.time.get_ticks()
        self.water_cooldown = 250
        self.water_frame = 0

        self._create_initial_world()

    def _load_assets(self) -> None:
        for img in os.listdir(ASSET_PATH_BACKGROUND):
            load_img = pygame.image.load(f"{ASSET_PATH_BACKGROUND}\\{img}").convert_alpha()
            load_img = pygame.transform.scale_by(load_img, SCALE)
            name = img.replace(".png", "")
            self.background_assets[name] = load_img


    # -- Chunk Generation -- #

    def _build_neighbor_dict(self, chunk_index: tuple[int, int]) -> dict[tuple[int, int], Chunk]:
        y0, x0 = chunk_index
        neighbors = {}
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nidx = (y0 + dy * self.chunk_size, x0 + dx * self.chunk_size)
            if nidx in self.chunks:
                neighbors[nidx] = self.chunks[nidx]
        return neighbors

    def _recollapse_neighbors(self, chunk_index: tuple[int, int]) -> None:
        y0, x0 = chunk_index
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            neighbor_index = (y0 + dy * self.chunk_size, x0 + dx * self.chunk_size)
            if neighbor_index in self.chunks:
                neighbor = self.chunks[neighbor_index]
                # restore raw tiles before re-collapsing
                neighbor.chunk = neighbor.chunk_raw.copy()
                neighbor._collapse_water(self._build_neighbor_dict(neighbor_index), is_recollapse=True)
                neighbor._generate_chunk_image(is_recollapse=True)

    def _generate_chunk(self, chunk_index: tuple[int, int]) -> None:
        chunk = Chunk(chunk_index, self.seed, self.background_assets)
        self.chunks[chunk_index] = chunk

        # water collapse needs neighbors, so redo it now that chunk is registered
        chunk.chunk = chunk.chunk_raw.copy()
        chunk._collapse_water(self._build_neighbor_dict(chunk_index))
        chunk._generate_chunk_image()

        # neighbors must recollapse now they have a new chunk on their border
        self._recollapse_neighbors(chunk_index)
        
    def _create_initial_world(self) -> None:
        chunk_indices = sorted(
            [(y, x) for y in range(0, self.gridh, self.chunk_size)
                    for x in range(0, self.gridw, self.chunk_size)]
        )

        # Create all chunks 
        for chunk_index in chunk_indices:
            self.chunks[chunk_index] = Chunk(chunk_index, self.seed, self.background_assets)

        # Collapse water with full neighbor awareness
        for chunk_index in chunk_indices:
            chunk = self.chunks[chunk_index]
            chunk.chunk = chunk.chunk_raw.copy()
            chunk._collapse_water(self._build_neighbor_dict(chunk_index))

        # Generate images
        for chunk_index in chunk_indices:
            chunk = self.chunks[chunk_index]
            chunk._generate_chunk_image(is_recollapse=False)

    # -- Rendering -- #

    def _get_drawable_chunks(self, chunk_index: tuple[int, int]) -> list:
        out = []
        y, x = chunk_index
        for offset in DRAWABLE_CHUNKS:
            dy, dx = offset
            ny, nx = y + dy * CHUNK_SIZE, x + dx * CHUNK_SIZE

            out.append((ny, nx))

        return out

    def _get_chunks_from_indices(self, chunk_indices: list[tuple[int, int]]) -> list[Chunk]:
        out = []
        for index in chunk_indices:
            if index not in self.chunks:
                self._generate_chunk(index)
            out.append(self.chunks[index])

        return out

    def _get_chunk_from_camera_pos(self, camera_pos: tuple[int, int]) -> tuple[int, int]:
        cam_x, cam_y = camera_pos
        TILE_W = 32 * SCALE
        TILE_H = 16 * SCALE
        
        half_w = TILE_W // 2
        half_h = TILE_H // 2

        origin_x = half_w
        origin_y = half_h

        #get center chunk
        screen_cx = SCREENW // 2
        screen_cy = SCREENH // 2

        world_x = screen_cx + cam_x + origin_x
        world_y = screen_cy + cam_y + origin_y

        tile_x = (world_x / half_w + world_y / half_h) / 2
        tile_y = (world_y / half_h - world_x / half_w) / 2

        tile_x -= CHUNK_SIZE / 2
        tile_y -= CHUNK_SIZE / 2

        tile_x = int(tile_x)
        tile_y = int(tile_y)

        chunk_x = (tile_x // CHUNK_SIZE) * CHUNK_SIZE
        chunk_y = (tile_y // CHUNK_SIZE) * CHUNK_SIZE

        selected_chunk = (chunk_y, chunk_x)

        return selected_chunk

    def _draw_background_layer(self, screen, camera_pos, drawable_chunks) -> None:
        sorted_chunks = sorted(drawable_chunks, key=lambda c: c.index[0] + c.index[1])

        for chunk in sorted_chunks:
            chunk._draw_background_layer(screen, camera_pos, self.season)

    def _draw_tree_layer(self, screen, camera_pos, drawable_chunks) -> None:
        sorted_chunks = sorted(drawable_chunks, key=lambda c: c.index[0] + c.index[1])

        for chunk in sorted_chunks:
            chunk._draw_tree_layer(screen, camera_pos, self.season)

    def _draw_water_layer(self, screen, camera_pos, drawable_chunks) -> None:
        sorted_chunks = sorted(drawable_chunks, key=lambda c: c.index[0] + c.index[1])

        for chunk in sorted_chunks:
            chunk._draw_water_layer(screen, camera_pos, self.water_frame)

    def _draw(self, screen, camera_pos: tuple[int, int]) -> None:
        selected_chunk = self._get_chunk_from_camera_pos(camera_pos)
        drawable_chunks_indices = self._get_drawable_chunks(selected_chunk)
        drawable_chunks = self._get_chunks_from_indices(drawable_chunks_indices)

        self._draw_background_layer(screen, camera_pos, drawable_chunks)
        self._draw_water_layer(screen, camera_pos, drawable_chunks)
        #here in the middle draw the animals so the z layer is behind tree but on top of background

        self._draw_tree_layer(screen, camera_pos, drawable_chunks)

        screen.blit(self.day_mask, (0,0))

    
    # -- Update -- #

    def _get_mask_color(self, percent: float) -> tuple[int,int,int,int]:
        '''
        Returns the interpolated RGBA color for a given percentage of the day.
        '''
        percent = percent % 1.0

        for i in range(len(MASK_COLOR) - 1):
            start_time, start_color = MASK_COLOR[i]
            end_time,   end_color   = MASK_COLOR[i + 1]

            if start_time <= percent <= end_time:
                t = (percent - start_time) / (end_time - start_time)
                
                r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
                a = int(start_color[3] + (end_color[3] - start_color[3]) * t)
                
                return (r, g, b, a)
        
        return MASK_COLOR[-1][1]

    def _update_day(self):
        current_time = pygame.time.get_ticks()
        percentage = current_time / self.day_cooldown
        color = self._get_mask_color(percentage)
        self.day_mask.fill(color)

    def _update_season(self):
        if pygame.time.get_ticks() - self.season_update_time >= self.season_cooldown:
            self.season_update_time = pygame.time.get_ticks()
            match self.season:
                case "summer":
                    self.season = "autumn"
                case "autumn":
                    self.season = "winter"
                case "winter":
                    self.season = "summer"

    def _update_water_animation(self):
        if pygame.time.get_ticks() - self.water_update_time >= self.water_cooldown:
            self.water_update_time = pygame.time.get_ticks()
            self.water_frame = (self.water_frame + 1) % 8


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
        if chunk_index not in self.chunks:
            self._generate_chunk(chunk_index)

    def update(self, screen, camera_pos):
        self._update_day()
        self._update_season()
        self._update_water_animation()
        self._draw(screen, camera_pos)


#FIXME change some trees (large ones) being rendered too high (sometimes on water)


if __name__ == "__main__":
    
    screen = pygame.display.set_mode((SCREENW, SCREENH))
    w = World()
    clock = pygame.time.Clock()

    camerax, cameray = 0, 0

    is_moving_left = is_moving_right = is_moving_up = is_moving_down = False

    is_running = True

    while is_running:
        #clock.tick(60)
        
        screen.fill((0, 0, 0))
        w.update(screen, (camerax, cameray))
        
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
                is_running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_running = False

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