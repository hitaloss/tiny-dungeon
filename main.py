import random
import pgzrun
from pgzero.actor import Actor
from pgzero.keyboard import keyboard
from pygame.rect import Rect as rect

# Unica exceção de import do pygame

from config import *
from utils.collision_check import collision_check
from utils.player_animation_manager import update_player_animation

from map.game_map import MAP_WIDTH, MAP_HEIGHT, TILE_GIDS, TILE_SIZE, MAP_DATA
from sprites.player_sprites import player_idle_down_sprites
from sprites.skeleton_sprites import *
from sprites.coin_sprites import coin_sprites

WIDTH = 800
HEIGHT = 650
TITLE = "Tiny Dungeon"
MAP_BACKGROUND = (234, 165, 108)


tiles = {}
player = None
skeletons = []
coins = []
game_won = False
coins_collected = 0


player_last_direction = DIR_DOWN
current_player_animation_sprites = player_idle_down_sprites
player_current_sprite_index = 0
player_animation_timer = 0.0
player_attacking = False
player_is_dead = False


coin_current_sprite_index = 0
coin_animation_timer = 0.0


def init_game():
    global player, tiles, skeletons, coins, coins_collected, game_won, player_is_dead

    player = Actor("player_idle_1")
    player.pos = (WIDTH // 2, HEIGHT // 2)
    player_is_dead = False

    for tile_name in set(TILE_GIDS.values()):
        tiles[tile_name] = Actor(tile_name)

    skeletons.clear()
    skeleton_positions = [
        (4, 2),
        (4, 21),
        (10, 22),
        (12, 14),
        (12, 34),
        (18, 37),
        (21, 24),
        (30, 25),
        (30, 8),
        (30, 37),
        (34, 14),
        (40, 22),
        (46, 9),
    ]
    for pos in skeleton_positions:
        actor = Actor("skeleton_idle_1")
        actor.pos = (
            pos[0] * TILE_SIZE + TILE_SIZE // 2,
            pos[1] * TILE_SIZE + TILE_SIZE // 2,
        )

        skeleton_dict = {
            "actor": actor,
            "patrol_start_x": actor.x - SKELETON_PATROL_DISTANCE / 2,
            "patrol_end_x": actor.x + SKELETON_PATROL_DISTANCE / 2,
            "moving_right": True,
            "is_patrolling": True,
            "is_attacking": False,
            "is_dead": False,
            "hit_applied": False,
            "despawn_timer": 0.0,
            "idle_timer": 0.0,
            "attack_hit_timer": 0.0,
            "attack_cooldown_timer": SKELETON_ATTACK_COOLDOWN,
            "animation_timer": 0.0,
            "current_sprite_index": 0,
            "current_sprites_list": skeleton_idle_sprites,
        }
        skeletons.append(skeleton_dict)

    coins.clear()
    coins_collected = 0
    game_won = False
    coin_positions = [(3, 3), (3, 21), (27, 7), (35, 38), (45, 35), (47, 8), (39, 38)]
    for pos in coin_positions:
        coin = Actor("coin_1")
        coin.pos = (
            pos[0] * TILE_SIZE + TILE_SIZE // 2,
            pos[1] * TILE_SIZE + TILE_SIZE // 2,
        )
        coins.append(coin)


def draw():
    screen.fill(MAP_BACKGROUND)

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile_gid = MAP_DATA[y * MAP_WIDTH + x] & 0x3FFFFFFF
            tile_name = TILE_GIDS.get(tile_gid)
            if tile_name:
                tile_actor = tiles[tile_name]
                tile_actor.topleft = (x * TILE_SIZE, y * TILE_SIZE)
                tile_actor.draw()

    player.draw()
    for coin in coins:
        coin.draw()
    for skeleton_dict in skeletons:
        skeleton_dict["actor"].draw()


def player_attack_end():
    global player_attacking
    player_attacking = False


def player_dying_end():
    pass


def update_coin_animation():
    global coin_animation_timer, coin_current_sprite_index
    coin_animation_timer += 1 / 60.0
    if coin_animation_timer >= ANIMATION_SPEED_COIN:
        coin_animation_timer = 0
        coin_current_sprite_index = (coin_current_sprite_index + 1) % len(coin_sprites)
    new_coin_image = coin_sprites[coin_current_sprite_index].image
    for coin in coins:
        coin.image = new_coin_image


def update():
    global player_last_direction, player_attacking, player_is_dead
    global player_current_sprite_index, player_animation_timer, current_player_animation_sprites
    global coins_collected, game_won

    if game_won:
        pass

    if player_is_dead:
        pass

    update_coin_animation()

    for coin in reversed(coins):
        if player.colliderect(coin):
            coins.remove(coin)
            coins_collected += 1
            print(f"Moedas coletadas: {coins_collected}/{TOTAL_COINS}")

    if coins_collected >= TOTAL_COINS:
        player_tile_x = int(player.x // TILE_SIZE)
        player_tile_y = int(player.y // TILE_SIZE)
        if (player_tile_x, player_tile_y) in [(14, 10), (15, 10)]:
            game_won = True
            print("VOCE VENCEU!!!")

    old_player_x, old_player_y = player.x, player.y
    player_walking = False
    if not player_attacking:
        if keyboard.left:
            player.x -= 2
            player_walking = True
            player_last_direction = DIR_LEFT
        if keyboard.right:
            player.x += 2
            player_walking = True
            player_last_direction = DIR_RIGHT
        if not collision_check(player.x, player.y, skeletons):
            player.x = old_player_x

        if keyboard.up:
            player.y -= 2
            player_walking = True
            player_last_direction = DIR_UP
        if keyboard.down:
            player.y += 2
            player_walking = True
            player_last_direction = DIR_DOWN
        if not collision_check(player.x, player.y, skeletons):
            player.y = old_player_y

        if keyboard.space:
            player_attacking = True
            player_walking = False
            player_current_sprite_index = 0

    if player_attacking:
        attack_hitbox = rect(0, 0, TILE_SIZE + 4, TILE_SIZE + 4)
        attack_hitbox.center = player.center
        for skeleton_dict in skeletons:
            if not skeleton_dict["is_dead"] and attack_hitbox.colliderect(
                skeleton_dict["actor"]._rect
            ):
                skeleton_dict.update(
                    {"is_dead": True, "current_sprite_index": 0, "animation_timer": 0.0}
                )

    player_was_hit = False
    for skeleton_dict in skeletons:
        if skeleton_dict["is_dead"]:
            if skeleton_dict["despawn_timer"] > 0:
                skeleton_dict["despawn_timer"] -= 1 / 60.0
                if skeleton_dict["despawn_timer"] <= 0:
                    skeleton_dict["remove_me"] = True
            else:
                current_list = (
                    skeleton_dying_sprites
                    if skeleton_dict["moving_right"]
                    else skeleton_dying_left_sprites
                )
                if skeleton_dict["current_sprites_list"] is not current_list:
                    skeleton_dict.update(
                        {
                            "current_sprites_list": current_list,
                            "current_sprite_index": 0,
                            "animation_timer": 0.0,
                        }
                    )

                skeleton_dict["animation_timer"] += 1 / 60.0
                if skeleton_dict["animation_timer"] >= 0.1:
                    skeleton_dict["animation_timer"] = 0
                    if skeleton_dict["current_sprite_index"] < len(current_list) - 1:
                        skeleton_dict["current_sprite_index"] += 1
                    elif skeleton_dict["despawn_timer"] <= 0:
                        skeleton_dict["despawn_timer"] = 1.0
            continue

        if skeleton_dict["attack_cooldown_timer"] > 0:
            skeleton_dict["attack_cooldown_timer"] -= 1 / 60.0

        attack_zone = (
            rect(
                skeleton_dict["actor"].right,
                skeleton_dict["actor"].top,
                TILE_SIZE,
                skeleton_dict["actor"].height,
            )
            if skeleton_dict["moving_right"]
            else rect(
                skeleton_dict["actor"].left - TILE_SIZE,
                skeleton_dict["actor"].top,
                TILE_SIZE,
                skeleton_dict["actor"].height,
            )
        )
        can_see_player = (
            attack_zone.colliderect(player._rect)
            and abs(player.y - skeleton_dict["actor"].y) < TILE_SIZE
        )
        can_attack = skeleton_dict["attack_cooldown_timer"] <= 0

        if can_see_player and can_attack and not skeleton_dict["is_attacking"]:
            skeleton_dict.update(
                {
                    "is_attacking": True,
                    "is_patrolling": False,
                    "attack_hit_timer": 0.0,
                    "hit_applied": False,
                    "current_sprite_index": 0,
                    "animation_timer": 0.0,
                }
            )

        if skeleton_dict["is_attacking"]:
            skeleton_dict["moving_right"] = player.x > skeleton_dict["actor"].x
            current_list = (
                skeleton_attack_sprites
                if skeleton_dict["moving_right"]
                else skeleton_attack_left_sprites
            )
            if skeleton_dict["current_sprites_list"] is not current_list:
                skeleton_dict.update(
                    {
                        "current_sprites_list": current_list,
                        "current_sprite_index": 0,
                        "animation_timer": 0.0,
                    }
                )

            if skeleton_dict["attack_hit_timer"] < SKELETON_HIT_DELAY:
                skeleton_dict["attack_hit_timer"] += 1 / 60.0
                if skeleton_dict["attack_hit_timer"] >= SKELETON_HIT_DELAY:
                    attack_hitbox = rect(0, 0, SKELETON_ATTACK_RANGE_WIDTH, TILE_SIZE)
                    attack_hitbox.center = skeleton_dict["actor"].center
                    offset = (
                        SKELETON_ATTACK_RANGE_OFFSET_X
                        if skeleton_dict["moving_right"]
                        else -SKELETON_ATTACK_RANGE_OFFSET_X
                    )
                    attack_hitbox.x += offset
                    if player.colliderect(attack_hitbox):
                        player_was_hit = True

        elif skeleton_dict["is_patrolling"]:
            current_list = (
                skeleton_walk_sprites
                if skeleton_dict["moving_right"]
                else skeleton_walk_left_sprites
            )
            if skeleton_dict["current_sprites_list"] is not current_list:
                skeleton_dict.update(
                    {
                        "current_sprites_list": current_list,
                        "current_sprite_index": 0,
                        "animation_timer": 0.0,
                    }
                )

            if skeleton_dict["moving_right"]:
                skeleton_dict["actor"].x += SKELETON_WALK_SPEED
                if skeleton_dict["actor"].x >= skeleton_dict["patrol_end_x"]:
                    skeleton_dict["is_patrolling"] = False
                    skeleton_dict["idle_timer"] = 0.0
            else:
                skeleton_dict["actor"].x -= SKELETON_WALK_SPEED
                if skeleton_dict["actor"].x <= skeleton_dict["patrol_start_x"]:
                    skeleton_dict["is_patrolling"] = False
                    skeleton_dict["idle_timer"] = 0.0

        else:
            current_list = (
                skeleton_idle_sprites
                if skeleton_dict["moving_right"]
                else skeleton_idle_left_sprites
            )
            if skeleton_dict["current_sprites_list"] is not current_list:
                skeleton_dict.update(
                    {
                        "current_sprites_list": current_list,
                        "current_sprite_index": 0,
                        "animation_timer": 0.0,
                    }
                )

            skeleton_dict["idle_timer"] += round(random.uniform(0.01, 2.0), 10) / 60.0
            if skeleton_dict["idle_timer"] >= SKELETON_IDLE_DURATION:
                skeleton_dict["is_patrolling"] = True
                skeleton_dict["moving_right"] = not skeleton_dict["moving_right"]

        skeleton_dict["animation_timer"] += 1 / 60.0

        speed = ANIMATION_SPEED_IDLE
        if skeleton_dict["is_patrolling"]:
            speed = ANIMATION_SPEED_WALK
        if skeleton_dict["is_attacking"]:
            speed = SKELETON_ATTACK_SPEED

        if skeleton_dict["animation_timer"] >= speed:
            skeleton_dict["animation_timer"] = 0
            current_list = skeleton_dict["current_sprites_list"]
            if len(current_list) > 0:
                skeleton_dict["current_sprite_index"] = (
                    skeleton_dict["current_sprite_index"] + 1
                ) % len(current_list)

                if (
                    skeleton_dict["is_attacking"]
                    and skeleton_dict["current_sprite_index"] == 0
                ):
                    skeleton_dict["is_attacking"] = False
                    skeleton_dict["attack_cooldown_timer"] = SKELETON_ATTACK_COOLDOWN
                    skeleton_dict["is_patrolling"] = True

    skeletons_to_keep = []
    for skeleton_dict in skeletons:
        if skeleton_dict.get("remove_me"):
            continue

        current_list = skeleton_dict["current_sprites_list"]
        if len(current_list) > 0:
            skeleton_dict["current_sprite_index"] %= len(current_list)
            skeleton_dict["actor"].image = current_list[
                skeleton_dict["current_sprite_index"]
            ].image

        skeletons_to_keep.append(skeleton_dict)

    skeletons[:] = skeletons_to_keep

    if player_was_hit and not player_is_dead:
        player_is_dead = True

    (
        current_player_animation_sprites,
        player_current_sprite_index,
        player_animation_timer,
    ) = update_player_animation(
        player,
        player_is_dead,
        player_attacking,
        player_walking,
        player_last_direction,
        1 / 60.0,
        current_player_animation_sprites,
        player_current_sprite_index,
        player_animation_timer,
        player_attack_end,
        player_dying_end,
    )


init_game()
pgzrun.go()
