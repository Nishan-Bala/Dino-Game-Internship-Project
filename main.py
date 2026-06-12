import pygame
import random
from operator import itemgetter

# Initialize Pygame and create a window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Hurdle Champion")
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
    scores.sort(key=itemgetter(1), reverse=True)

    file = open(score_file, "w")
    for name, score in scores:
        file.write(f"{name},{score}\n")
    file.close()

# Updated to include extra score from medals
def cal_score(start_time, total_time_paused, bonus_score):
    current_time = pygame.time.get_ticks() - start_time - total_time_paused
    base_score = int(current_time / 100)
    return base_score + bonus_score

is_entering_name = False
username = ""

is_settings = False
sound_effects_vol = 50
jump_sound = pygame.mixer.Sound("audio/jump.MP3")
jump_sound.set_volume(sound_effects_vol / 100)

# Game state variables
small_font = pygame.font.Font(pygame.font.get_default_font(), 28)
mini_font = pygame.font.Font(pygame.font.get_default_font(), 18)
current_font_color = "Black"

is_start_screen = True
is_leaderboard = False
is_playing = False

GROUND_Y = 300  # The Y-coordinate of the ground (running track surface)
JUMP_GRAVITY_START_SPEED = -15  # The speed at which the athlete jumps
players_gravity_speed = 0  # The current speed at which the athlete falls
can_double_jump = False
start_time = 0
score = 0
extra_score = 0 # Points added by medals
is_paused = False
time_paused = 0
total_time_paused = 0

# ─── MECHANICAL VARIABLES ────────────────────────────────────────────────────
# Slide Mechanic
is_sliding = False
slide_timer = 0
SLIDE_DURATION = 40

# Dash Mechanic
is_dashing = False
dash_timer = 0
DASH_DURATION = 20
dash_cooldown = 0
DASH_COOLDOWN_MAX = 300

# Medal Collectibles
active_medal = None
medal_type = ""
medal_rect = pygame.Rect(800, 0, 30, 30)
medal_timer = 0
MEDAL_INTERVAL = 150

# Load level assets — stadium environment
HEART_SURF = pygame.image.load("graphics/level/heart.png").convert_alpha()
STADIUM_SKY_SURF = pygame.transform.scale(pygame.image.load("graphics/level/background.png").convert(),(800,300))
TRACK_SURF_1 = pygame.image.load("graphics/level/ground.png").convert()
TRACK_SURF_2 = pygame.image.load("graphics/level/ground.png").convert()
track_rect_1 = TRACK_SURF_1.get_rect(topleft=(800, GROUND_Y))
track_rect_2 = TRACK_SURF_2.get_rect(topleft=(0, GROUND_Y))

# Stadium decorations (replaces clouds)
banner_1 = pygame.image.load("graphics/level/cloud_1.png").convert_alpha()
banner_2 = pygame.image.load("graphics/level/cloud_2.png").convert_alpha()
banner_1_rect = banner_1.get_rect(topleft=(100, 50))
banner_2_rect = banner_2.get_rect(topleft=(500, 80))

game_font = pygame.font.Font(pygame.font.get_default_font(), 50)
score_surf = game_font.render("SCORE?", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))

# Powerup system
active_powerup = None
powerup_timer = 0
POWERUP_INTERVAL = 300

# Energy Boost powerup
energy_boost_surf = pygame.image.load("graphics/power_ups/spring.png").convert_alpha()
energy_boost_rect = energy_boost_surf.get_rect(bottomleft=(800, GROUND_Y))
energy_boost_surf = pygame.transform.scale(energy_boost_surf, (40, 40))
energy_boost_hitbox = energy_boost_rect.inflate(-5, -5)
energy_boost_active = False
energy_boost_timer = 0
ENERGY_BOOST_DURATION = 600

# Medical Kit powerup
medkit_surf = pygame.image.load("graphics/power_ups/health_powerup.png").convert_alpha()
medkit_surf = pygame.transform.scale(medkit_surf, (64, 64))
medkit_rect = medkit_surf.get_rect(bottomleft=(800, 100))
medkit_hitbox = medkit_rect.inflate(-20, -20)

