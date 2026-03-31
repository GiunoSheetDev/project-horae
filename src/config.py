SCREENW, SCREENH = 1280, 720
SCALE = 1

GRIDW, GRIDH = 100, 100
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


DRAWABLE_CHUNKS = [(-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3),
                    (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (2, -2), 
                    (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3),  (0, -3), (1, -3)
                    ]


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


TREE_PROBABILITY = 0.33

TREE_ANCHORS = {
    "tree_0" : (14, 61),
    "tree_1" : (13, 76),
    "tree_2" : (19, 70),
    "tree_3" : (15, 69),
    "tree_4" : (14, 69),
    "tree_5" : (30, 77),
    "tree_6" : (29, 80),
    "tree_7" : (24, 83),
    "tree_8" : (42, 82),
    "tree_9" : (27, 79)
}
