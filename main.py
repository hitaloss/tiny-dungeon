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
    SKELETON_PATROL_DISTANCE,
)
from utils import collision_check
from utils.player_animation_manager import update_player_animation
from utils.skeleton_animation_manager import update_skeleton_state_and_animation

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

from sprites.skeleton_sprites import skeleton_idle_sprites

WIDTH = 800
HEIGHT = 600
TITLE = "Tiny Dungeon"

BLACK = (0, 0, 0)
MAP_BACKGROUND = (234, 165, 108)

tiles = {}

player = None

player_last_direction = DIR_DOWN

current_player_animation_sprites = player_idle_down_sprites
current_sprite_index = 0
animation_timer = 0.0

player_attacking = False
player_is_dead = False

skeleton = None
skeleton_current_animation_sprites = None
skeleton_current_frame_index = 0
skeleton_animation_timer = 0.0

skeleton_patrol_start_x = 0
skeleton_patrol_end_x = 0
skeleton_moving_right = True
skeleton_is_patrolling = True
skeleton_idle_timer = 0


def init_game():
    global player, current_player_animation_sprites, skeleton, skeleton_patrol_start_x, skeleton_patrol_end_x, skeleton_current_animation_sprites

    player = current_player_animation_sprites[0]
    player.pos = (WIDTH // 2, HEIGHT // 2)
    player.width = TILE_SIZE
    player.height = TILE_SIZE

    for tile_name in set(TILE_GIDS.values()):
        tiles[tile_name] = Actor(tile_name)

    skeleton = skeleton_idle_sprites[0]
    skeleton_initial_tile_x = (WIDTH // 2) // TILE_SIZE
    skeleton_initial_tile_y = (HEIGHT // 2 + TILE_SIZE * 2) // TILE_SIZE

    skeleton.pos = (
        skeleton_initial_tile_x * TILE_SIZE + TILE_SIZE // 2,
        skeleton_initial_tile_y * TILE_SIZE + TILE_SIZE // 2,
    )
    skeleton.width = TILE_SIZE
    skeleton.height = TILE_SIZE

    skeleton_patrol_start_x = skeleton.x - SKELETON_PATROL_DISTANCE / 2
    skeleton_patrol_end_x = skeleton.x + SKELETON_PATROL_DISTANCE / 2

    skeleton_current_animation_sprites = skeleton_idle_sprites


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
    skeleton.draw()


def player_attack_end():
    global player_attacking
    player_attacking = False


def player_dying_end():
    pass


def update():
    global current_player_animation_sprites, current_sprite_index, animation_timer, player_attacking, player_is_dead, player_last_direction
    global skeleton_current_animation_sprites, skeleton_current_frame_index, skeleton_animation_timer, skeleton_moving_right, skeleton_is_patrolling, skeleton_idle_timer

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

    current_player_animation_sprites, current_sprite_index, animation_timer = (
        update_player_animation(
            player,
            player_is_dead,
            player_attacking,
            player_walking,
            player_last_direction,
            1 / 60.0,
            current_player_animation_sprites,
            current_sprite_index,
            animation_timer,
            player_attack_end,
            player_dying_end,
        )
    )

    (
        skeleton_current_animation_sprites,
        skeleton_current_frame_index,
        skeleton_animation_timer,
        skeleton_moving_right,
        skeleton_is_patrolling,
        skeleton_idle_timer,
    ) = update_skeleton_state_and_animation(
        skeleton_obj=skeleton,
        alt_time=1 / 60.0,
        patrol_start_x=skeleton_patrol_start_x,
        patrol_end_x=skeleton_patrol_end_x,
        current_direction_is_right=skeleton_moving_right,
        is_patrolling=skeleton_is_patrolling,
        idle_timer=skeleton_idle_timer,
        current_sprites_list=skeleton_current_animation_sprites,
        current_sprite_index=skeleton_current_frame_index,
        animation_timer=skeleton_animation_timer,
    )


init_game()

pgzrun.go()
