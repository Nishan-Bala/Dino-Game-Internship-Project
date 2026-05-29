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

# Load level assets
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
game_font = pygame.font.Font(pygame.font.get_default_font(), 50)
score_surf = game_font.render("SCORE?", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))

# Load sprite assets
player_surf = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))
player_hitbox = player_rect.inflate(-6, -6)
egg_surf = pygame.image.load("graphics/egg/egg_1.png").convert_alpha()
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))
egg_hitbox = egg_rect.inflate(-4,-4)
egg_width = egg_surf.get_width()
is_double_egg = False


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
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    can_double_jump = True
                elif can_double_jump:
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    can_double_jump = False
        else:
            # When player wants to play again by pressing SPACE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                is_playing = True
                egg_rect.left = 800
                start_time = pygame.time.get_ticks()

    if is_playing:
        screen.fill("purple")  # Wipe the screen

        # Blit the level assets
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
            is_double_egg = random.random() < 0.2 #20% chance of 2 eggs
        screen.blit(egg_surf, egg_rect)
        if is_double_egg:
            screen.blit(egg_surf, (egg_rect.x + egg_width, egg_rect.y))
            egg_hitbox = pygame.Rect(0, 0, (egg_width*2) - 4, egg_rect.height - 4)
            egg_hitbox.center = (egg_rect.centerx + (egg_width / 2), egg_rect.centery)
        else:
            egg_hitbox = pygame.Rect(0, 0, (egg_width) - 4, egg_rect.height - 4)
            egg_hitbox.center = egg_rect.center
        pygame.draw.rect(screen, "red", egg_hitbox, 2)

        # Adjust player's vertical location then blit it
        players_gravity_speed += 1
        player_rect.y += players_gravity_speed
        if player_rect.bottom > GROUND_Y:
            player_rect.bottom = GROUND_Y
        screen.blit(player_surf, player_rect)
        player_hitbox.center = player_rect.center
        pygame.draw.rect(screen, "red", player_hitbox, 2)

        # When player collides with enemy, game ends
        if egg_hitbox.colliderect(player_hitbox):
            is_playing = False

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