# ─── Athlete sprite assets ────────────────────────────────────────────────────
PLAYER_SIZE = (80, 125)
athlete_run_1 = pygame.transform.scale(pygame.image.load("graphics/player/player_run_1.png").convert_alpha(), PLAYER_SIZE)
athlete_run_2 = pygame.transform.scale(pygame.image.load("graphics/player/player_run_2.png").convert_alpha(), PLAYER_SIZE)
athlete_run_3 = pygame.transform.scale(pygame.image.load("graphics/player/player_run_3.png").convert_alpha(), PLAYER_SIZE)
athlete_run_4 = pygame.transform.scale(pygame.image.load("graphics/player/player_run_4.png").convert_alpha(), PLAYER_SIZE)
# Jump frame
athlete_jump = pygame.transform.scale(pygame.image.load("graphics/player/player_jump_1.png").convert_alpha(), PLAYER_SIZE)
athlete_slide = pygame.transform.scale(pygame.image.load("graphics/player/player_sliding.png").convert_alpha(), PLAYER_SIZE)

# Active frame list — 4 running frames
athlete_run_frames = [athlete_run_1, athlete_run_2, athlete_run_3, athlete_run_4]
player_frames = athlete_run_frames

player_frame_index = 0   
animation_speed = 8      
animation_counter = 0    

# Player rect / hitbox
player_surf = athlete_run_1
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))
player_hitbox = player_rect.inflate(-11, -8)

# ─── Hurdle obstacle assets ────────────────────────────────────────────────────
hurdle_surf = pygame.transform.scale(pygame.image.load("graphics/obstacle/hurdle.png").convert_alpha(),(75,75))
hurdle_rect = hurdle_surf.get_rect(bottomleft=(800, GROUND_Y))
hurdle_width = hurdle_surf.get_width()
hurdle_type = "normal"

# Flying Obstacles Assets
javelin_surf = pygame.transform.scale(pygame.image.load("graphics/obstacle/javelin.png").convert_alpha(), (100, 20))
shoe_surf = pygame.transform.scale(pygame.image.load("graphics/obstacle/shoe.png").convert_alpha(), (40, 40))
football_1 = pygame.transform.scale(pygame.image.load("graphics/obstacle/football_1.png").convert_alpha(), (50, 30))
football_2 = pygame.transform.scale(pygame.image.load("graphics/obstacle/football_2.png").convert_alpha(), (50, 30))
football_frames = [football_1, football_2]

# Animation Trackers for Flying Obstacles
shoe_angle = 0
football_anim_counter = 0
football_frame_index = 0

lives = 3
is_invincible = False
invincible_timer = 0
invincible_duration = 90

bronze_medal_surf = pygame.Surface((30, 30), pygame.SRCALPHA); bronze_medal_surf.fill((205, 127, 50))
silver_medal_surf = pygame.Surface((30, 30), pygame.SRCALPHA); silver_medal_surf.fill((192, 192, 192))
gold_medal_surf = pygame.Surface((30, 30), pygame.SRCALPHA); gold_medal_surf.fill((255, 215, 0))

