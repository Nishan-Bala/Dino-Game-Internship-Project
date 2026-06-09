"""Dino Game in Python

A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @bassemfarid, no one or nothing else. 🤖
"""

import pygame
import random
from operator import itemgetter
# Initialize Pygame and create a window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
running = True  # Pygame main loop, kills pygame when False

score_file = "scores.txt"

def load_scores():
    scores = []
    file = open(score_file, "r")
    for line in file:
        line = line.strip()
        if "," in line:
            name, score = line.rsplit(",", 1)
            scores.append((name, int(score)))
            scores.sort(key=itemgetter(1), reverse=True)
    file.close()
    return scores

def save_score(name, score):
    scores = load_scores()
    scores.append((name, score))
    scores.sort(key = itemgetter(1), reverse=True)

    file = open(score_file, "w")
    for name, score in scores:
        file.write(f"{name},{score}\n")
    file.close()

def cal_score(start_time, total_time_paused):
    current_time = pygame.time.get_ticks() - start_time - total_time_paused
    score = int(current_time / 100)
    return score

is_entering_name = False
username = ""
    

is_settings = False
sound_effects_vol = 50
jump_sound = pygame.mixer.Sound("audio/jump.MP3")
jump_sound.set_volume(sound_effects_vol/100)

# Game state variables
small_font = pygame.font.Font(pygame.font.get_default_font(), 28)
mini_font = pygame.font.Font(pygame.font.get_default_font(), 18)
current_font_color = "Black"
is_playing = True  # Whether in game or in menu
GROUND_Y = 300  # The Y-coordinate of the ground level
JUMP_GRAVITY_START_SPEED = -15  # The speed at which the player jumps
players_gravity_speed = 0  # The current speed at which the player falls
can_double_jump = False
start_time = 0
score = 0
is_paused = False
time_paused = 0
total_time_paused = 0

# Load level assets
is_night = False
HEART_SURF = pygame.image.load("graphics/level/heart.png").convert_alpha()
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
SKY_NIGHT_SURF = pygame.image.load("graphics/level/sky_night.png").convert()
current_sky = SKY_SURF
GROUND_SURF_1 = pygame.image.load("graphics/level/ground.png").convert()
GROUND_SURF_2 = pygame.image.load("graphics/level/ground.png").convert()
ground_rect_1 = GROUND_SURF_1.get_rect(topleft = (800, GROUND_Y))
ground_rect_2 = GROUND_SURF_2.get_rect(topleft = (0, GROUND_Y))
cloud_1 = pygame.image.load("graphics/level/cloud_1.png").convert_alpha()
cloud_2 = pygame.image.load("graphics/level/cloud_2.png").convert_alpha()
cloud_1_rect = cloud_1.get_rect(topleft=(100, 50))
cloud_2_rect = cloud_2.get_rect(topleft=(500, 80))
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
heart_hitbox = heart_rect.inflate(-20,-20)
armour_powerup_surf = pygame.image.load("graphics/power_ups/armour.png").convert_alpha()
armour_powerup_surf = pygame.transform.scale(armour_powerup_surf, (50, 50))
armour_rect = armour_powerup_surf.get_rect(bottomleft=(800, GROUND_Y))
armour_hitbox = armour_rect.inflate(-10, -10)
armour_active = False
armour_timer = 0
ARMOUR_DURATION = 600


# Load sprite assets
player_jump = pygame.image.load("graphics/player/player_jump.png").convert_alpha()
player_jump_night = pygame.image.load("graphics/player/player_jump_night.png").convert_alpha()
current_jump = player_jump
player_walk_1 = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_walk_2 = pygame.image.load("graphics/player/player_walk_2.png").convert_alpha()
player_walk_1_night = pygame.image.load("graphics/player/player_walk_1_night.png").convert_alpha()
player_walk_2_night = pygame.image.load("graphics/player/player_walk_2_night.png").convert_alpha()
player_walk_1_armour = pygame.image.load("graphics/player/player_walk_1_armour.png").convert_alpha()
player_walk_2_armour = pygame.image.load("graphics/player/player_walk_2_armour.png").convert_alpha()
player_walk_1_night_armour = pygame.image.load("graphics/player/player_walk_1_night_armour.png").convert_alpha()
player_walk_2_night_armour = pygame.image.load("graphics/player/player_walk_2_night_armour.png").convert_alpha()
player_frames = [player_walk_1, player_walk_2] # Animation frame list
player_frame_index = 0  # Tracks which frame is currently shown
animation_speed = 8    # How many game frames to wait before switching sprite frame
animation_counter = 0   # Counts up each game frame to trigger animation switch


