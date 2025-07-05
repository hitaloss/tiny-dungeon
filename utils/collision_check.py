from pygame import Rect as rect

from map.game_map import (
    TILE_SIZE,
    MAP_HEIGHT,
    MAP_WIDTH,
    MAP_DATA,
    TILE_GIDS,
    TILE_GIDS_COLISION,
)

from config import (
    PLAYER_COLISION_WIDTH,
    PLAYER_COLISION_HEIGHT,
    PLAYER_COLISION_OFFSET_X,
    PLAYER_COLISION_OFFSET_Y,
    SKELETON_COLISION_WIDTH,
    SKELETON_COLISION_HEIGHT,
    SKELETON_COLISION_OFFSET_X,
    SKELETON_COLISION_OFFSET_Y,
)


def collision_check(x_player_position, y_player_position, skeleton_obj):

    player_hitbox = rect(0, 0, PLAYER_COLISION_WIDTH, PLAYER_COLISION_HEIGHT)
    player_hitbox.center = (x_player_position, y_player_position)
    player_hitbox.move_ip(PLAYER_COLISION_OFFSET_X, PLAYER_COLISION_OFFSET_Y)

    for y_tile in range(MAP_HEIGHT):
        for x_tile in range(MAP_WIDTH):
            tile_gid = MAP_DATA[y_tile * MAP_WIDTH + x_tile] & 0x3FFFFFFF
            tile_name = TILE_GIDS.get(tile_gid)

            if tile_name in TILE_GIDS_COLISION.values():
                tile_rect = rect(
                    x_tile * TILE_SIZE, y_tile * TILE_SIZE, TILE_SIZE, TILE_SIZE
                )
                if player_hitbox.colliderect(tile_rect):
                    return False

    if skeleton_obj:
        skeleton_hitbox = rect(0, 0, SKELETON_COLISION_WIDTH, SKELETON_COLISION_HEIGHT)
        skeleton_hitbox.center = skeleton_obj.center
        skeleton_hitbox.move_ip(SKELETON_COLISION_OFFSET_X, SKELETON_COLISION_OFFSET_Y)

        if player_hitbox.colliderect(skeleton_hitbox):
            return False

    return True