# ─────────────────────────────────────────────────────────────────────────────
while running:
    # Poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ── Start screen events ───────────────────────────────────────────────
        elif is_start_screen:
            if event.type == pygame.KEYDOWN:
                if is_settings:
                    if event.key == pygame.K_ESCAPE:
                        is_settings = False
                    elif event.key == pygame.K_LEFT:
                        sound_effects_vol = max(0, sound_effects_vol - 5)
                        jump_sound.set_volume(sound_effects_vol / 100)
                    elif event.key == pygame.K_RIGHT:
                        sound_effects_vol = min(100, sound_effects_vol + 5)
                        jump_sound.set_volume(sound_effects_vol / 100)
                elif is_leaderboard:
                    if event.key == pygame.K_ESCAPE:
                        is_leaderboard = False
                else:
                    if event.key == pygame.K_SPACE:
                        is_start_screen = False
                        is_playing = True
                        start_time = pygame.time.get_ticks()
                    elif event.key == pygame.K_s:
                        is_settings = True
                    elif event.key == pygame.K_l:
                        is_leaderboard = True
                    elif event.key == pygame.K_q:
                        running = False

        # ── In-game events ────────────────────────────────────────────────────
        elif is_playing:
            if (
                event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
                or event.type == pygame.MOUSEBUTTONDOWN
            ):
                jump_sound.play()
                is_sliding = False 
                if player_rect.bottom >= GROUND_Y:
                    players_gravity_speed = -25 if energy_boost_active else JUMP_GRAVITY_START_SPEED
                    can_double_jump = True
                elif can_double_jump:
                    players_gravity_speed = -25 if energy_boost_active else JUMP_GRAVITY_START_SPEED
                    can_double_jump = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN and player_rect.bottom >= GROUND_Y and not is_dashing:
                    is_sliding = True
                    slide_timer = SLIDE_DURATION
                
                elif (event.key == pygame.K_LSHIFT or event.key == pygame.K_z) and dash_cooldown <= 0:
                    is_dashing = True
                    dash_timer = DASH_DURATION
                    dash_cooldown = DASH_COOLDOWN_MAX
                    is_sliding = False

                elif event.key == pygame.K_ESCAPE:
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

        # ── Game-over / name-entry events ─────────────────────────────────────
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
                    hurdle_rect.left = 800
                    start_time = pygame.time.get_ticks()
                    energy_boost_active = False
                    energy_boost_timer = 0
                    time_paused = 0
                    total_time_paused = 0
                    username = ""
                    player_frames = athlete_run_frames
                    
                    extra_score = 0
                    is_sliding = False
                    is_dashing = False
                    dash_cooldown = 0
                    active_medal = None

    # ── Draw Start Screen ─────────────────────────────────────────────────────
    if is_start_screen:
        screen.fill("black")
        if is_settings:
            setting_surf = game_font.render("Settings Menu", False, "white")
            screen.blit(setting_surf, setting_surf.get_rect(center=(400, 110)))
            sound_effects_vol_label = small_font.render(
                f"Sound Effects Volume: {sound_effects_vol}", False, "white"
            )
            screen.blit(sound_effects_vol_label, sound_effects_vol_label.get_rect(center=(400, 195)))

            bar_x, bar_y, bar_w, bar_h = 200, 215, 400, 22
            pygame.draw.rect(screen, "gray", (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, "white", (bar_x, bar_y, int(bar_w * sound_effects_vol / 100), bar_h))
            pygame.draw.rect(screen, "white", (bar_x, bar_y, bar_w, bar_h), 2)

            instruct_surf = mini_font.render("<- -> to adjust volume", False, "white")
            screen.blit(instruct_surf, instruct_surf.get_rect(center=(400, 270)))

            back_surf = mini_font.render("ESC to go back", False, "white")
            screen.blit(back_surf, back_surf.get_rect(center=(400, 370)))

        elif is_leaderboard:
            title_surf = game_font.render("Top 5 Athletes", False, "White")
            screen.blit(title_surf, title_surf.get_rect(center=(400, 80)))

            scores = load_scores()

            if not scores:
                none_surf = small_font.render("No records yet!", False, "Gray")
                screen.blit(none_surf, none_surf.get_rect(center=(400, 200)))
            else:
                for i, (name, s) in enumerate(scores[:5]):
                    entry_surf = small_font.render(f"{i+1}. {name}  {s}", False, "White")
                    screen.blit(entry_surf, entry_surf.get_rect(center=(400, 150 + i * 36)))

            back_surf = mini_font.render("ESC to go back", False, "Gray")
            screen.blit(back_surf, back_surf.get_rect(center=(400, 360)))

        else:
            title_surf = game_font.render("Hurdle Champion", False, "White")
            screen.blit(title_surf, title_surf.get_rect(center=(400, 100)))

            play_surf = small_font.render("SPACE - Race | DOWN - Slide | LSHIFT - Dash", False, "Gray")
            screen.blit(play_surf, play_surf.get_rect(center=(400, 180)))

            set_surf = small_font.render("S - Settings", False, "Gray")
            screen.blit(set_surf, set_surf.get_rect(center=(400, 220)))

            lead_surf = small_font.render("L - Leaderboard", False, "Gray")
            screen.blit(lead_surf, lead_surf.get_rect(center=(400, 260)))

            quit_surf = small_font.render("Q - Quit", False, "Gray")
            screen.blit(quit_surf, quit_surf.get_rect(center=(400, 300)))

    # ── Draw Gameplay ─────────────────────────────────────────────────────────
    elif is_playing:
        if not is_paused:
            if energy_boost_active:
                energy_boost_timer -= 1
                if energy_boost_timer <= 0:
                    energy_boost_active = False

            if is_sliding:
                slide_timer -= 1
                if slide_timer <= 0:
                    is_sliding = False
            
            if is_dashing:
                dash_timer -= 1
                if dash_timer <= 0:
                    is_dashing = False
            if dash_cooldown > 0:
                dash_cooldown -= 1

            time_paused = 0
            move_speed = (8 + min(score // 150, 10)) * (1.5 if is_dashing else 1.0)
            
            # ── Stadium background ────────────────────────────────────────────
            screen.fill("purple")
            screen.blit(STADIUM_SKY_SURF, (0, 0))

            track_rect_1.x -= move_speed
            track_rect_2.x -= move_speed
            if track_rect_1.right < 0:
                track_rect_1.left = track_rect_2.right
            if track_rect_2.right < 0:
                track_rect_2.left = track_rect_1.right
            screen.blit(TRACK_SURF_1, track_rect_1)
            screen.blit(TRACK_SURF_2, track_rect_2)

            banner_1_rect.x -= 1
            banner_2_rect.x -= 2
            if banner_1_rect.right < 0:
                banner_1_rect.left = 800
            if banner_2_rect.right < 0:
                banner_2_rect.left = 800
            screen.blit(banner_1, banner_1_rect)
            screen.blit(banner_2, banner_2_rect)

            score = cal_score(start_time, total_time_paused, extra_score)
            score_surf = game_font.render(f"Score: {score}", False, current_font_color)
            score_rect = score_surf.get_rect(center=(400, 50))
            screen.blit(score_surf, score_rect)

            # ── Obstacle Logic with Flying Objects ────────────────────────────
            hurdle_rect.x -= move_speed
            
            expiry_right = hurdle_rect.right + (hurdle_width if hurdle_type == "double" else 0)

            # Spawn randomly between the obstacles
            if expiry_right <= 0:
                hurdle_rect.left = 800
                roll = random.random()
                if roll < 0.2:
                    hurdle_type = "double"
                elif roll < 0.4:
                    hurdle_type = random.choice(["javelin", "shoe", "football"])
                else:
                    hurdle_type = "normal"

            # Flying Obstacles height offset
            flying_y = GROUND_Y - 75

            if hurdle_type == "javelin":
                # Render Javelin moving linearly
                javelin_rect = javelin_surf.get_rect(bottomleft=(hurdle_rect.x, flying_y))
                screen.blit(javelin_surf, javelin_rect)
                hurdle_hitbox = javelin_rect.inflate(-10, -10)
                
            elif hurdle_type == "shoe":
                # Render Shoe with continuous rotation
                shoe_angle = (shoe_angle + 10) % 360
                rotated_shoe = pygame.transform.rotate(shoe_surf, shoe_angle)
                shoe_rect = rotated_shoe.get_rect(center=(hurdle_rect.x + 37, flying_y - 15))
                screen.blit(rotated_shoe, shoe_rect)
                # Static hitbox logic so it feels fair when spinning
                hurdle_hitbox = pygame.Rect(0, 0, 30, 30)
                hurdle_hitbox.center = shoe_rect.center
                
            elif hurdle_type == "football":
                # Render Football and cycle animations
                football_anim_counter += 1
                if football_anim_counter >= 10:
                    football_anim_counter = 0
                    football_frame_index = (football_frame_index + 1) % len(football_frames)
                
                current_football = football_frames[football_frame_index]
                football_rect = current_football.get_rect(bottomleft=(hurdle_rect.x, flying_y))
                screen.blit(current_football, football_rect)
                hurdle_hitbox = football_rect.inflate(-10, -10)

            elif hurdle_type == "double":
                screen.blit(hurdle_surf, hurdle_rect)
                second_center = (hurdle_rect.centerx + hurdle_width, hurdle_rect.centery)
                screen.blit(hurdle_surf, hurdle_surf.get_rect(center=second_center))
                hurdle_hitbox = pygame.Rect(0, 0, (hurdle_width * 2) - 4, hurdle_rect.height - 4)
                hurdle_hitbox.center = (hurdle_rect.centerx + (hurdle_width / 2), hurdle_rect.centery)
                
            else:
                screen.blit(hurdle_surf, hurdle_rect)
                hurdle_hitbox = hurdle_rect.inflate(-26, -17)
                hurdle_hitbox.center = hurdle_rect.center

            pygame.draw.rect(screen, "red", hurdle_hitbox, 2)

            # ── Medal Collectible Logic ───────────────────────────────────────
            medal_timer += 1
            if medal_timer >= MEDAL_INTERVAL and active_medal is None:
                medal_timer = 0
                if random.random() < 0.6: 
                    active_medal = True
                    roll = random.random()
                    if roll < 0.1:
                        medal_type = "gold"
                    elif roll < 0.4:
                        medal_type = "silver"
                    else:
                        medal_type = "bronze"
                    
                    medal_rect.left = 800
                    medal_rect.bottom = random.choice([GROUND_Y, GROUND_Y - 80, GROUND_Y - 140])

            if active_medal:
                medal_rect.x -= move_speed
                if medal_type == "gold":
                    screen.blit(gold_medal_surf, medal_rect)
                elif medal_type == "silver":
                    screen.blit(silver_medal_surf, medal_rect)
                else:
                    screen.blit(bronze_medal_surf, medal_rect)
                
                if medal_rect.right <= 0:
                    active_medal = None
                
                if medal_rect.colliderect(player_hitbox):
                    if medal_type == "gold":
                        extra_score += 300
                    elif medal_type == "silver":
                        extra_score += 100
                    else:
                        extra_score += 50
                    active_medal = None

            # ── Powerup spawning and movement ─────────────────────────────────
            powerup_timer += 1
            if powerup_timer >= POWERUP_INTERVAL and active_powerup is None:
                powerup_timer = 0
                roll = random.random()
                if roll < 0.45:
                    if hurdle_rect.left > 200:
                        active_powerup = 'energy_boost'
                        energy_boost_rect.left = 800
                elif roll < 0.5:
                    if hurdle_rect.left > 200:
                        active_powerup = 'medkit'
                        medkit_rect.left = 800

            if active_powerup == 'energy_boost':
                energy_boost_rect.x -= move_speed
                energy_boost_hitbox.center = energy_boost_rect.center
                screen.blit(energy_boost_surf, energy_boost_rect)
                if energy_boost_rect.right <= 0:
                    active_powerup = None
                if energy_boost_hitbox.colliderect(player_hitbox):
                    energy_boost_active = True
                    energy_boost_timer = ENERGY_BOOST_DURATION
                    active_powerup = None

            elif active_powerup == 'medkit':
                medkit_rect.x -= move_speed
                medkit_hitbox.center = medkit_rect.center
                screen.blit(medkit_surf, medkit_rect)
                if medkit_rect.right <= 0:
                    active_powerup = None
                if medkit_hitbox.colliderect(player_hitbox):
                    lives = min(lives + 1, 7)
                    active_powerup = None

            # Active powerup HUD timers
            if energy_boost_active:
                boost_text = small_font.render(
                    f"Energy Boost: {(energy_boost_timer / 60):.2f} s", False, "White"
                )
                screen.blit(boost_text, boost_text.get_rect(center=(650, 350)))
            
            if dash_cooldown > 0:
                dash_text = mini_font.render(f"Dash CD: {(dash_cooldown / 60):.1f} s", False, "White")
                screen.blit(dash_text, dash_text.get_rect(center=(650, 380)))
            elif not is_dashing:
                dash_text = mini_font.render("Dash READY (LSHIFT)", False, "Green")
                screen.blit(dash_text, dash_text.get_rect(center=(650, 380)))

            # ── Athlete animation & physics ───────────────────────────────────
            players_gravity_speed += 1
            player_rect.y += players_gravity_speed
            if player_rect.bottom > GROUND_Y:
                player_rect.bottom = GROUND_Y

            if is_sliding and player_rect.bottom == GROUND_Y:
                player_surf = athlete_slide
                player_hitbox.height = PLAYER_SIZE[1] // 2
                player_hitbox.width = PLAYER_SIZE[0] - 10
            else:
                player_hitbox.height = PLAYER_SIZE[1] - 8
                player_hitbox.width = PLAYER_SIZE[0] - 11
                if player_rect.bottom >= GROUND_Y:
                    animation_counter += 1 + (1 if is_dashing else 0)
                    if animation_counter >= animation_speed:
                        animation_counter = 0
                        player_frame_index = (player_frame_index + 1) % len(player_frames)
                    player_surf = player_frames[player_frame_index]
                else:
                    player_surf = athlete_jump
                    animation_counter = 0
            
            player_hitbox.midbottom = player_rect.midbottom
            
            if is_dashing:
                player_surf = player_surf.copy()
                player_surf.fill((255, 100, 100), special_flags=pygame.BLEND_RGB_ADD)

            screen.blit(player_surf, player_rect)
            pygame.draw.rect(screen, "red", player_hitbox, 2)

            # ── Collision detection ───────────────────────────────────────────
            if hurdle_hitbox.colliderect(player_hitbox):
                if is_dashing:
                    hurdle_rect.left = -200 
                elif not is_invincible:
                    lives -= 1
                    is_invincible = True
                    invincible_timer = invincible_duration
                    if lives <= 0:
                        is_playing = False
                        is_entering_name = True
                        username = ""

            if is_invincible:
                invincible_timer -= 1
                if invincible_timer <= 0:
                    is_invincible = False

            for i in range(lives):
                screen.blit(HEART_SURF, (10 + i * 50, 10))

        # ── Pause overlay ─────────────────────────────────────────────────────
        if is_paused:
            pause_overlay = pygame.Surface((800, 400), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 150))
            screen.blit(pause_overlay, (0, 0))

            if is_settings:
                setting_surf = game_font.render("Settings Menu", False, "white")
                screen.blit(setting_surf, setting_surf.get_rect(center=(400, 110)))
                sound_effects_vol_label = small_font.render(
                    f"Sound Effects Volume: {sound_effects_vol}", False, "white"
                )
                screen.blit(sound_effects_vol_label, sound_effects_vol_label.get_rect(center=(400, 195)))

                bar_x, bar_y, bar_w, bar_h = 200, 215, 400, 22
                pygame.draw.rect(screen, "gray", (bar_x, bar_y, bar_w, bar_h))
                pygame.draw.rect(screen, "white", (bar_x, bar_y, int(bar_w * sound_effects_vol / 100), bar_h))
                pygame.draw.rect(screen, "white", (bar_x, bar_y, bar_w, bar_h), 2)

                instruct_surf = mini_font.render("<- -> to adjust volume", False, "white")
                screen.blit(instruct_surf, instruct_surf.get_rect(center=(400, 270)))

                back_surf = mini_font.render("ESC to go back to pause menu", False, "white")
                screen.blit(back_surf, back_surf.get_rect(center=(400, 380)))
            else:
                pause_surf = game_font.render("PAUSED", False, "White")
                resume_surf = small_font.render("ESC to Resume", False, "Gray")
                quit_surf = small_font.render("Q to Quit", False, "Gray")
                to_settings_surf = small_font.render("S to Settings", False, "Gray")

                screen.blit(pause_surf, pause_surf.get_rect(center=(400, 160)))
                screen.blit(resume_surf, resume_surf.get_rect(center=(400, 215)))
                screen.blit(quit_surf, quit_surf.get_rect(center=(400, 245)))
                screen.blit(to_settings_surf, to_settings_surf.get_rect(center=(400, 275)))

    # ── Draw Game-Over / Name Entry Screen ────────────────────────────────────
    else:
        screen.fill("black")
        screen.blit(
            game_font.render(f"Race Over! Score: {score}", False, "White"),
            game_font.render(f"Race Over! Score: {score}", False, "White").get_rect(center=(400, 80)),
        )

        if is_entering_name:
            screen.blit(
                small_font.render("Enter your athlete name:", False, "Gray"),
                small_font.render("Enter your athlete name:", False, "Gray").get_rect(center=(400, 180)),
            )
            screen.blit(
                game_font.render(username + "|", False, "White"),
                game_font.render(username + "|", False, "White").get_rect(center=(400, 240)),
            )
            screen.blit(
                mini_font.render("Press ENTER to save", False, "Gray"),
                mini_font.render("Press ENTER to save", False, "Gray").get_rect(center=(400, 310)),
            )
        else:
            scores = load_scores()
            for i, (name, s) in enumerate(scores[:5]):
                screen.blit(
                    small_font.render(f"{i+1}. {name}  {s}", False, "White"),
                    small_font.render(f"{i+1}. {name}  {s}", False, "White").get_rect(
                        center=(400, 170 + i * 36)
                    ),
                )
            screen.blit(
                small_font.render("SPACE to race again", False, "Gray"),
                small_font.render("SPACE to race again", False, "Gray").get_rect(center=(400, 360)),
            )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()