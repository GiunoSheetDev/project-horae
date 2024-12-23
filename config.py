import os

SCREEN_W = 800
SCREEN_H = 800



# wave function collapse ############################
BACKGROUND_STARTING_X = 350
BACKGROUND_STARTING_Y = 200
SCALE = 1
MAP_ROW_LEN = 20




ASSET_PATH = os.path.join("assets", "Isometric Environment", "Tiles")

TILE_DARK_GRASS_DIRT = os.path.join(ASSET_PATH, "dark_grass_dirt.png")
TILE_DARK_GRASS_ROCK = os.path.join(ASSET_PATH, "dark_grass_rock.png")
TILE_DIRT_FULL = os.path.join(ASSET_PATH, "dirt_full.png")
TILE_LIGHT_GRASS_DIRT = os.path.join(ASSET_PATH, "light_grass_dirt.png")
TILE_LIGHT_GRASS_ROCK = os.path.join(ASSET_PATH, "light_grass_rock.png")
TILE_ROCK_FULL = os.path.join(ASSET_PATH, "rock_full.png")
TILE_WATER_LEFT = os.path.join(ASSET_PATH, "water_left.png")
TILE_WATER_RIGHT = os.path.join(ASSET_PATH, "water_right.png")
TILE_WATER_EXTERNAL_MIDDLE = os.path.join(ASSET_PATH, "water_external_middle.png")
TILE_WATER_INTERNAL_MIDDLE = os.path.join(ASSET_PATH, "water_internal_middle.png")
TILE_WATER_MIDDLE = os.path.join(ASSET_PATH, "water_middle.png")


NORTH_EAST = 0
SOUTH_EAST = 1
SOUTH_WEST = 2
NORTH_WEST = 3

