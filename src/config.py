SCREENW, SCREENH = 1280, 720
SCALE = 1

GRIDW, GRIDH = 200, 200
CHUNK_SIZE = 20

CHUNK_IMAGE_WIDTH = 32 * CHUNK_SIZE
CHUNK_IMAGE_HEIGHT = 16 * CHUNK_SIZE + 32
CHUNK_IMAGE_SIZE = (CHUNK_IMAGE_WIDTH, CHUNK_IMAGE_HEIGHT)


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


DRAWABLE_CHUNKS = [(-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3)]


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