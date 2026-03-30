SCREENW, SCREENH = 1280, 720
SCALE = 1

GRIDW, GRIDH = 200, 200
CHUNK_SIZE = 20

CHUNK_IMAGE_SIZE = (32 * CHUNK_SIZE, 16 * CHUNK_SIZE + 32)


import os
ASSET_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.pardir,
    "assets"
)

ASSET_PATH_BACKGROUND = os.path.join(
    ASSET_PATH,
    "Isometric Environment",
    "Tiles"
)

ASSET_PATH_ANIMALS = os.path.join(
    ASSET_PATH,
    "Isometric Animals"
)


from enum import Enum

class Tile(Enum):
    EMPTY = 0
    PLAIN = 1
    FOREST= 2
    WATER = 3
    WATER_EXT = 4
    WATER_INT = 5
    WATER_LEFT = 6
    WATER_RIGHT = 7
    WATER_MID = 8

class Biome(Enum):
    EMPTY = 0
    OCEAN = 1
    FOREST = 2
    PLAIN = 3






BIOME_SCALE = 0.012   # lower = bigger biome regions
TILE_SCALE  = 0.08    # lower = bigger tile blobs within a biome