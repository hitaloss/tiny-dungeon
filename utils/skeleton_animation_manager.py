from pgzero.actor import Actor

# Novamente a excessão que foi passada no teste
from pygame import Rect as rect

from config import (
    DIR_LEFT,
    DIR_RIGHT,
    SKELETON_WALK_SPEED,
    SKELETON_IDLE_DURATION,
    SKELETON_PATROL_DISTANCE,
    SKELETON_ATTACK_SPEED,
    SKELETON_HIT_DELAY,
    SKELETON_ATTACK_RANGE_OFFSET_X,
    SKELETON_ATTACK_RANGE_OFFSET_Y,
    SKELETON_ATTACK_RANGE_WIDTH,
    SKELETON_ATTACK_RANGE_HEIGHT,
    SKELETON_ATTACK_COOLDOWN,
    TILE_SIZE,
)


from sprites.skeleton_sprites import (
    skeleton_idle_sprites,
    skeleton_idle_left_sprites,
    skeleton_walk_sprites,
    skeleton_walk_left_sprites,
    skeleton_attack_sprites,
    skeleton_attack_left_sprites,
    skeleton_dying_sprites,
    skeleton_dying_left_sprites,
)


def update_skeleton_state_and_animation(
    skeleton_obj,
    player_obj,
    alt_time,
    patrol_start_x,
    patrol_end_x,
    current_direction_is_right,
    is_patrolling,
    idle_timer,
    is_attacking,
    is_dead,
    attack_hit_timer,
    hit_applied,
    attack_cooldown_timer,
    current_sprites_list,
    current_sprite_index,
    animation_timer,
    on_attack_end_callback,
):
    player_was_hit = False
    start_despawn_timer = False

    if is_dead:
        if current_direction_is_right:
            current_sprites_list = skeleton_dying_sprites
        else:
            current_sprites_list = skeleton_dying_left_sprites

        animation_timer += alt_time
        if animation_timer >= 0.1:
            animation_timer = 0
            if current_sprite_index < len(current_sprites_list) - 1:
                current_sprite_index += 1
            else:
                start_despawn_timer = True

        skeleton_obj.image = current_sprites_list[current_sprite_index].image

        return (
            current_sprites_list,
            current_sprite_index,
            animation_timer,
            current_direction_is_right,
            is_patrolling,
            idle_timer,
            is_attacking,
            attack_hit_timer,
            hit_applied,
            attack_cooldown_timer,
            False,
            start_despawn_timer,
        )

    if not is_attacking and attack_cooldown_timer > 0:
        attack_cooldown_timer -= alt_time
        if attack_cooldown_timer < 0:
            attack_cooldown_timer = 0

    if is_attacking:
        attack_hit_timer += alt_time
        if attack_hit_timer >= SKELETON_HIT_DELAY and not hit_applied:
            attack_hitbox_x = skeleton_obj.x
            attack_hitbox_y = skeleton_obj.y
            if current_direction_is_right:
                attack_hitbox_x += SKELETON_ATTACK_RANGE_OFFSET_X
            else:
                attack_hitbox_x -= SKELETON_ATTACK_RANGE_OFFSET_X

            attack_hitbox_y -= SKELETON_ATTACK_RANGE_OFFSET_Y

            skeleton_attack_rect = rect(
                attack_hitbox_x - SKELETON_ATTACK_RANGE_WIDTH / 2,
                attack_hitbox_y - SKELETON_ATTACK_RANGE_HEIGHT / 2,
                SKELETON_ATTACK_RANGE_WIDTH,
                SKELETON_ATTACK_RANGE_HEIGHT,
            )

            if player_obj.colliderect(skeleton_attack_rect):
                player_was_hit = True

            hit_applied = True
    else:
        is_vertically_aligned = abs(player_obj.y - skeleton_obj.y) < TILE_SIZE
        is_in_front = False

        if current_direction_is_right:
            if (
                player_obj.left >= skeleton_obj.right
                and player_obj.left - skeleton_obj.right < TILE_SIZE - 10
            ):
                is_in_front = True

        else:
            if (
                player_obj.right <= skeleton_obj.left
                and skeleton_obj.left
                and skeleton_obj.left - player_obj.right < TILE_SIZE - 10
            ):
                is_in_front = True

        if (
            is_in_front
            and is_vertically_aligned
            and not is_attacking
            and attack_cooldown_timer <= 0
        ):
            is_attacking = True
            is_patrolling = False
            attack_hit_timer = 0.0
            hit_applied = False
            current_sprite_index = 0
            animation_timer = 0.0
        elif is_patrolling:
            if current_direction_is_right:
                skeleton_obj.x += SKELETON_WALK_SPEED
                current_sprites_list = skeleton_walk_sprites
                if skeleton_obj.x >= patrol_end_x:
                    skeleton_obj.x = patrol_end_x
                    current_direction_is_right = False
                    is_patrolling = False
                    idle_timer = 0.0
            else:
                skeleton_obj.x -= SKELETON_WALK_SPEED
                current_sprites_list = skeleton_walk_left_sprites
                if skeleton_obj.x <= patrol_start_x:
                    skeleton_obj.x = patrol_start_x
                    current_direction_is_right = True
                    is_patrolling = False
                    idle_timer = 0.0
        else:
            idle_timer += alt_time
            if current_direction_is_right:
                current_sprites_list = skeleton_idle_sprites
            else:
                current_sprites_list = skeleton_idle_left_sprites

            if idle_timer >= SKELETON_IDLE_DURATION:
                is_patrolling = True

    animation_timer += alt_time

    skeleton_speed_used = 0

    if is_attacking:
        skeleton_speed_used = SKELETON_ATTACK_SPEED
        if current_direction_is_right:
            current_sprites_list = skeleton_attack_sprites
        else:
            current_sprites_list = skeleton_attack_left_sprites
    elif is_patrolling:
        skeleton_speed_used = 0.1
    else:
        skeleton_speed_used = 0.2

    if animation_timer >= skeleton_speed_used:
        animation_timer = 0

        if (
            current_sprites_list == skeleton_attack_sprites
            or current_sprites_list == skeleton_attack_left_sprites
        ):
            if current_sprite_index < len(current_sprites_list) - 1:
                current_sprite_index += 1
            else:
                current_sprite_index = 0
                on_attack_end_callback()
                is_attacking = False

        elif (
            current_sprites_list == skeleton_dying_sprites
            or current_sprites_list == skeleton_dying_left_sprites
        ):
            if current_sprite_index < len(current_sprites_list) - 1:
                pass

        else:
            current_sprite_index = (current_sprite_index + 1) % len(
                current_sprites_list
            )

        skeleton_obj.image = current_sprites_list[current_sprite_index].image

    return (
        current_sprites_list,
        current_sprite_index,
        animation_timer,
        current_direction_is_right,
        is_patrolling,
        idle_timer,
        is_attacking,
        attack_hit_timer,
        hit_applied,
        attack_cooldown_timer,
        player_was_hit,
        start_despawn_timer,
    )