player_surf = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))
player_hitbox = player_rect.inflate(-11, -8)
egg_rotation_angle = 0
egg_surf = pygame.image.load("graphics/egg/egg_1.png").convert_alpha()
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))
egg_cracked = pygame.image.load("graphics/egg/egg_cracked.png").convert_alpha()
egg_hitbox = egg_rect.inflate(-7,-7)
egg_width = egg_surf.get_width()
is_double_egg = False
is_cracked = False

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
                jump_sound.play()
                if player_rect.bottom >= GROUND_Y:
                    players_gravity_speed = -25 if spring_active else JUMP_GRAVITY_START_SPEED
                    can_double_jump = True
                elif can_double_jump:
                    players_gravity_speed = -25 if spring_active else JUMP_GRAVITY_START_SPEED
                    can_double_jump = False
            elif is_playing:
                if event.type == pygame.KEYDOWN:
 
                    if event.key == pygame.K_ESCAPE:
                        if is_settings:
                            is_settings = False
                        else:
                            is_paused = not is_paused
                            if is_paused:
                                time_paused = pygame.time.get_ticks()
                            else:
                                total_time_paused += pygame.time.get_ticks() - time_paused
 
                    elif event.key == pygame.K_s and is_paused:
                        is_settings = not is_settings
 
                    elif event.key == pygame.K_q and is_paused and not is_settings:
                        running = False
 
                    elif is_settings:
                        if event.key == pygame.K_LEFT:
                            sound_effects_vol = max(0, sound_effects_vol - 5)
                            jump_sound.set_volume(sound_effects_vol / 100)
                        elif event.key == pygame.K_RIGHT:
                            sound_effects_vol = min(100, sound_effects_vol + 5)
                            jump_sound.set_volume(sound_effects_vol / 100)
                        elif event.key == pygame.K_n:
                            is_night = not is_night
                            if is_night:
                                    current_sky = SKY_NIGHT_SURF
                                    current_jump = player_jump_night
                                    if armour_active:
                                        player_frames = [player_walk_1_night_armour, player_walk_2_night_armour]
                                    else:
                                        player_frames = [player_walk_1_night, player_walk_2_night]
                                    current_font_color = "White"
                            else:
                                current_sky = SKY_SURF
                                current_jump = player_jump
                                if armour_active:
                                    player_frames = [player_walk_1_armour, player_walk_2_armour]
                                else:
                                    player_frames = [player_walk_1, player_walk_2]
                                current_font_color = "Black"
        else:
            if is_entering_name:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and username.strip():
                        save_score(username.strip(), score)
                        is_entering_name = False
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif event.unicode.isprintable() and len(username) < 15:
                        username += event.unicode
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    is_playing = True
                    lives = 3
                    is_invincible = False
                    egg_rect.left = 800
                    start_time = pygame.time.get_ticks()
                    spring_active = False
                    spring_timer = 0
                    armour_active = False
                    armour_timer = 0
                    is_cracked = False
                    time_paused = 0
                    total_time_paused = 0
                    username = ""
                    # Reset player frames to normal
                    if is_night:
                        player_frames = [player_walk_1_night, player_walk_2_night]
                    else:
                        player_frames = [player_walk_1, player_walk_2]

    if is_playing:
        if not is_paused:
            if spring_active:
                spring_timer -= 1
                if spring_timer <= 0:
                    spring_active = False
            if armour_active:
                armour_timer -= 1
                if armour_timer <= 0:
                    armour_active = False
                    if is_night:
                        player_frames = [player_walk_1_night, player_walk_2_night]
                    else:
                        player_frames = [player_walk_1, player_walk_2]
            time_paused = 0
            screen.fill("purple")  
            # Wipe the screen# Blit the level assets
            screen.blit(current_sky, (0, 0))
            ground_rect_1.x -= 5
            ground_rect_2.x -= 5
            if ground_rect_1.right < 0:
                ground_rect_1.left = ground_rect_2.right
            if ground_rect_2.right < 0:
                ground_rect_2.left = ground_rect_1.right
            screen.blit(GROUND_SURF_1, ground_rect_1)
            screen.blit(GROUND_SURF_2, ground_rect_2)
            cloud_1_rect.x -= 1
            cloud_2_rect.x -= 2
            if cloud_1_rect.right < 0:
                cloud_1_rect.left = 800
            if cloud_2_rect.right < 0:
                cloud_2_rect.left = 800
            screen.blit(cloud_1, cloud_1_rect)
            screen.blit(cloud_2, cloud_2_rect)

            score = cal_score(start_time, total_time_paused)
            score_surf = game_font.render(f"Score: {score}", False, current_font_color)
            score_rect = score_surf.get_rect(center=(400, 50))
            screen.blit(score_surf, score_rect)

            egg_speed = 5 + min(score // 150, 10)
            egg_rect.x -= egg_speed
            if egg_rect.right <= 0:
                egg_rect.left = 800
                is_double_egg = random.random() < 0.21
                is_cracked = False
 
            egg_rotation_angle = (egg_rotation_angle + egg_speed * 1.4) % 360
            rotated_egg = pygame.transform.rotate(egg_surf, egg_rotation_angle)
            rotated_rect = rotated_egg.get_rect(center=egg_rect.center)
            if is_cracked:
                screen.blit(egg_cracked, egg_rect)
            else:
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
                elif roll < 0.6:
                    if egg_rect.left > 200:
                        active_powerup = 'armour'
                        armour_rect.left = 800

            if active_powerup == 'spring':
                spring_rect.x -= 5
                spring_hitbox.center = spring_rect.center
                screen.blit(spring_powerup_surf, spring_rect)
                spring_hitbox.center = spring_rect.center
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
            elif active_powerup == 'armour':
                armour_rect.x -= 5
                armour_hitbox.center = armour_rect.center
                screen.blit(armour_powerup_surf, armour_rect)
                if armour_rect.right <= 0:
                    active_powerup = None
                if armour_hitbox.colliderect(player_hitbox):
                    armour_active = True
                    armour_timer = ARMOUR_DURATION
                    active_powerup = None
                    if is_night:
                        player_frames = [player_walk_1_night_armour, player_walk_2_night_armour]
                    else:
                        player_frames = [player_walk_1_armour, player_walk_2_armour]

            if spring_active:
                spring_timer_text = small_font.render(f"Jump Boost: {(spring_timer / 60):.2f} s", False, "White")
                spring_timer_text_rect = spring_timer_text.get_rect(center=(650, 350))
                screen.blit(spring_timer_text, spring_timer_text_rect)
            
            if armour_active:
                armour_timer_text = small_font.render(f"Armour: {(armour_timer / 60):.2f} s", False, "Cyan")
                screen.blit(armour_timer_text, armour_timer_text.get_rect(center=(620, 375)))
                


            pygame.draw.rect(screen, "red", heart_hitbox, 2)
            pygame.draw.rect(screen, "red", spring_hitbox, 2)

            
            if player_rect.bottom >= GROUND_Y:
                animation_counter += 1
                if animation_counter >= animation_speed:
                    animation_counter = 0
                    player_frame_index = (player_frame_index + 1) % len(player_frames)
                player_surf = player_frames[player_frame_index]
            else:
                player_surf = current_jump
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
                if armour_active:
                    # Armour takes the hit: crack the egg, remove armour, go invincible briefly
                    is_cracked = True
                    armour_active = False
                    armour_timer = 0
                    is_invincible = True
                    invincible_timer = invincible_duration
                    if is_night:
                        player_frames = [player_walk_1_night, player_walk_2_night]
                    else:
                        player_frames = [player_walk_1, player_walk_2]
                else:
                    lives -= 1
                    is_invincible = True
                    invincible_timer = invincible_duration
                    if lives <= 0:
                        is_playing = False
                        is_entering_name = True
                        username = ""

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
            if is_settings:
                setting_surf = game_font.render("Settings Menu", False, "white")
                screen.blit(setting_surf, setting_surf.get_rect(center=(400, 110)))
                sound_effects_vol_label = small_font.render(f"Sound Effests Volume: {sound_effects_vol}", False, "white")
                screen.blit(sound_effects_vol_label, sound_effects_vol_label.get_rect(center=(400, 195)))

                bar_x, bar_y, bar_w, bar_h = 200, 215, 400, 22
                pygame.draw.rect(screen, "gray", (bar_x, bar_y, bar_w, bar_h))
                pygame.draw.rect(screen, "white", (bar_x, bar_y, int(bar_w * sound_effects_vol / 100), bar_h))
                pygame.draw.rect(screen, "white", (bar_x, bar_y, bar_w, bar_h), 2)

                instruct_surf = mini_font.render("<- -> to adjust sound_effects_vol", False, "white")
                screen.blit(instruct_surf, instruct_surf.get_rect(center = (400,270)))

                if is_night:
                    night = "ON"
                    night_color = "Green"
                else:
                    night = "OFF"
                    night_color = "Red"
                night_surf = small_font.render(f"Night Mode: {night}", False, night_color)
                screen.blit(night_surf, night_surf.get_rect(center =(400, 310)))


                back_surf = mini_font.render("ESC to go back to pause menu", False, "white")
                screen.blit(back_surf, back_surf.get_rect(center=(200, 380)))
            else:
                pause_surf = game_font.render("PAUSED", False, "White")
                resume_surf = small_font.render("ESC to Resume", False, "Gray")
                quit_surf = small_font.render("Q to Quit", False, "Gray")
                to_settings_surf = small_font.render("S to Settings", False, "Gray")
                
                screen.blit(pause_surf, pause_surf.get_rect(center=(400, 160)))
                screen.blit(resume_surf, resume_surf.get_rect(center=(400, 215)))
                screen.blit(quit_surf, quit_surf.get_rect(center=(400, 245)))
                screen.blit(to_settings_surf, to_settings_surf.get_rect(center = (400, 275)))

    # When game is over, display game over message
    else:
        screen.fill("black")
        screen.blit(game_font.render(f"Game Over! Score: {score}", False, "White"),
        game_font.render(f"Game Over! Score: {score}", False, "White").get_rect(center=(400, 80)))

        if is_entering_name:
            screen.blit(small_font.render("Enter your name:", False, "Gray"), small_font.render("Enter your name:", False, "Gray").get_rect(center=(400, 180)))
            screen.blit(game_font.render(username + "|", False, "White"), game_font.render(username + "|", False, "White").get_rect(center=(400, 240)))
            screen.blit(mini_font.render("Press ENTER to save", False, "Gray"), mini_font.render("Press ENTER to save", False, "Gray").get_rect(center=(400, 310)))
        else:
            scores = load_scores()
            for i, (name, s) in enumerate(scores[:5]):
                screen.blit(small_font.render(f"{i+1}. {name}  {s}", False, "White"),
                        small_font.render(f"{i+1}. {name}  {s}", False, "White").get_rect(center=(400, 170 + i * 36)))
            screen.blit(small_font.render("SPACE to play again", False, "Gray"), small_font.render("SPACE to play again", False, "Gray").get_rect(center=(400, 360)))

    # flip the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # Limits game loop to 60 FPS

pygame.quit()
