import random
import pgzrun
from pgzero.actor import Actor
from pgzero.keyboard import keyboard
from pgzero import music
from pygame.rect import Rect as rect

# Unica exceção de import do pygame

from config import *
from utils.collision_check import collision_check
from utils.player_animation_manager import update_player_animation

from map.game_map import MAP_WIDTH, MAP_HEIGHT, TILE_GIDS, TILE_SIZE, MAP_DATA
from sprites.player_sprites import player_idle_down_sprites
from sprites.skeleton_sprites import *
from sprites.coin_sprites import coin_sprites
from sprites.indicator_sprites import indicator_sprites

WIDTH = 800
HEIGHT = 640
TITLE = "Tiny Dungeon"
MAP_BACKGROUND = (234, 165, 108)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)


tiles = {}
player = None
skeletons = []
coins = []
indicators = []
game_won = False
coins_collected = 0
game_state = "menu"
music_on = True
indicator_on = False
transition_radius = 0
transition_target_state = ""
player_last_direction = DIR_DOWN
current_player_animation_sprites = player_idle_down_sprites
player_current_sprite_index = 0
player_animation_timer = 0.0
player_attacking = False
player_is_dead = False
coin_current_sprite_index = 0
coin_animation_timer = 0.0
indicator_sprites_current_index = 0
indicator_animation_timer = 0