''''''
tilesRules = { #[NORTH-EAST, SOUTH-EAST, SOUTH-WEST, NORTH-WEST]
    TILE_DARK_GRASS_DIRT : {
        NORTH_EAST: [TILE_DARK_GRASS_DIRT, TILE_WATER_MIDDLE, TILE_DIRT_FULL], 
        SOUTH_EAST: [TILE_DARK_GRASS_DIRT, TILE_WATER_RIGHT, TILE_DIRT_FULL, TILE_WATER_INTERNAL_MIDDLE],
        SOUTH_WEST: [TILE_DARK_GRASS_DIRT, TILE_WATER_LEFT, TILE_DIRT_FULL, TILE_WATER_INTERNAL_MIDDLE],
        NORTH_WEST: [TILE_DARK_GRASS_DIRT, TILE_WATER_MIDDLE, TILE_DIRT_FULL],
        },

    TILE_DARK_GRASS_ROCK : {
        NORTH_EAST: [TILE_DARK_GRASS_ROCK, TILE_WATER_MIDDLE],
        SOUTH_EAST: [TILE_DARK_GRASS_ROCK, TILE_WATER_RIGHT, TILE_WATER_INTERNAL_MIDDLE],
        SOUTH_WEST: [TILE_DARK_GRASS_ROCK, TILE_WATER_LEFT, TILE_WATER_INTERNAL_MIDDLE],
        NORTH_WEST: [TILE_DARK_GRASS_ROCK, TILE_WATER_MIDDLE],
        },
                                                 

    TILE_DIRT_FULL : {
        NORTH_EAST: [TILE_LIGHT_GRASS_DIRT, TILE_DARK_GRASS_DIRT, TILE_DIRT_FULL, TILE_WATER_MIDDLE],
        SOUTH_EAST: [TILE_LIGHT_GRASS_DIRT, TILE_DARK_GRASS_DIRT, TILE_DIRT_FULL, TILE_WATER_RIGHT, TILE_WATER_INTERNAL_MIDDLE],
        SOUTH_WEST: [TILE_LIGHT_GRASS_DIRT, TILE_DARK_GRASS_DIRT, TILE_DIRT_FULL, TILE_WATER_LEFT, TILE_WATER_INTERNAL_MIDDLE],
        NORTH_WEST: [TILE_LIGHT_GRASS_DIRT, TILE_DARK_GRASS_DIRT, TILE_DIRT_FULL, TILE_WATER_MIDDLE]
        },

    TILE_LIGHT_GRASS_DIRT :{
        NORTH_EAST: [TILE_LIGHT_GRASS_DIRT, TILE_DIRT_FULL], 
        SOUTH_EAST: [TILE_LIGHT_GRASS_DIRT, TILE_DIRT_FULL], 
        SOUTH_WEST: [TILE_LIGHT_GRASS_DIRT, TILE_DIRT_FULL], 
        NORTH_WEST: [TILE_LIGHT_GRASS_DIRT, TILE_DIRT_FULL]
        },

    TILE_LIGHT_GRASS_ROCK : {
        NORTH_EAST: [TILE_LIGHT_GRASS_ROCK, TILE_ROCK_FULL],
        SOUTH_EAST: [TILE_LIGHT_GRASS_ROCK, TILE_ROCK_FULL],
        SOUTH_WEST: [TILE_LIGHT_GRASS_ROCK, TILE_ROCK_FULL],
        NORTH_WEST: [TILE_LIGHT_GRASS_ROCK, TILE_ROCK_FULL],
        },

    TILE_ROCK_FULL : {
        NORTH_EAST: [TILE_LIGHT_GRASS_ROCK, TILE_ROCK_FULL],
        SOUTH_EAST: [TILE_LIGHT_GRASS_ROCK, TILE_ROCK_FULL],
        SOUTH_WEST: [TILE_LIGHT_GRASS_ROCK, TILE_ROCK_FULL],
        NORTH_WEST: [TILE_LIGHT_GRASS_ROCK, TILE_ROCK_FULL],
        },

    TILE_WATER_LEFT : {
        NORTH_EAST: [TILE_DARK_GRASS_DIRT, TILE_DARK_GRASS_ROCK, TILE_DIRT_FULL], 
        SOUTH_EAST: [TILE_WATER_MIDDLE, TILE_WATER_LEFT, TILE_WATER_EXTERNAL_MIDDLE], 
        SOUTH_WEST: [TILE_WATER_MIDDLE], 
        NORTH_WEST: [TILE_WATER_MIDDLE, TILE_WATER_LEFT, TILE_WATER_INTERNAL_MIDDLE]
        },

    TILE_WATER_RIGHT : {
        NORTH_EAST: [TILE_WATER_RIGHT, TILE_WATER_MIDDLE, TILE_WATER_INTERNAL_MIDDLE], 
        SOUTH_EAST: [TILE_WATER_MIDDLE], 
        SOUTH_WEST: [TILE_WATER_RIGHT, TILE_WATER_MIDDLE, TILE_WATER_EXTERNAL_MIDDLE],
        NORTH_WEST: [TILE_DARK_GRASS_DIRT, TILE_DARK_GRASS_ROCK, TILE_DIRT_FULL]
        },
    
    TILE_WATER_EXTERNAL_MIDDLE : {
        NORTH_EAST: [TILE_WATER_RIGHT],
        SOUTH_EAST: [TILE_WATER_MIDDLE],
        SOUTH_WEST: [TILE_WATER_MIDDLE],
        NORTH_WEST: [TILE_WATER_LEFT]
        },

    TILE_WATER_INTERNAL_MIDDLE: {
        NORTH_EAST: [TILE_DARK_GRASS_DIRT, TILE_DARK_GRASS_ROCK, TILE_DIRT_FULL],
        SOUTH_EAST: [TILE_WATER_LEFT],
        SOUTH_WEST: [TILE_WATER_RIGHT],
        NORTH_WEST: [TILE_DARK_GRASS_DIRT, TILE_DARK_GRASS_ROCK, TILE_DIRT_FULL]
        },

    TILE_WATER_MIDDLE: {
        NORTH_EAST: [TILE_WATER_LEFT, TILE_WATER_RIGHT, TILE_WATER_EXTERNAL_MIDDLE, TILE_WATER_MIDDLE],
        SOUTH_EAST: [TILE_DARK_GRASS_DIRT, TILE_DARK_GRASS_ROCK, TILE_DIRT_FULL, TILE_WATER_LEFT, TILE_WATER_MIDDLE],
        SOUTH_WEST: [TILE_DARK_GRASS_DIRT, TILE_DARK_GRASS_ROCK, TILE_DIRT_FULL, TILE_WATER_RIGHT, TILE_WATER_MIDDLE],
        NORTH_WEST: [TILE_WATER_LEFT, TILE_WATER_RIGHT, TILE_WATER_EXTERNAL_MIDDLE, TILE_WATER_MIDDLE]
    }
}






tilesWeights = {
    TILE_DARK_GRASS_DIRT : 32,
    TILE_DARK_GRASS_ROCK : 32,
    TILE_DIRT_FULL : 4,
    TILE_LIGHT_GRASS_DIRT : 8,
    TILE_LIGHT_GRASS_ROCK : 8,
    TILE_ROCK_FULL : 4,
    TILE_WATER_RIGHT : 4,
    TILE_WATER_LEFT : 4,
    TILE_WATER_EXTERNAL_MIDDLE: 2,
    TILE_WATER_INTERNAL_MIDDLE: 2,
    TILE_WATER_MIDDLE : 2
}

################################################################