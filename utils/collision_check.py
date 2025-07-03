from pygame import Rect as rect

from map.game_map import (
    TILE_SIZE,
    MAP_HEIGHT,
    MAP_WIDTH,
    MAP_DATA,
    TILE_GIDS,
    TILE_GIDS_COLISION,
)

PLAYER_COLISION_WIDTH = TILE_SIZE - 4
PLAYER_COLISION_HEIGHT = TILE_SIZE - 4
PLAYER_COLISION_OFFSET_X = 2
PLAYER_COLISION_OFFSET_Y = 2


def collision_check(x_player_position, y_player_position):

    collision_check_rect = rect(
        x_player_position + PLAYER_COLISION_OFFSET_X - (PLAYER_COLISION_WIDTH / 2),
        y_player_position + PLAYER_COLISION_OFFSET_Y - (PLAYER_COLISION_HEIGHT / 2),
        PLAYER_COLISION_WIDTH,
        PLAYER_COLISION_HEIGHT,
    )

    for y_tile in range(MAP_HEIGHT):
        for x_tile in range(MAP_WIDTH):
            tile_gid = MAP_DATA[y_tile * MAP_WIDTH + x_tile] & 0x3FFFFFFF
            tile_name = TILE_GIDS.get(tile_gid)

            if tile_name in TILE_GIDS_COLISION.values():
                tile_rect = rect(
                    x_tile * TILE_SIZE, y_tile * TILE_SIZE, TILE_SIZE, TILE_SIZE
                )
                if collision_check_rect.colliderect(tile_rect):
                    return False
    return True
