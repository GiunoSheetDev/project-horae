import os
import pygame

from config import *
from random import randint, sample


class Animal:
    def __init__(self):
        self.animation_assets = {}
        self._load_assets()

        self.clock = pygame.time.Clock().tick(FPS)


        self.animation_type = "idle"
        self.animation_direction = "north-east"
        self.animation_frame = 0
        self.animation_cooldown = 100
        self.animation_update_time = pygame.time.get_ticks()
        self.image = self.animation_assets[self.animation_type][self.animation_direction][self.animation_frame]


        self.max_hunger = 400
        self.hunger = randint(self.max_hunger // 2, self.max_hunger)
        self.is_hungry = False
        self.max_thirst = 400
        self.thirst = randint(self.max_thirst // 2, self.max_thirst)
        self.is_thirsty = False


        self.movement_target_chunk = None
        self.movement_target_local_coordinates = None



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
            self.animation_frame = (self.animation_frame) % len(self.animation_assets[self.animation_type][self.animation_direction])
            self.image = self.animation_assets[self.animation_type][self.animation_direction][self.animation_frame]

    def _update_animation_direction(self, new_dir: str) -> None:
        self.animation_direction = new_dir
        self._reset_animation()

    def _update_animation_type(self, new_type: str) -> None:
        self.animation_type = new_type
        self._reset_animation()


    # -- Movement -- #
    #TODO figure out how to merge multiple chunks

    def _is_tile_reachable(self, start_pos_chunk: tuple[int, int], start_pos_local : tuple[int, int], end_pos_chunk : tuple[int, int], end_pos_local : tuple[int, int], world_path : dict) -> bool:
        pass
            
            #TODO make a flood list that so that tiles that are reachable have the same num, 
            #if 2 meet get the dominant one from running count and replace all less domninant into more dominant

    def _get_closest_tile(self, *args : Tile) -> tuple[tuple[int, int], tuple[int, int]]:
        pass

    def _get_random_tile(self, *args : Tile) -> tuple[tuple[int, int], tuple[int, int]]:
        pass

    def _update_movement_target(self) -> None:
        if self.movement_target_chunk is not None:
            return
        
        if self.is_thirsty:
            self.movement_target_chunk, self.movement_target_local_coordinates = self._get_closest_tile(Tile.WATER_EXT, Tile.WATER_INT, Tile.WATER_LEFT, Tile.WATER_MID, Tile.WATER_RIGHT)
            '''
            self._get_closest_tile will be something like
            def _get_closest_tiles(*args : Tile) -> tuple[tuple[int, int], tuple[int, int]] 

                where first return arg is chunk_index and the second the [y, x]
            
            '''
            return
        
        if self.is_hungry:
            self.movement_target_chunk, self.movement_target_local_coordinates = self._get_closest_tile(Tile.PLAIN)
            return
        
        self._get_random_tile(Tile.PLAIN, Tile.FOREST)




class Stag(Animal):
    def __init__(self):
        super().__init__()

class Badger(Animal):
    def __init__(self):
        super().__init__()

class Boar(Animal):
    def __init__(self):
        super().__init__()

class Wolf(Animal):
    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREENW, SCREENH))

    a = Stag()

    print(a.animation_assets["idle"].keys())








