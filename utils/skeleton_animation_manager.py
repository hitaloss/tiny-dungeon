from pgzero.actor import Actor
from config import (
    DIR_LEFT,
    DIR_RIGHT,
    SKELETON_WALK_SPEED,
    SKELETON_IDLE_DURATION,
    SKELETON_PATROL_DISTANCE,
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
    alt_time,
    patrol_start_x,
    patrol_end_x,
    current_direction_is_right,
    is_patrolling,
    idle_timer,
    current_sprites_list,
    current_sprite_index,
    animation_timer,
):
    if is_patrolling:
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

    if is_patrolling:
        skeleton_speed_used = 0.1
    else:
        skeleton_speed_used = 0.2

    if animation_timer >= skeleton_speed_used:
        animation_timer = 0
        current_sprite_index = (current_sprite_index + 1) % len(current_sprites_list)
        skeleton_obj.image = current_sprites_list[current_sprite_index].image

    return (
        current_sprites_list,
        current_sprite_index,
        animation_timer,
        current_direction_is_right,
        is_patrolling,
        idle_timer,
    )
