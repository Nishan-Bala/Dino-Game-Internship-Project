"""Dino Game in Python

A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @bassemfarid, no one or nothing else. 🤖
"""

import pygame
import random

# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
running = True  # Pygame main loop, kills pygame when False

# Game state variables
is_playing = True  # Whether in game or in menu
GROUND_Y = 300  # The Y-coordinate of the ground level
JUMP_GRAVITY_START_SPEED = -15  # The speed at which the player jumps
players_gravity_speed = 0  # The current speed at which the player falls

can_double_jump = False
start_time = 0
score = 0
is_paused = False

# Load level assets
HEART_SURF = pygame.image.load("graphics/level/heart.png").convert_alpha()
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
game_font = pygame.font.Font(pygame.font.get_default_font(), 50)
score_surf = game_font.render("SCORE?", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))

active_powerup = None
powerup_timer = 0
POWERUP_INTERVAL = 300 
spring_powerup_surf = pygame.image.load("graphics/power_ups/spring.png").convert_alpha()
spring_rect = spring_powerup_surf.get_rect(bottomleft = (800, GROUND_Y))
spring_powerup_surf = pygame.transform.scale(spring_powerup_surf, (40, 40))
spring_hitbox = spring_rect.inflate(-5,-5)
spring_active = False
spring_timer = 0
SPRING_DURATION = 600
heart_powerup_surf = pygame.image.load("graphics/power_ups/health_powerup.png").convert_alpha()
heart_powerup_surf = pygame.transform.scale(heart_powerup_surf, (64, 64))
heart_rect = heart_powerup_surf.get_rect(bottomleft = (800, GROUND_Y))
heart_hitbox = heart_rect.inflate(-10,-10)

# Load sprite assets
player_jump = pygame.image.load("graphics/player/player_jump.png").convert_alpha()
player_walk_1 = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_walk_2 = pygame.image.load("graphics/player/player_walk_2.png").convert_alpha()
player_frames = [player_walk_1, player_walk_2] # Animation frame list
player_frame_index = 0  # Tracks which frame is currently shown
animation_speed = 8    # How many game frames to wait before switching sprite frame
animation_counter = 0   # Counts up each game frame to trigger animation switch

player_surf = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))
player_hitbox = player_rect.inflate(-8, -8)
egg_rotation_angle = 0
egg_surf = pygame.image.load("graphics/egg/egg_1.png").convert_alpha()
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))
egg_hitbox = egg_rect.inflate(-6,-6)
egg_width = egg_surf.get_width()
is_double_egg = False


lives = 3
is_invincible = False      
invincible_timer = 0
invincible_duration = 90    

