import pgzrun
from map.game_map import (
    MAP_WIDTH,
    MAP_HEIGHT,
    TILE_GIDS,
    TILE_GIDS_COLISION,
    TILE_SIZE,
    MAP_DATA,
)

from pygame import Rect as rect

WIDTH = 800
HEIGHT = 600
TITLE = "Tiny Dungeon"

BLACK = (0, 0, 0)
MAP_BACKGROUND = (234, 165, 108)

player = None

tiles = {}


def init_game():
    global player

    player = Actor("player")
    player.pos = (WIDTH // 2, HEIGHT // 2)

    for tile_name in set(TILE_GIDS.values()):
        tiles[tile_name] = Actor(tile_name)


def draw():
    screen.fill(MAP_BACKGROUND)

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile_gid_original = MAP_DATA[y * MAP_WIDTH + x]
            tile_gid = tile_gid_original & 0x3FFFFFFF

            tile_name = TILE_GIDS.get(tile_gid)

            if tile_name:
                tile_actor = tiles[tile_name]
                tile_actor.topleft = (x * TILE_SIZE, y * TILE_SIZE)
                tile_actor.draw()

    player.draw()


def update():
    old_player_x = player.x
    old_player_y = player.y

    if keyboard.left:
        player.x -= 1
    if keyboard.right:
        player.x += 1

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile_gid = MAP_DATA[y * MAP_WIDTH + x] & 0x3FFFFFFF
            tile_name = TILE_GIDS.get(tile_gid)

            if tile_name in TILE_GIDS_COLISION.values():
                tile_rect = rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if player.colliderect(tile_rect):
                    player.x = old_player_x

    if keyboard.down:
        player.y += 1
    if keyboard.up:
        player.y -= 1

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile_gid = MAP_DATA[y * MAP_WIDTH + x] & 0x3FFFFFFF
            tile_name = TILE_GIDS.get(tile_gid)

            if tile_name in TILE_GIDS_COLISION.values():
                tile_rect = rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if player.colliderect(tile_rect):
                    player.y = old_player_y


init_game()

pgzrun.go()
