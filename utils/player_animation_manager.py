from sprites.player_sprites import (
    player_idle_sprites,
    player_idle_left_sprites,
    player_idle_up_sprites,
    player_idle_down_sprites,
    player_walk_sprites,
    player_walk_left_sprites,
    player_walk_up_sprites,
    player_walk_down_sprites,
    player_attack_sprites,
    player_attack_left_sprites,
    player_attack_up_sprites,
    player_attack_down_sprites,
    player_dying_sprites,
    player_dying_left_sprites,
    player_dying_up_sprites,
    player_dying_down_sprites,
)


from config import (
    DIR_UP,
    DIR_DOWN,
    DIR_LEFT,
    DIR_RIGHT,
    ANIMATION_SPEED_IDLE,
    ANIMATION_SPEED_WALK,
    ANIMATION_SPEED_ATTACK,
)


def update_player_animation(
    player_obj,
    is_dead,
    is_attacking,
    is_walking,
    last_direction,
    delta_time,
    current_anim_list,
    current_frame_idx,
    anim_timer,
    on_attack_end_callback,
    on_dying_end_callback,
):

    anim_timer += delta_time

    speed_used = 0
    target_animation_list = None

    if is_dead:
        if last_direction == DIR_UP:
            target_animation_list = player_dying_up_sprites
        elif last_direction == DIR_DOWN:
            target_animation_list = player_dying_down_sprites
        elif last_direction == DIR_LEFT:
            target_animation_list = player_dying_left_sprites
        elif last_direction == DIR_RIGHT:
            target_animation_list = player_dying_sprites
        else:
            target_animation_list = player_dying_down_sprites
        speed_used = 0.2
    elif is_attacking:
        if last_direction == DIR_UP:
            target_animation_list = player_attack_up_sprites
        elif last_direction == DIR_DOWN:
            target_animation_list = player_attack_down_sprites
        elif last_direction == DIR_LEFT:
            target_animation_list = player_attack_left_sprites
        elif last_direction == DIR_RIGHT:
            target_animation_list = player_attack_sprites
        else:
            target_animation_list = player_attack_down_sprites
        speed_used = ANIMATION_SPEED_ATTACK
    elif is_walking:
        if last_direction == DIR_UP:
            target_animation_list = player_walk_up_sprites
        elif last_direction == DIR_DOWN:
            target_animation_list = player_walk_down_sprites
        elif last_direction == DIR_LEFT:
            target_animation_list = player_walk_left_sprites
        elif last_direction == DIR_RIGHT:
            target_animation_list = player_walk_sprites
        else:
            target_animation_list = player_walk_down_sprites
        speed_used = ANIMATION_SPEED_WALK
    else:
        if last_direction == DIR_UP:
            target_animation_list = player_idle_up_sprites
        elif last_direction == DIR_DOWN:
            target_animation_list = player_idle_down_sprites
        elif last_direction == DIR_LEFT:
            target_animation_list = player_idle_left_sprites
        elif last_direction == DIR_RIGHT:
            target_animation_list = player_idle_sprites
        else:
            target_animation_list = player_idle_down_sprites
        speed_used = ANIMATION_SPEED_IDLE

    if current_anim_list != target_animation_list:
        current_anim_list = target_animation_list
        current_frame_idx = 0
        anim_timer = 0.0

    if anim_timer >= speed_used:
        anim_timer = 0
        current_frame_idx = current_frame_idx + 1

        if current_anim_list == player_attack_up_sprites:
            if current_frame_idx >= len(player_attack_up_sprites):
                current_frame_idx = len(player_attack_up_sprites) - 1
                on_attack_end_callback()
        elif current_anim_list == player_attack_down_sprites:
            if current_frame_idx >= len(player_attack_down_sprites):
                current_frame_idx = len(player_attack_down_sprites) - 1
                on_attack_end_callback()
        elif current_anim_list == player_attack_left_sprites:
            if current_frame_idx >= len(player_attack_left_sprites):
                current_frame_idx = len(player_attack_left_sprites) - 1
                on_attack_end_callback()
        elif current_anim_list == player_attack_sprites:
            if current_frame_idx >= len(player_attack_sprites):
                current_frame_idx = len(player_attack_sprites) - 1
                on_attack_end_callback()
        elif current_anim_list == player_dying_up_sprites:
            if current_frame_idx >= len(player_dying_up_sprites):
                current_frame_idx = len(player_dying_up_sprites) - 1
                on_dying_end_callback()
        elif current_anim_list == player_dying_down_sprites:
            if current_frame_idx >= len(player_dying_down_sprites):
                current_frame_idx = len(player_dying_down_sprites) - 1
                on_dying_end_callback()
        elif current_anim_list == player_dying_left_sprites:
            if current_frame_idx >= len(player_dying_left_sprites):
                current_frame_idx = len(player_dying_left_sprites) - 1
                on_dying_end_callback()
        elif current_anim_list == player_dying_sprites:
            if current_frame_idx >= len(player_dying_sprites):
                current_frame_idx = len(player_dying_sprites) - 1
                on_dying_end_callback()
        else:
            current_frame_idx %= len(current_anim_list)

    player_obj.image = current_anim_list[current_frame_idx].image

    return current_anim_list, current_frame_idx, anim_timer