while running:
    # Poll for events
    for event in pygame.event.get():
        # pygame.QUIT --> user clicked X to close your window
        if event.type == pygame.QUIT:
            running = False

        elif is_playing:
            # When player wants to jump by pressing SPACE
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                or event.type == pygame.MOUSEBUTTONDOWN
            ):
                if player_rect.bottom >= GROUND_Y:
                    players_gravity_speed = -25 if spring_active else JUMP_GRAVITY_START_SPEED
                    can_double_jump = True
                elif can_double_jump:
                    players_gravity_speed = -25 if spring_active else JUMP_GRAVITY_START_SPEED
                    can_double_jump = False
            elif is_playing:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    is_paused = not is_paused
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q and is_paused:
                    running = False
        else:
            # When player wants to play again by pressing SPACE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                is_playing = True
                lives = 3                  
                is_invincible = False      
                egg_rect.left = 800
                start_time = pygame.time.get_ticks()
                spring_active = False
                spring_timer = 0

    if is_playing:
        if not is_paused:
            if spring_active:
                spring_timer -= 1
                if spring_timer <= 0:
                    spring_active = False

            screen.fill("purple")  
            # Wipe the screen# Blit the level assets
            screen.blit(SKY_SURF, (0, 0))
            screen.blit(GROUND_SURF, (0, GROUND_Y))

            current_time = pygame.time.get_ticks() - start_time
            score = int(current_time / 100)  # Divide by 100 to make the score tick up at a readable pace
        
            score_surf = game_font.render(f"Score: {score}", False, "Black")
            score_rect = score_surf.get_rect(center=(400, 50))
        
            pygame.draw.rect(screen, "#c0e8ec", score_rect)
            pygame.draw.rect(screen, "#c0e8ec", score_rect, 10)
            screen.blit(score_surf, score_rect)

            # Adjust egg's horizontal location then blit it
            egg_rect.x -= 5
            if egg_rect.right <= 0:
                egg_rect.left = 800
                is_double_egg = random.random() < 0.2  # 20% chance of 2 eggs

            egg_rotation_angle = (egg_rotation_angle + 7) % 360  # negative = clockwise
            rotated_egg = pygame.transform.rotate(egg_surf, egg_rotation_angle)
            rotated_rect = rotated_egg.get_rect(center=egg_rect.center)
            screen.blit(rotated_egg, rotated_rect)

            if is_double_egg:
                second_center = (egg_rect.centerx + egg_width, egg_rect.centery)
                screen.blit(rotated_egg, rotated_egg.get_rect(center=second_center))
                egg_hitbox = pygame.Rect(0, 0, (egg_width * 2) - 4, egg_rect.height - 4)
                egg_hitbox.center = (egg_rect.centerx + (egg_width / 2), egg_rect.centery)
            else:
                egg_hitbox = pygame.Rect(0, 0, egg_width - 4, egg_rect.height - 4)
                egg_hitbox.center = egg_rect.center
            pygame.draw.rect(screen, "red", egg_hitbox, 2)
            
            
            powerup_timer += 1
            if powerup_timer >= POWERUP_INTERVAL and active_powerup is None:
                powerup_timer = 0
                roll = random.random()
                if roll < 0.45:
                    if egg_rect.left > 200:
                        active_powerup = 'spring'
                        spring_rect.left = 800
                elif roll < 0.5:
                    if egg_rect.left > 200:
                        active_powerup = 'heart'
                        heart_rect.left = 800

            if active_powerup == 'spring':
                spring_rect.x -= 5
                spring_hitbox.center = spring_rect.center
                screen.blit(spring_powerup_surf, spring_rect)
                spring_hitbox.center = spring_rect.center
                spring_timer_text = game_font.render(f"Jump Boost: {spring_timer}", False, "White")
                spring_timer_text_rect = spring_timer_text.get_rect(center=(650, 350))
                screen.blit(spring_timer_text, spring_timer_text_rect)
                if spring_rect.right <= 0:
                    active_powerup = None
                if spring_hitbox.colliderect(player_hitbox):
                    spring_active = True
                    spring_timer = SPRING_DURATION
                    active_powerup = None
            

            elif active_powerup == 'heart':
                heart_rect.x -= 5
                heart_hitbox.center = heart_rect.center
                screen.blit(heart_powerup_surf, heart_rect)
                if heart_rect.right <= 0:
                    active_powerup = None
                if heart_hitbox.colliderect(player_hitbox):
                    lives = min(lives + 1, 7)
                    active_powerup = None

            pygame.draw.rect(screen, "red", heart_hitbox, 2)
            pygame.draw.rect(screen, "red", spring_hitbox, 2)

            
            if player_rect.bottom >= GROUND_Y:
                animation_counter += 1
                if animation_counter >= animation_speed:
                    animation_counter = 0
                    player_frame_index = (player_frame_index + 1) % len(player_frames)
                player_surf = player_frames[player_frame_index]
            else:
                player_surf = player_jump
                animation_counter = 0 

        # Adjust player's vertical location then blit it
            players_gravity_speed += 1
            player_rect.y += players_gravity_speed
            if player_rect.bottom > GROUND_Y:
                player_rect.bottom = GROUND_Y
            screen.blit(player_surf, player_rect)
            player_hitbox.center = player_rect.center
            pygame.draw.rect(screen, "red", player_hitbox, 2)

        # When player collides with enemy, game ends
        # When player collides with enemy, lose a life
            if egg_hitbox.colliderect(player_hitbox) and not is_invincible:
                lives -= 1
                is_invincible = True
                invincible_timer = invincible_duration
                if lives <= 0:
                    is_playing = False

        # Count down invincibility
            if is_invincible:
                invincible_timer -= 1
                if invincible_timer <= 0:
                    is_invincible = False

        # Draw lives as hearts
            for i in range(lives):
                screen.blit(HEART_SURF, (10 + i * 50, 10))

        if is_paused:
            pause_overlay = pygame.Surface((800, 400), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 150))  # semi-transparent dark overlay
            screen.blit(pause_overlay, (0, 0))

            pause_surf = game_font.render("PAUSED", False, "White")
            resume_surf = game_font.render("ESC to Resume", False, "Gray")
            quit_surf = game_font.render("Q to Quit", False, "Gray")

            screen.blit(pause_surf, pause_surf.get_rect(center=(400, 160)))
            screen.blit(resume_surf, resume_surf.get_rect(center=(400, 230)))
            screen.blit(quit_surf, quit_surf.get_rect(center=(400, 290)))

    # When game is over, display game over message
    else:
        screen.fill("black")
        game_over_surf = game_font.render(f"Game Over! Final Score: {score}", False, "White")
        game_over_rect = game_over_surf.get_rect(center=(400, 200))
        screen.blit(game_over_surf, game_over_rect)

    # flip the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # Limits game loop to 60 FPS

pygame.quit()
