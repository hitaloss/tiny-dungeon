import pgzrun
from pgzero.actor import Actor
from pgzero.keyboard import keyboard


# A excessão que foi passada no teste
from pygame import Rect as rect

from config import (
    DIR_LEFT,
    DIR_RIGHT,
    DIR_UP,
    DIR_DOWN,
)

from map.game_map import (
    MAP_WIDTH,
    MAP_HEIGHT,
    TILE_GIDS,
    TILE_SIZE,
    MAP_DATA,
)


from sprites.player_sprites import (
    player_idle_down_sprites,
)
from utils import collision_check
from utils.animation_manager import update_player_animation

WIDTH = 800
HEIGHT = 600
TITLE = "Tiny Dungeon"

BLACK = (0, 0, 0)
MAP_BACKGROUND = (234, 165, 108)

tiles = {}

player = None


DIR_LEFT = 1
DIR_RIGHT = 2
DIR_UP = 3
DIR_DOWN = 4
player_last_direction = DIR_DOWN


current_animation_sprites = player_idle_down_sprites
current_sprite_index = 0
animation_timer = 0.0

player_attacking = False
player_is_dead = False


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


def player_dying_end():
    pass


def update():
    global current_animation_sprites, current_sprite_index, animation_timer, player_attacking, player_is_dead, player_last_direction

    old_player_x = player.x
    old_player_y = player.y

    player_walking = False

    if player_is_dead:
        pass
    elif player_attacking:
        pass
    # >>> CONDIÇÃO TEMPORARIA <<<
    elif keyboard.k:
        player_is_dead = True
        player_attacking = False
        player_walking = False
        current_sprite_index = 0
        animation_timer = 0.0
    elif keyboard.space:
        player_attacking = True
        player_walking = False
        current_sprite_index = 0
        animation_timer = 0.0
    else:
        if keyboard.left:
            player.x -= 1
            player_walking = True
            player_last_direction = DIR_LEFT
        if keyboard.right:
            player.x += 1
            player_walking = True
            player_last_direction = DIR_RIGHT
        if not collision_check.collision_check(player.x, player.y):
            player.x = old_player_x

        if keyboard.down:
            player.y += 1
            player_walking = True
            player_last_direction = DIR_DOWN
        if keyboard.up:
            player.y -= 1
            player_walking = True
            player_last_direction = DIR_UP

        if not collision_check.collision_check(player.x, player.y):
            player.y = old_player_y

    current_animation_sprites, current_sprite_index, animation_timer = (
        update_player_animation(
            player,
            player_is_dead,
            player_attacking,
            player_walking,
            player_last_direction,
            1 / 60.0,
            current_animation_sprites,
            current_sprite_index,
            animation_timer,
            player_attack_end,
            player_dying_end,
        )
    )


init_game()

pgzrun.go()
