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

from utils import collision_check

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

player_attack_sprites = [
    Actor("player_attacking_1"),
    Actor("player_attacking_2"),
    Actor("player_attacking_3"),
    Actor("player_attacking_4"),
    Actor("player_attacking_5"),
]

current_animation_sprites = player_idle_sprites
current_sprite_index = 0
animation_timer = 0.0
animation_speed_idle = 0.3
animation_speed_walk = 0.1

animation_speed_attack = 0.1
player_attacking = False


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


def player_attack_end():
    global player_attacking
    player_attacking = False


def update():
    global current_animation_sprites, current_sprite_index, animation_timer, player_attacking

    old_player_x = player.x
    old_player_y = player.y

    player_walking = False

    if player_attacking:
        pass
    elif keyboard.space:
        player_attacking = True
        player_walking = False
        current_animation_sprites = player_attack_sprites
        current_sprite_index = 0
        animation_timer = 0.0
    else:
        if keyboard.left:
            player.x -= 1
            player_walking = True
        if keyboard.right:
            player.x += 1
            player_walking = True

        if not collision_check.collision_check(player.x, player.y):
            player.x = old_player_x

        if keyboard.down:
            player.y += 1
            player_walking = True
        if keyboard.up:
            player.y -= 1
            player_walking = True

        if not collision_check.collision_check(player.x, player.y):
            player.y = old_player_y

    animation_timer += 1 / 60

    if player_attacking:
        speed_used = animation_speed_attack
    elif player_walking:
        current_animation_sprites = player_walk_sprites
        speed_used = animation_speed_walk
    else:
        current_animation_sprites = player_idle_sprites
        speed_used = animation_speed_idle

    if animation_timer >= speed_used:
        animation_timer = 0
        current_sprite_index = current_sprite_index + 1

        if (
            current_animation_sprites == player_attack_sprites
            and current_sprite_index >= len(current_animation_sprites)
        ):
            current_sprite_index = len(current_animation_sprites) - 1
            player_attack_end()
        else:
            current_sprite_index %= len(current_animation_sprites)

        player.image = current_animation_sprites[current_sprite_index].image


init_game()

pgzrun.go()
