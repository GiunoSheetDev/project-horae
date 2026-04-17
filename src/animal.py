import os
import pygame

from config import *
from random import randint, sample, choice
from heapq import heappush, heappop


class Animal:
    def __init__(self, world_chunks : dict):
        self.world_chunks = world_chunks

        self.animation_assets = {}
        self._load_assets()

        self.clock = pygame.time.Clock().tick(FPS)

        # -- Animations -- #

        self.animation_type = "idle"
        self.animation_direction = "north-east"
        self.animation_frame = 0
        self.animation_cooldown = 100
        self.animation_update_time = pygame.time.get_ticks()
        self.image = self.animation_assets[self.animation_type][self.animation_direction][self.animation_frame]


        # -- Needs -- #

        self.max_hunger = 400
        self.hunger = randint(self.max_hunger // 2, self.max_hunger)
        self.is_hungry = False
        self.max_thirst = 400
        self.thirst = randint(self.max_thirst // 2, self.max_thirst)
        self.is_thirsty = False


        # -- Movement -- #
        self.position_chunk, self.position_local = self._get_initial_position(Tile.PLAIN, Tile.FOREST)
        self.movement_target_chunk, self.movement_target_local = self._get_random_tile(Tile.PLAIN, Tile.FOREST)
        self.path = self.get_path(self.position_chunk, self.position_local, self.movement_target_chunk, self.movement_target_local)
        self.t = 0 # the progress from 0 to 1 when moving to one tile to the next
        self.speed = 0.05
        self.next_chunk, self.next_local = None, None
        


    def _load_assets(self) -> None:
        animal_path = os.path.join(ASSET_PATH_ANIMALS, self.__class__.__name__.lower())
        
        for anim_name in os.listdir(animal_path):
            animation_path = os.path.join(animal_path, anim_name)
            self.animation_assets[anim_name] = {}
            
            for direction in os.listdir(animation_path):
                img_path = os.path.join(animation_path, direction)
                out = []
                
                for img in os.listdir(img_path):
                    load_img = pygame.image.load(os.path.join(img_path, img)).convert_alpha()
                    load_img = pygame.transform.scale_by(load_img, SCALE)
                    out.append(load_img)
                
                self.animation_assets[anim_name][direction] = out


    # -- Animations -- #

    def _reset_animation(self) -> None:
        self.animation_frame = 0
        self.animation_update_time = pygame.time.get_ticks()
        self.image = self.animation_assets[self.animation_type][self.animation_direction][self.animation_frame]

    def _update_animation_frame(self) -> None:
        if pygame.time.get_ticks() - self.animation_update_time >= self.animation_cooldown:
            self.animation_update_time = pygame.time.get_ticks()
            self.animation_frame = (self.animation_frame + 1) % len(self.animation_assets[self.animation_type][self.animation_direction])
            self.image = self.animation_assets[self.animation_type][self.animation_direction][self.animation_frame]

    def _update_animation_direction(self, new_dir: str) -> None:
        self.animation_direction = new_dir
        self._reset_animation()

    def _update_animation_type(self, new_type: str) -> None:
        self.animation_type = new_type
        self._reset_animation()

    def draw(self, screen: pygame.Surface, camera_pos: tuple[int, int]) -> None:
        cam_x, cam_y = camera_pos
        TILE_W = 32 * SCALE
        TILE_H = 16 * SCALE
        half_w = TILE_W // 2
        half_h = TILE_H // 2
        TREE_OVERHEAD = 96
        origin_x = half_w  # = 16

        def tile_to_iso(chunk, local):
            chk_y, chk_x = chunk
            loc_y, loc_x = local
            
            x = (chk_x - chk_y) * half_w - origin_x + origin_x + (32 * CHUNK_SIZE) // 2 + loc_x * 16 - loc_y * 16
            y = (chk_x + chk_y) * half_h + loc_x * 8 + loc_y * 8 + TREE_OVERHEAD
            return x, y

        cur_x, cur_y = tile_to_iso(self.position_chunk, self.position_local)

        if self.next_chunk is not None:
            nxt_x, nxt_y = tile_to_iso(self.next_chunk, self.next_local)
            world_x = cur_x + (nxt_x - cur_x) * self.t
            world_y = cur_y + (nxt_y - cur_y) * self.t
        else:
            world_x, world_y = cur_x, cur_y

        draw_x = world_x - cam_x + half_w - self.image.get_width() // 2
        draw_y = world_y - cam_y - (self.image.get_height() - half_h)

        screen.blit(self.image, (draw_x, draw_y))

    # -- Needs -- #

    def _handle_needs(self) -> None:
        self.hunger -= 0.2
        self.thirst -= 0.2

        if self.thirst <= 0:
            self.thirst = 0
            self.is_thirsty = True

        if self.hunger <= 0:
            self.hunger = 0
            self.is_hungry = True


    # -- Movement -- #
    def _get_initial_position(self, *tiles):
        valid_positions = []

        for chunk_index, chunk in self.world_chunks.items():
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    if Tile(chunk.chunk_raw[y, x]) in tiles:
                        valid_positions.append((chunk_index, (y, x)))

        if not valid_positions:
            for row in chunk.chunk_raw:
                print(row)
            raise ValueError("No valid tiles found")

        return choice(valid_positions)

    def heuristic(self, chunk, local, goals):
            ''' Manhattan Distance '''
            cy, cx = chunk
            ly, lx = local

            return min(
                abs((cy * CHUNK_SIZE + ly) - (g_chunk[0] * CHUNK_SIZE + g_local[0])) +
                abs((cx * CHUNK_SIZE + lx) - (g_chunk[1] * CHUNK_SIZE + g_local[1]))
                for g_chunk, g_local in goals
            )
        
    def get_chunks_in_radius(self, center, radius):
            ''' Returns all pregenerated chunks indices in a radius'''
            cy, cx = center
            chunks = []

            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius +1):
                    candidate = (cy + dy * CHUNK_SIZE, cx + dx * CHUNK_SIZE)
                    if candidate in self.world_chunks:
                        chunks.append(candidate)

            return chunks

    def get_path(self, start_chunk: tuple[int, int], start_local: tuple[int, int], end_chunk: tuple[int, int], end_local: tuple[int, int]) -> list | None:
        '''
        A* from (start_chunk, start_local) to (end_chunk, end_local).
        Water tiles are unwalkable.
        Returns path as list of (chunk, local) tuples, or None if unreachable.
        '''
        if start_chunk == end_chunk and start_local == end_local:
            return [(start_chunk, start_local)]

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        goal_list = [(end_chunk, end_local)]

        sy, sx = start_chunk
        ey, ex = end_chunk
        chunk_dist = max(abs(ey - sy) // CHUNK_SIZE, abs(ex - sx) // CHUNK_SIZE)
        max_radius = max(chunk_dist + 1, 5)

        chunks_to_search = set(self.get_chunks_in_radius(start_chunk, max_radius))

        open_set = []
        heappush(open_set, (
            self.heuristic(start_chunk, start_local, goal_list),
            0,
            start_chunk,
            start_local,
            [(start_chunk, start_local)]
        ))

        visited = set()

        while open_set:
            f, g, chunk, local, path = heappop(open_set)

            if (chunk, local) in visited:
                continue
            visited.add((chunk, local))

            if chunk == end_chunk and local == end_local:
                return path

            cy, cx = chunk
            y, x = local

            for dy, dx in directions:
                ny, nx = y + dy, x + dx
                nchunk = (cy, cx)

                if ny < 0:
                    nchunk = (cy - CHUNK_SIZE, cx)
                    ny += CHUNK_SIZE
                elif ny >= CHUNK_SIZE:
                    nchunk = (cy + CHUNK_SIZE, cx)
                    ny -= CHUNK_SIZE

                if nx < 0:
                    nchunk = (nchunk[0], cx - CHUNK_SIZE)
                    nx += CHUNK_SIZE
                elif nx >= CHUNK_SIZE:
                    nchunk = (nchunk[0], cx + CHUNK_SIZE)
                    nx -= CHUNK_SIZE

                if nchunk not in chunks_to_search:
                    continue
                if (nchunk, (ny, nx)) in visited:
                    continue
                if self.world_chunks[nchunk].chunk_raw[ny, nx] == Tile.WATER:
                    continue

                new_g = g + 1
                heappush(open_set, (
                    new_g + self.heuristic(nchunk, (ny, nx), goal_list),
                    new_g,
                    nchunk,
                    (ny, nx),
                    path + [(nchunk, (ny, nx))]
                ))

        return None

    def _get_random_tile(self, *tiles: Tile) -> tuple[tuple[int, int], tuple[int, int]]:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                    (1, 1), (1, -1), (-1, 1), (-1, -1)]
        max_attempts_per_chunk = 10

        shuffled = sample(directions, len(directions))

        for dy, dx in shuffled:
            chunk_index = (
                self.position_chunk[0] + dy * CHUNK_SIZE,
                self.position_chunk[1] + dx * CHUNK_SIZE
            )

            # Skip chunks that haven't been generated yet
            if chunk_index not in self.world_chunks:
                continue

            chunk_raw = self.world_chunks[chunk_index].chunk_raw

            for _ in range(max_attempts_per_chunk):
                y = randint(0, CHUNK_SIZE - 1)
                x = randint(0, CHUNK_SIZE - 1)

                if Tile(chunk_raw[y, x]) in tiles:
                    return chunk_index, (y, x)

    def _update_movement_target(self) -> None:
        if self.movement_target_chunk is not None:
            return
        
        if self.is_thirsty:
            self.movement_target_chunk, self.movement_target_local = self._get_random_tile(Tile.WATER_EXT, Tile.WATER_INT, Tile.WATER_LEFT, Tile.WATER_MID, Tile.WATER_RIGHT)
            self.path = self.get_path(self.position_chunk, self.position_local, self.movement_target_chunk, self.movement_target_local)
            self.path.pop() #remove last index so it never works on water 
            return
        
        if self.is_hungry:
            self.movement_target_chunk, self.movement_target_local = self._get_random_tile(Tile.PLAIN)
            self.path = self.get_path(self.position_chunk, self.position_local, self.movement_target_chunk, self.movement_target_local)
            self.path.pop() #remove last index so it never works on grass but "faces it" for idle animation
            return
        
        self._get_random_tile(Tile.PLAIN, Tile.FOREST)

    def _move(self) -> None:
        if self.next_chunk is None:
            if not self.path:
                self._update_animation_type("idle")
                return
            self.next_chunk, self.next_local = self.path.pop(0)
            self._update_animation_type("walk")

        self.t += self.speed

        if self.t >= 1.0:
            self.position_chunk = self.next_chunk
            self.position_local = self.next_local
            self.next_chunk, self.next_local = None, None
            self.t = 0.0
            return

        cy, cx = self.position_chunk
        ly, lx = self.position_local
        ncy, ncx = self.next_chunk
        ny, nx = self.next_local  

        dy = (ncy * CHUNK_SIZE + ny) - (cy * CHUNK_SIZE + ly)
        dx = (ncx * CHUNK_SIZE + nx) - (cx * CHUNK_SIZE + lx)

        match (dx, dy):
            case (1, 0):  direction = "south-east"
            case (0, 1):  direction = "south-west"
            case (-1, 0): direction = "north-west"
            case (0, -1): direction = "north-east"
            case _:       direction = self.animation_direction

        if direction != self.animation_direction:
            self._update_animation_direction(direction)

    # -- Update -- #

    def update(self):
        self._handle_needs()
        self._update_animation_frame()
        self._move()      
    


class Stag(Animal):
    def __init__(self, world_chunks):
        super().__init__(world_chunks)

class Badger(Animal):
    def __init__(self, world_chunks):
        super().__init__(world_chunks)

class Boar(Animal):
    def __init__(self, world_chunks):
        super().__init__(world_chunks)

class Wolf(Animal):
    def __init__(self, world_chunks):
        super().__init__(world_chunks)


class AnimalManager:
    '''
    Class that assigns animals to chunks
    '''
    def __init__(self, world_chunks: dict):
        self.chunks = world_chunks
        self.animals = set()

    def _reset_chunks_animals(self) -> None:
        for chunk in self.chunks.values():
            chunk.animals = set()

    def _update_chunks(self) -> None:
        self._reset_chunks_animals()

        animal: Animal
        for animal in self.animals:
            self.chunks[animal.position_chunk].animals.add(animal)



if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREENW, SCREENH))
    

    a = Stag()

    print(a.animation_assets["idle"].keys())