def init_game():
    global player, tiles, skeletons, coins, coins_collected, game_won, player_is_dead
    global indicators, player_attacking, player_animation_timer, player_current_sprite_index, transition_radius

    player_is_dead = False
    player_attacking = False
    player_animation_timer = 0.0
    player_current_sprite_index = 0
    player = Actor("player_idle_1")
    player.pos = (WIDTH // 2, HEIGHT // 2)

    game_state = "playing"
    game_won = False
    transition_radius = 0
    skeletons.clear()
    coins.clear()
    indicators.clear()
    coins_collected = 0

    for tile_name in set(TILE_GIDS.values()):
        tiles[tile_name] = Actor(tile_name)

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
        skeletons.append(
            {
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
        )

    coin_positions = [(3, 3), (3, 21), (27, 7), (13, 28), (19, 27), (47, 8), (24, 35)]
    for pos in coin_positions:
        coin = Actor("coin_1")
        coin.pos = (
            pos[0] * TILE_SIZE + TILE_SIZE // 2,
            pos[1] * TILE_SIZE + TILE_SIZE // 2,
        )
        coins.append(coin)


def draw_game():
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
    for indicator in indicators:
        indicator.draw()

    text = f"Moedas: {coins_collected}/{TOTAL_COINS}"
    screen.draw.text(
        text,
        topright=(WIDTH - 15, 17),
        fontsize=20,
        color=YELLOW,
        ocolor=BLACK,
        owidth=1.5,
        fontname="pixel.ttf",
    )


def draw_menu():
    screen.fill(BLACK)

    screen.draw.text(
        "TINY DUNGEON",
        center=(WIDTH // 2, HEIGHT * 0.25),
        fontsize=50,
        color="white",
        ocolor=BLACK,
        owidth=1.5,
        fontname="pixel.ttf",
    )

    screen.draw.text(
        "JOGAR",
        center=(WIDTH // 2 - 100, HEIGHT * 0.6),
        fontsize=15,
        color="white",
        ocolor=BLACK,
        owidth=1.5,
        fontname="pixel.ttf",
    )

    music_text = "SOM: LIGADO" if music_on else "SOM: DESLIGADO"
    screen.draw.text(
        music_text,
        center=(WIDTH // 2 + 100, HEIGHT * 0.6),
        fontsize=15,
        color="white",
        ocolor=BLACK,
        owidth=1.5,
        fontname="pixel.ttf",
    )

    screen.draw.text(
        "SAIR",
        topleft=(15, 15),
        fontsize=15,
        color="white",
        ocolor=BLACK,
        owidth=1.5,
        fontname="pixel.ttf",
    )


def draw_endscreen(message):
    screen.fill(BLACK)
    screen.draw.text(
        message,
        center=(WIDTH // 2, HEIGHT * 0.25),
        fontsize=50,
        color="white",
        ocolor=BLACK,
        owidth=1.5,
        fontname="pixel.ttf",
    )
    screen.draw.text(
        "JOGAR DE NOVO",
        center=(WIDTH // 2, HEIGHT * 0.6),
        fontsize=15,
        color="white",
        ocolor=BLACK,
        owidth=1.5,
        fontname="pixel.ttf",
    )


def draw():
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "transition":
        draw_game()
        screen.draw.filled_circle((player.x, player.y), transition_radius, BLACK)
    elif game_state == "game_over":
        draw_endscreen("DERROTA")
    elif game_state == "victory":
        draw_endscreen("FIM DE JOGO")


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


def update_indicator_animation():
    global indicator_animation_timer, indicator_sprites_current_index
    indicator_animation_timer += 1 / 60.0
    if indicator_animation_timer >= ANIMATION_SPEED_COIN:
        indicator_animation_timer = 0
        indicator_sprites_current_index = (indicator_sprites_current_index + 1) % len(
            indicator_sprites
        )
    new_indicator_image = indicator_sprites[indicator_sprites_current_index].image
    for indicator in indicators:
        indicator.image = new_indicator_image


def update_transition():
    global transition_radius, game_state, transition_target_state
    transition_radius += 15

    if transition_radius > WIDTH:
        game_state = transition_target_state


def update_game():
    global player_last_direction, player_attacking, player_is_dead
    global player_current_sprite_index, player_animation_timer, current_player_animation_sprites
    global coins_collected, game_won, game_state, transition_target_state

    if game_won:
        pass

    if player_is_dead:
        game_state = "transition"
        transition_target_state = "game_over"
        pass

    update_coin_animation()

    for coin in reversed(coins):
        if player.colliderect(coin):
            coins.remove(coin)
            coins_collected += 1
            if music_on:
                sounds.picked_coin.play()

    if coins_collected >= TOTAL_COINS:
        player_tile_x = int(player.x // TILE_SIZE)
        player_tile_y = int(player.y // TILE_SIZE)
        if not indicators:
            indicator_pos = [(14, 10), (15, 10)]
            for pos in indicator_pos:
                indicator = Actor("indicator_1")
                indicator.pos = (
                    pos[0] * TILE_SIZE + TILE_SIZE // 2,
                    pos[1] * TILE_SIZE + TILE_SIZE // 2,
                )
                indicators.append(indicator)
        update_indicator_animation()
        if (player_tile_x, player_tile_y) in [(14, 10), (15, 10)]:
            game_state = "transition"
            transition_target_state = "victory"
            if music_on:
                sounds.victory.play()
            game_won = True

    old_player_x, old_player_y = player.x, player.y
    player_walking = False
    if not player_attacking:
        if keyboard.left:
            player.x -= 1.3
            player_walking = True
            player_last_direction = DIR_LEFT
        if keyboard.right:
            player.x += 1.3
            player_walking = True
            player_last_direction = DIR_RIGHT
        if not collision_check(player.x, player.y, skeletons):
            player.x = old_player_x

        if keyboard.up:
            player.y -= 1.3
            player_walking = True
            player_last_direction = DIR_UP
        if keyboard.down:
            player.y += 1.3
            player_walking = True
            player_last_direction = DIR_DOWN
        if not collision_check(player.x, player.y, skeletons):
            player.y = old_player_y

        if keyboard.space:
            player_attacking = True
            player_walking = False
            player_current_sprite_index = 0
            if music_on:
                sounds.sword_sfx.play()

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
                if music_on:
                    sounds.bones.play()
                    sounds.bones_2.play()

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
            if music_on:
                sounds.sword_sfx.play()

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

            skeleton_dict["idle_timer"] += (
                round(random.SystemRandom().uniform(0.0001, 2.0), 2) / 60.0
            )
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
        game_state = "transition"
        transition_target_state = "game_over"
        if music_on:
            sounds.player_death.play()

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


def on_mouse_down(pos):
    global game_state, music_on, transition_radius

    if game_state == "menu":
        start_button = rect((WIDTH // 2 - 170, HEIGHT * 0.6 - 20), (140, 40))
        music_button = rect((WIDTH // 2 + 30, HEIGHT * 0.6 - 20), (140, 40))
        exit_button = rect((15, 15), (80, 30))
        if start_button.collidepoint(pos):
            game_state = "playing"
            init_game()
            if music_on:
                music.play("game.ogg")
                music.set_volume(0.3)
            else:
                music.stop()
        if music_button.collidepoint(pos):
            music_on = not music_on
            if music_on:
                music.unpause()
            else:
                music.pause()
        if exit_button.collidepoint(pos):
            quit()

    elif game_state in ["game_over", "victory"]:
        play_again_button = rect((WIDTH // 2 - 190, HEIGHT * 0.6 - 20), (380, 40))
        if play_again_button.collidepoint(pos):
            game_state = "menu"
            transition_radius = 0
            if music_on:
                music.play("menu.mp3")


def update():
    if game_state == "playing":
        update_game()
    elif game_state == "transition":
        update_transition()


init_game()

music.play("menu.mp3")
music.set_volume(0.3)

pgzrun.go()
