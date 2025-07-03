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

tiles = {}

player = None

player_sprites = {}
player_current_sprite = "idle"
player_current_sprite_index = 0
player_sprite_timer = 0

player_idle_sprites = [
    Actor("player_idle_1"),
    Actor("player_idle_2"),
    Actor("player_idle_3"),
    Actor("player_idle_4"),
]

player_walk_sprites = [
    Actor("player_walking_1"),
    Actor("player_walking_2"),
    Actor("player_walking_3"),
    Actor("player_walking_4"),
]

current_animation_sprites = player_idle_sprites
current_sprite_index = 0
animation_timer = 0.0
animation_speed_idle = 0.3
animation_speed_walk = 0.1


def init_game():
    global player, current_animation_sprites

    player = current_animation_sprites[0]
    player.pos = (WIDTH // 2, HEIGHT // 2)
    player.width = TILE_SIZE
    player.height = TILE_SIZE

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


PLAYER_COLISION_WIDTH = TILE_SIZE - 4
PLAYER_COLISION_HEIGHT = TILE_SIZE - 4
PLAYER_COLISION_OFFSET_X = 2
PLAYER_COLISION_OFFSET_Y = 2


def update():
    global current_animation_sprites, current_sprite_index, animation_timer

    old_player_x = player.x
    old_player_y = player.y

    player_walking = False

    if keyboard.left:
        player.x -= 1
        player_walking = True
    if keyboard.right:
        player.x += 1
        player_walking = True

    player_collision_check_rect_x = rect(
        player.x + PLAYER_COLISION_OFFSET_X - (PLAYER_COLISION_WIDTH / 2),
        player.y + PLAYER_COLISION_OFFSET_Y - (PLAYER_COLISION_HEIGHT / 2),
        PLAYER_COLISION_WIDTH,
        PLAYER_COLISION_HEIGHT,
    )

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile_gid = MAP_DATA[y * MAP_WIDTH + x] & 0x3FFFFFFF
            tile_name = TILE_GIDS.get(tile_gid)

            if tile_name in TILE_GIDS_COLISION.values():
                tile_rect = rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if player_collision_check_rect_x.colliderect(tile_rect):
                    player.x = old_player_x

    if keyboard.down:
        player.y += 1
        player_walking = True
    if keyboard.up:
        player.y -= 1
        player_walking = True

    player_collision_check_rect_y = rect(
        player.x + PLAYER_COLISION_OFFSET_X - (PLAYER_COLISION_WIDTH / 2),
        player.y + PLAYER_COLISION_OFFSET_Y - (PLAYER_COLISION_HEIGHT / 2),
        PLAYER_COLISION_WIDTH,
        PLAYER_COLISION_HEIGHT,
    )

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile_gid = MAP_DATA[y * MAP_WIDTH + x] & 0x3FFFFFFF
            tile_name = TILE_GIDS.get(tile_gid)

            if tile_name in TILE_GIDS_COLISION.values():
                tile_rect = rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if player_collision_check_rect_y.colliderect(tile_rect):
                    player.y = old_player_y

    animation_timer += 1 / 60

    if player_walking:
        current_animation_sprites = player_walk_sprites
        speed_used = animation_speed_walk
    else:
        current_animation_sprites = player_idle_sprites
        speed_used = animation_speed_idle

    if animation_timer >= speed_used:
        animation_timer = 0
        current_sprite_index = (current_sprite_index + 1) % len(
            current_animation_sprites
        )
        player.image = current_animation_sprites[current_sprite_index].image


init_game()

pgzrun.go()
