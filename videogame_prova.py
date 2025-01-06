import pygame
import sys
import random
import json
import math
from PIL import Image
import numpy as np
from noise import pnoise2

pygame.init()

def extract_frames_as_ascii(json_path, image_path):
    color_mapping = {
        (0,   0,   0, 255): "X",
        (255, 255, 255, 255): ".",
        (255,   0,   0, 255): "R",
        (  0, 255,   0, 255): "G",
        (  0,   0, 255, 255): "B",
    }
    transparent_char = " "
    default_char = "X"

    with open(json_path, 'r') as f:
        data = json.load(f)
    img = Image.open(image_path).convert("RGBA")
    frames = data["frames"]
    result = {}

    for frame_name, frame_info in frames.items():
        x = frame_info["frame"]["x"]
        y = frame_info["frame"]["y"]
        w = frame_info["frame"]["w"]
        h = frame_info["frame"]["h"]

        cropped = img.crop((x, y, x + w, y + h))
        pixels = cropped.load()

        ascii_rows = []
        for row in range(h):
            row_chars = []
            for col in range(w):
                r, g, b, a = pixels[col, row]
                if a == 0:
                    row_chars.append(transparent_char)
                else:
                    row_chars.append(color_mapping.get((r, g, b, a), default_char))
            ascii_rows.append("".join(row_chars))

        result[frame_name] = ascii_rows
    return result

def extract_frames_rgba(json_path, image_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    img = Image.open(image_path).convert("RGBA")
    frames = data["frames"]
    result = {}

    for frame_name, frame_info in frames.items():
        x = frame_info["frame"]["x"]
        y = frame_info["frame"]["y"]
        w = frame_info["frame"]["w"]
        h = frame_info["frame"]["h"]

        cropped = img.crop((x, y, x + w, y + h))
        pixels = cropped.load()

        rgba_rows = []
        for row in range(h):
            row_cols = []
            for col in range(w):
                r, g, b, a = pixels[col, row]
                row_cols.append((r, g, b, a))
            rgba_rows.append(row_cols)

        result[frame_name] = rgba_rows
    return result

def make_frame_rgba(rgba_rows):
    height = len(rgba_rows)
    width = len(rgba_rows[0]) if height > 0 else 0

    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        for x in range(width):
            r, g, b, a = rgba_rows[y][x]
            surf.set_at((x, y), (r, g, b, a))
    return surf


def pil_image_to_surface(pil_image):
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    return pygame.image.fromstring(data, size, mode)

def mask_get_bounding_rect(mask):
    w, h = mask.get_size()
    min_x, min_y = w, h
    max_x, max_y = -1, -1
    for y in range(h):
        for x in range(w):
            if mask.get_at((x, y)) != 0:
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y
    if max_x < min_x or max_y < min_y:
        return pygame.Rect(0, 0, 0, 0)
    return pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

def show_intro_screen():
    # Load the images
    image1 = pygame.image.load("backgrounds/intro_image0.png")
    image2 = pygame.image.load("backgrounds/intro_image1.png")
    
    # Scale the images to fit the screen size
    image1 = pygame.transform.scale(image1, (WIDTH * SCALE_FACTOR, HEIGHT * SCALE_FACTOR))
    image2 = pygame.transform.scale(image2, (WIDTH * SCALE_FACTOR, HEIGHT * SCALE_FACTOR))
    
    pre_game_music.play(-1)  # Play intro music on loop

    # Variables for image iteration
    show_image1 = True
    clock = pygame.time.Clock()
    iteration_timer = 0
    toggle_interval = 500  # Milliseconds to switch images

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
                pre_game_music.stop()
                print("stop intro music")

        # Alternate between images
        iteration_timer += clock.tick()
        if iteration_timer > toggle_interval:
            iteration_timer = 0
            show_image1 = not show_image1
        
        # Display the current image
        if show_image1:
            DISPLAY.blit(image1, (0, 0))
        else:
            DISPLAY.blit(image2, (0, 0))

        pygame.display.flip()

    return



### SOUNDS INITIALIZATION ###
# Initialize the mixer
pygame.mixer.init()

# Load sounds
sounds = {
    "jump": pygame.mixer.Sound("sounds/jump.wav"),
    "shoot": pygame.mixer.Sound("sounds/laser.wav"),
    "walk": pygame.mixer.Sound("sounds/walk.wav"),
    "sit": pygame.mixer.Sound("sounds/sit.mp3"),

    "player_wins": pygame.mixer.Sound("sounds/player_wins.wav"),
    "player_dies": pygame.mixer.Sound("sounds/player_dies.wav"),
    "game_over": pygame.mixer.Sound("sounds/game_over.wav"),

    "boss_appears": pygame.mixer.Sound("sounds/boss_appears.wav"),
    "boss_dies": pygame.mixer.Sound("sounds/boss_dies.wav"),
    "boss_shoots": pygame.mixer.Sound("sounds/boss_laser.wav"),

    "boss_loses_life": pygame.mixer.Sound("sounds/boss_loses_life.wav"),
    "player_loses_life": pygame.mixer.Sound("sounds/boss_loses_life.wav"),
}


# Background music
pre_game_music = pygame.mixer.Sound("sounds/intro_song.mp3")
spaceships_music = pygame.mixer.Sound("sounds/spaceships_song.mp3")
final_battle_music = pygame.mixer.Sound("sounds/final_battle_song.mp3")

# adjust volume 
pre_game_music.set_volume(0.5)
spaceships_music.set_volume(0.5)
final_battle_music.set_volume(0.5)
sounds['walk'].set_volume(1)
sounds['boss_loses_life'].set_volume(1)
sounds['player_loses_life'].set_volume(1)

## GLOBAL VARIABLES ###
FPS = 60
WIDTH, HEIGHT = 640, 360
SCALE_FACTOR = 2
DISPLAY = pygame.display.set_mode((WIDTH * SCALE_FACTOR, HEIGHT * SCALE_FACTOR))
pygame.display.set_caption("Cyberpunk Mars")
CLOCK = pygame.time.Clock()

PLAYER_SPEED = 2.2
BOSS_SPEED   = 0.6
BOSS_SPEED_ENTER = 2.0
INV_TIME = 3 * FPS

BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
RED    = (255, 0, 0)

is_walking_sound_playing = False

def draw_pixel_art(surface, pixel_map, color=WHITE):
    for y, row in enumerate(pixel_map):
        for x, ch in enumerate(row):
            if ch == 'X':
                surface.set_at((x, y), color)

def scale_surf(surf, factor=SCALE_FACTOR):
    w = surf.get_width()  * factor
    h = surf.get_height() * factor
    return pygame.transform.scale(surf, (w, h))


# -----------------------------------------------------------------------------------
# LOAD PLAYER
# -----------------------------------------------------------------------------------
json_path = "Hyper main character/Hyper main character.json"
image_path = "Hyper main character/Hyper main character.png"

frames_ascii = extract_frames_as_ascii(json_path, image_path)
frames_rgba  = extract_frames_rgba(json_path, image_path)

rgba_rows_0 = frames_rgba["Hyper main character0.png"]
pl_idleL_1  = make_frame_rgba(rgba_rows_0)

rgba_rows_1 = frames_rgba["Hyper main character1.png"]
pl_idleL_2  = make_frame_rgba(rgba_rows_1)

pl_runL_1   = pl_idleL_1
rgba_rows_3 = frames_rgba["Hyper main character3.png"]
pl_runL_2   = make_frame_rgba(rgba_rows_3)

rgba_rows_5 = frames_rgba["Hyper main character5.png"]
pl_jumpL    = make_frame_rgba(rgba_rows_5)

rgba_rows_2 = frames_rgba["Hyper main character2.png"]
pl_downL    = make_frame_rgba(rgba_rows_2)

PL_IDLE_R_FRAMES = [scale_surf(pl_idleL_1, factor=1),
                    scale_surf(pl_idleL_2, factor=1)]
PL_RUN_R_FRAMES  = [scale_surf(pl_runL_1, factor=1),
                    scale_surf(pl_runL_2, factor=1)]
PL_JUMP_R_FRAMES = [scale_surf(pl_jumpL, factor=1)]
PL_DOWN_R_FRAMES = [scale_surf(pl_downL, factor=1)]

PL_IDLE_L_FRAMES = [pygame.transform.flip(f, True, False) for f in PL_IDLE_R_FRAMES]
PL_RUN_L_FRAMES  = [pygame.transform.flip(f, True, False) for f in PL_RUN_R_FRAMES]
PL_JUMP_L_FRAMES = [pygame.transform.flip(f, True, False) for f in PL_JUMP_R_FRAMES]
PL_DOWN_L_FRAMES = [pygame.transform.flip(f, True, False) for f in PL_DOWN_R_FRAMES]

PL_IDLE_R_MASKS = [pygame.mask.from_surface(f) for f in PL_IDLE_R_FRAMES]
PL_IDLE_L_MASKS = [pygame.mask.from_surface(f) for f in PL_IDLE_L_FRAMES]
PL_RUN_R_MASKS  = [pygame.mask.from_surface(f) for f in PL_RUN_R_FRAMES]
PL_RUN_L_MASKS  = [pygame.mask.from_surface(f) for f in PL_RUN_L_FRAMES]
PL_JUMP_R_MASKS = [pygame.mask.from_surface(f) for f in PL_JUMP_R_FRAMES]
PL_JUMP_L_MASKS = [pygame.mask.from_surface(f) for f in PL_JUMP_L_FRAMES]
PL_DOWN_R_MASKS = [pygame.mask.from_surface(f) for f in PL_DOWN_R_FRAMES]
PL_DOWN_L_MASKS = [pygame.mask.from_surface(f) for f in PL_DOWN_L_FRAMES]

# -----------------------------------------------------------------------------------
# LOAD SPACESHIP
# -----------------------------------------------------------------------------------
ship_pixels = [
    "       XXXX        ",
    "    XXX    XXX     ",
    "  XXX  XX XX  XXX  ",
    " XXXX  XX XX  XXXX ",
    "XXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXX",
    " XXXX  XX XX  XXXX ",
    "   XXX       XXX   ",
    "     XXX   XXX     "
]
ship_surf = pygame.Surface((len(ship_pixels[0]), len(ship_pixels)), pygame.SRCALPHA)
draw_pixel_art(ship_surf, ship_pixels, RED)
SHIP_IMG = scale_surf(ship_surf, factor=2)

# -----------------------------------------------------------------------------------
# LOAD BOSS
# -----------------------------------------------------------------------------------
json_path = "enemy hyper/enemy hyper.json"
image_path = "enemy hyper/enemy hyper.png"

frames_ascii_boss = extract_frames_as_ascii(json_path, image_path)
frames_rgba_boss  = extract_frames_rgba(json_path, image_path)

rgba_rows_boss0 = frames_rgba_boss["enemy hyper0.png"]
boss_surf_0 = make_frame_rgba(rgba_rows_boss0)

rgba_rows_boss1 = frames_rgba_boss["enemy hyper1.png"]
boss_surf_1 = make_frame_rgba(rgba_rows_boss1)

BOSS_IMG_0 = scale_surf(boss_surf_0, factor=1)
BOSS_IMG_1 = scale_surf(boss_surf_1, factor=1)

BOSS_IDLE_R_FRAMES = [BOSS_IMG_0, BOSS_IMG_1]
BOSS_IDLE_L_FRAMES = [pygame.transform.flip(f, True, False) for f in BOSS_IDLE_R_FRAMES]

# -----------------------------------------------------------------------------------
# BOSS LASER
# -----------------------------------------------------------------------------------
boss_laser_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
pygame.draw.rect(boss_laser_surf, RED, (0, 0, 3, 3))
BOSS_LASER_IMG = scale_surf(boss_laser_surf, factor=2)
BOSS_LASER_MASK = pygame.mask.from_surface(BOSS_LASER_IMG)

# -----------------------------------------------------------------------------------
# PLAYER LASER
# -----------------------------------------------------------------------------------
player_laser_surf = pygame.Surface((2, 2), pygame.SRCALPHA)
pygame.draw.rect(player_laser_surf, WHITE, (0, 0, 2, 2))
PLAYER_LASER_IMG = scale_surf(player_laser_surf)

# -----------------------------------------------------------------------------------
# LIVES ICON
# -----------------------------------------------------------------------------------
life_pixel_map = [
    "  XXX  ",
    " X   X ",
    "X     X",
    "X  X  X",
    "X     X",
    " X   X ",
    "  XXX  "
]
life_surf = pygame.Surface((len(life_pixel_map[0]), len(life_pixel_map)), pygame.SRCALPHA)
draw_pixel_art(life_surf, life_pixel_map, color=WHITE)
LIFE_IMG = scale_surf(life_surf, factor=2)

life_surf_boss = pygame.Surface((len(life_pixel_map[0]), len(life_pixel_map)), pygame.SRCALPHA)
draw_pixel_art(life_surf_boss, life_pixel_map, color=RED)
LIFE_IMG_BOSS = scale_surf(life_surf_boss, factor=2)


# -----------------------------------------------------------------------------------
# SCENE / BACKGROUND
# -----------------------------------------------------------------------------------
WORLD_WIDTH = 2000
GROUND_LEVEL = HEIGHT - 24

green_colors = [
    (154, 186, 181),
    (69, 100, 95),
    (22, 46, 42),
    (14, 24, 23)
]

sky_texture = Image.open('backgrounds/sky_buildings.png')
sky_texture_surface = pil_image_to_surface(sky_texture)

bg_layer_image = Image.open('backgrounds/buildings.png')
bg_layer_mid = pil_image_to_surface(bg_layer_image)

ground_colors = [
    (105, 105, 105),
    (193, 68, 14),
    (139, 69, 19),
    (160, 82, 45)
]
ground_texture = Image.open('backgrounds/ground.png')
ground_texture_surface = pil_image_to_surface(ground_texture)

def draw_ground(surface, camera_x):
    ground_y = GROUND_LEVEL
    offset_x = -camera_x % ground_texture_surface.get_width()
    for x in range(-1, (surface.get_width() // ground_texture_surface.get_width()) + 2):
        surface.blit(ground_texture_surface, (offset_x + x * ground_texture_surface.get_width(), ground_y))


# -----------------------------------------------------------------------------------
# MAIN GAME
# -----------------------------------------------------------------------------------
def main():
    global is_walking_sound_playing  # Use the global variable for walking sound
    # Show the intro screen
    show_intro_screen()

    # Optionally start playing the spaceship song once the intro ends
    spaceships_music.play(-1)  # loop = -1
    print("spaceships_music")
    player_x = 50
    player_y = GROUND_LEVEL - PL_IDLE_L_FRAMES[0].get_height()
    facing_right = True
    on_ground = True
    player_vy = 0
    jump_power = 5
    player_state = "idle"
    prev_player_state = "idle" 

    anim_timer = 0
    anim_index = 0
    boss_anim_index = 0
    boss_anim_timer = 0

    lives = 5
    invincible = False
    inv_timer = 0

    boss_active = False
    boss_hp = 10
    boss_x = WORLD_WIDTH + 100
    boss_y = GROUND_LEVEL - BOSS_IDLE_R_FRAMES[0].get_height()
    boss_laser_timer = 0
    boss_invincible = False
    boss_inv_timer = 0
    BOSS_INV_TIME = 60

    # Once boss is triggered, we do an entrance
    boss_enter_done = False
    # Then countdown
    boss_fight_begun = False
    countdown_timer = 0
    # We freeze the camera once fight begins
    freeze_camera = False
    locked_camera_x = 0
    # If the player was jumping when the boss is triggered, we let them land
    # Then freeze everything
    player_landed_for_cutscene = False

    lasers = []
    enemy_lasers = []
    ships = []
    SHIP_SPAWN_INTERVAL = 180
    ship_timer = SHIP_SPAWN_INTERVAL
    STOP_SPAWN_X = WORLD_WIDTH - 600

    for _ in range(3):
        sx = random.randint(WIDTH, WIDTH + 400)
        sy = random.randint(10, 100)
        ships.append({"x": sx, "y": sy})

    camera_x = 0
    font_large = pygame.font.Font(None, 64)
    font_big   = pygame.font.Font(None, 22)

    boss_aim_at_head = True

    final_battle_music_playing = False  
    boss_appears_playing= False
    boss_appears_stopped= False
    spaceships_music_stop = False

    # Start the game
    running = True
    while running:
        dt = CLOCK.tick(FPS)
        keys = pygame.key.get_pressed()

        # normal logic
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.KEYDOWN:
                if not boss_active:
                    # normal input
                    if event.key == pygame.K_UP:
                        if on_ground and player_state!='down':
                            sounds["jump"].play()
                            print("jump")
                            player_vy = -jump_power
                            on_ground = False
                            player_state = "jump"
                    elif event.key == pygame.K_SPACE:
                        sounds["shoot"].play()
                        print("shoot")
                        direction = 1 if facing_right else -1
                        lx = player_x + (PL_IDLE_L_FRAMES[0].get_width() // 2)
                        ly = player_y + (PL_IDLE_L_FRAMES[0].get_height() // 2)
                        lasers.append([lx, ly, direction, "player"])
                    elif event.key == pygame.K_DOWN:
                        if on_ground and player_state!='down':
                            if prev_player_state != "down":
                                sounds["sit"].play()
                                print("sit")
                            player_state = "down"
                            
                else:
                    # Boss triggered
                    # If we haven't begun the fight, we freeze all new input
                    # EXCEPT we let the player finish falling if they're in mid-air
                    if boss_fight_begun:

                        if not boss_appears_stopped:
                            sounds['boss_appears'].stop()
                            print("stop boss appears")
                            boss_appears_stopped = True
                        if not final_battle_music_playing:
                            final_battle_music.play(-1)
                            print("final_battle_music")
                            final_battle_music_playing = True  

                        # fight started => normal input
                        if event.key == pygame.K_UP:
                            if on_ground and player_state!='down':
                                player_vy = -jump_power
                                on_ground = False
                                player_state = "jump"
                                sounds["jump"].play()
                                print("jump")
                        elif event.key == pygame.K_SPACE:
                            direction = 1 if facing_right else -1
                            lx = player_x + (PL_IDLE_L_FRAMES[0].get_width() // 2)
                            ly = player_y + (PL_IDLE_L_FRAMES[0].get_height() // 2)
                            lasers.append([lx, ly, direction, "player"])
                            sounds["shoot"].play()
                            print("shoot")
                        elif event.key == pygame.K_DOWN:
                            if on_ground and player_state!='down':
                                player_state = "down"
                                sounds["sit"].play()
                                print("sit")
                    else:
                        # freeze: no new moves

                        pass

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    if player_state == "down":
                        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                            player_state = "run"
                            # Handle walking sound

                            if not is_walking_sound_playing:  # Only play if not already playing
                                sounds["walk"].play(-1)  # Loop the walking sound
                                print("walk")
                                is_walking_sound_playing = True

                            if is_walking_sound_playing:  # Only stop if the sound is playing
                                sounds["walk"].stop()  # Stop the walking sound
                                print("stop walk")
                                is_walking_sound_playing = False

                        else:
                            player_state = "idle"
        # store old state for next loop
        prev_player_state = player_state
        # ------------------------------------------------------------------------------
        # If boss not active, normal movement
        # ------------------------------------------------------------------------------
        if not boss_active:
            moving = False
            if keys[pygame.K_LEFT]:
                player_x -= PLAYER_SPEED
                facing_right = False
                moving = True
                if on_ground and player_state != "down":
                    player_state = "run"
            elif keys[pygame.K_RIGHT]:
                player_x += PLAYER_SPEED
                facing_right = True
                moving = True
                if on_ground and player_state != "down":
                    player_state = "run"
            
            # Handle walking sound
            if moving and on_ground:
                if not is_walking_sound_playing:
                    sounds["walk"].play(-1)  # Loop the walking sound
                    is_walking_sound_playing = True
                    print("walk")
            else:
                if is_walking_sound_playing:
                    sounds["walk"].stop()  # Stop the walking sound
                    is_walking_sound_playing = False
                    print("stop walk")


            if not moving and on_ground and player_state not in ("down", "jump"):
                player_state = "idle"

            if not on_ground:
                # gravity
                player_vy += 0.2
                player_y += player_vy
                if player_y >= GROUND_LEVEL - PL_IDLE_L_FRAMES[0].get_height():
                    player_y = GROUND_LEVEL - PL_IDLE_L_FRAMES[0].get_height()
                    player_vy = 0
                    on_ground = True
                    if player_state != "down":
                        player_state = "idle"

            if player_x < 0:
                player_x = 0
            if player_x > WORLD_WIDTH - 20:
                player_x = WORLD_WIDTH - 20

            # spawn ships
            if player_x < STOP_SPAWN_X:
                ship_timer += 1
                if ship_timer > SHIP_SPAWN_INTERVAL:
                    ship_timer = 0
                    sx = random.randint(int(player_x + WIDTH), int(player_x + WIDTH + 400))
                    sy = random.randint(20, 100)
                    ships.append({"x": sx, "y": sy})

            for s in ships:
                s["x"] -= 1
            ships = [s for s in ships if s["x"] > -200]

            for s in ships:
                if random.random() < 0.01:
                    ex = s["x"] + SHIP_IMG.get_width()//2
                    ey = s["y"] + SHIP_IMG.get_height()
                    enemy_lasers.append([ex, ey, 3, "ship"])

            for l in lasers:
                if l[3] == "player":
                    l[0] += 5 * l[2]
            lasers = [l for l in lasers if -100 < l[0] < WORLD_WIDTH+100]

            # move enemy lasers
            to_remove = []
            for el in enemy_lasers:
                if el[3] == "ship":
                    el[1] += 3
                if (el[0]<-100 or el[0]>WORLD_WIDTH+100 or
                    el[1]<-50  or el[1]>HEIGHT+50):
                    to_remove.append(el)
            for x_ in to_remove:
                if x_ in enemy_lasers:
                    enemy_lasers.remove(x_)

            # Activate boss
            if player_x > WORLD_WIDTH - 600:
                boss_active = True
                player_state = "idle"
                anim_index = 0

        else:
            # ------------------------------------------------------------------------------
            # BOSS Active
            # ------------------------------------------------------------------------------
            # 1) The boss enters from the right
            if not boss_enter_done:
                # play boss_appears_countdown if not already playing
                if not spaceships_music_stop:
                    spaceships_music.stop()
                    print("spaceships_music stop")
                    spaceships_music_stop = True

                if not boss_appears_playing:
                    sounds['boss_appears'].play() # loop during entrance + countdown
                    print("boss_appears")
                    boss_appears_playing = True
                # Keep letting the player finish their jump if mid-air:
                if not on_ground:
                    player_vy += 0.2
                    player_y += player_vy
                    if player_y >= GROUND_LEVEL - PL_IDLE_L_FRAMES[0].get_height():
                        player_y = GROUND_LEVEL - PL_IDLE_L_FRAMES[0].get_height()
                        player_vy = 0
                        on_ground = True
                        player_state = "idle"

                # if on_ground => we can say the player has now landed
                if on_ground:
                    player_landed_for_cutscene = True

                if is_walking_sound_playing:
                    sounds["walk"].stop()
                    print("stop walk")
                    is_walking_sound_playing = False

                # The boss moves in from the right
                if boss_x > WORLD_WIDTH - 300:
                    boss_x -= BOSS_SPEED_ENTER
                else:
                    boss_x = WORLD_WIDTH - 300
                    boss_enter_done = True

            # 2) Once the boss has “entered,” we freeze everything if we have also landed
            elif not boss_fight_begun:
                # At this point, the boss is at final x. We want to do a countdown.
                # We only start the countdown if the player has landed
                if not player_landed_for_cutscene:
                    # still mid-air => apply gravity until they land
                    if not on_ground:
                        player_vy += 0.2
                        player_y += player_vy
                        if player_y >= GROUND_LEVEL - PL_IDLE_L_FRAMES[0].get_height():
                            player_y = GROUND_LEVEL - PL_IDLE_L_FRAMES[0].get_height()
                            player_vy = 0
                            on_ground = True
                            player_state = "idle"

                    else:
                        # once on_ground, set landed_for_cutscene = True
                        player_landed_for_cutscene = True

                # If we have landed, we do the countdown
                if player_landed_for_cutscene:
                    if countdown_timer < 4*FPS:
                        countdown_timer += 1
                        # freeze everything: no boss follow, no movement
                        # so do NOT do boss_x +/- BOSS_SPEED, do not do player movement
                    else:
                        # fight starts
                        boss_fight_begun = True
                        freeze_camera = True
                        locked_camera_x = camera_x

            else:
                # 3) Boss fight begun => normal movement
                moving = False
                if keys[pygame.K_LEFT]:
                    player_x -= PLAYER_SPEED
                    facing_right = False
                    moving = True
                    if on_ground and player_state != "down":
                        player_state = "run"
                    # Handle walking sound
                    if moving and on_ground:  # Player is walking
                        if not is_walking_sound_playing:  # Only play if not already playing
                            sounds["walk"].play(-1)  # Loop the walking sound
                            print("walk")
                            is_walking_sound_playing = True
                    else:  # Player is not walking
                        if is_walking_sound_playing:  # Only stop if the sound is playing
                            sounds["walk"].stop()  # Stop the walking sound
                            print("walk")
                            is_walking_sound_playing = False

                elif keys[pygame.K_RIGHT]:
                    player_x += PLAYER_SPEED
                    facing_right = True
                    moving = True
                    if on_ground and player_state != "down":
                        player_state = "run"
                    # Handle walking sound

                    if moving and on_ground:  # Player is walking
                        if not is_walking_sound_playing:  # Only play if not already playing
                            sounds["walk"].play(-1)  # Loop the walking sound
                            print("walk")
                            is_walking_sound_playing = True
                    else:  # Player is not walking
                        if is_walking_sound_playing:  # Only stop if the sound is playing
                            sounds["walk"].stop()  # Stop the walking sound
                            print("walk")
                            is_walking_sound_playing = False


                if not moving and on_ground and player_state not in ("down","jump"):
                    player_state = "idle"

                if not on_ground:
                    player_vy += 0.2
                    player_y += player_vy
                    if player_y >= GROUND_LEVEL - PL_IDLE_L_FRAMES[0].get_height():
                        player_y = GROUND_LEVEL - PL_IDLE_L_FRAMES[0].get_height()
                        player_vy = 0
                        on_ground = True
                        if player_state != "down":
                            player_state = "idle"

                # The boss now follows horizontally
                if player_x > boss_x:
                    boss_x += BOSS_SPEED
                elif player_x < boss_x:
                    boss_x -= BOSS_SPEED

                if player_x < 0:
                    player_x = 0
                if player_x > WORLD_WIDTH - 20:
                    player_x = WORLD_WIDTH - 20
                
                left_bound = camera_x
                right_bound_alien = camera_x + WIDTH - PL_IDLE_L_FRAMES[0].get_width()
                if player_x < left_bound:
                    player_x = left_bound
                if player_x > right_bound_alien:
                    player_x = right_bound_alien

                right_bound_boss = camera_x + WIDTH - BOSS_IDLE_R_FRAMES[0].get_width()
                if boss_x < camera_x:
                    boss_x = camera_x
                if boss_x > right_bound_boss:
                    boss_x = right_bound_boss




            # Move player's lasers
            for l in lasers:
                if l[3] == "player":
                    l[0] += 5 * l[2]
            lasers = [l for l in lasers if -100 < l[0] < WORLD_WIDTH+100]

            # Move enemy lasers
            to_remove = []
            for el in enemy_lasers:
                if len(el) == 5 and el[4] == "boss":
                    el[0] += el[2]
                    el[1] += el[3]
                elif len(el) == 4 and el[3] == "ship":
                    el[1] += 3

                if (el[0]<-100 or el[0]>WORLD_WIDTH+100 or
                    el[1]<-50  or el[1]>HEIGHT+50):
                    to_remove.append(el)
            for x_ in to_remove:
                if x_ in enemy_lasers:
                    enemy_lasers.remove(x_)

        # CAMERA
        if freeze_camera:
            camera_x = locked_camera_x
        else:
            camera_x = player_x - (WIDTH // 6)
            if camera_x < 0:
                camera_x = 0
            if camera_x > WORLD_WIDTH - WIDTH:
                camera_x = WORLD_WIDTH - WIDTH

        # ANIMATION
        anim_timer += 1
        if player_state == "idle":
            if anim_timer > 20:
                anim_timer = 0
                anim_index = (anim_index + 1) % 2
        elif player_state == "run":
            if anim_timer > 10:
                anim_timer = 0
                anim_index = (anim_index + 1) % 2
        elif player_state == "down":
            anim_index = 0
        else:
            anim_index = 0

        boss_anim_timer += 1
        if boss_anim_timer > 20:
            boss_anim_timer = 0
            boss_anim_index = (boss_anim_index + 1) % 2

        # Determine current frame
        if player_state == "idle":
            frame_img = PL_IDLE_R_FRAMES[anim_index] if facing_right else PL_IDLE_L_FRAMES[anim_index]
            frame_mask = PL_IDLE_R_MASKS[anim_index] if facing_right else PL_IDLE_L_MASKS[anim_index]
        elif player_state == "run":
            frame_img = PL_RUN_R_FRAMES[anim_index] if facing_right else PL_RUN_L_FRAMES[anim_index]
            frame_mask = PL_RUN_R_MASKS[anim_index] if facing_right else PL_RUN_L_MASKS[anim_index]
        elif player_state == "down":
            frame_img = PL_DOWN_R_FRAMES[0] if facing_right else PL_DOWN_L_FRAMES[0]
            frame_mask = PL_DOWN_R_MASKS[0] if facing_right else PL_DOWN_L_MASKS[0]
        else:  # jump
            frame_img = PL_JUMP_R_FRAMES[0] if facing_right else PL_JUMP_L_FRAMES[0]
            frame_mask = PL_JUMP_R_MASKS[0] if facing_right else PL_JUMP_L_MASKS[0]

        player_rect = frame_img.get_rect(topleft=(player_x, player_y))

        # BOSS SHOOT
        if boss_active and boss_fight_begun:
            boss_laser_timer += 1
            if boss_laser_timer > 70:
                boss_laser_timer = 0
                ex = boss_x + BOSS_IDLE_R_FRAMES[0].get_width() // 2
                ey = boss_y + BOSS_IDLE_R_FRAMES[0].get_height() // 5

                clip_rect = mask_get_bounding_rect(frame_mask)
                player_top = player_y + clip_rect.top
                player_bottom = player_top + clip_rect.height
                player_center_x = player_x + clip_rect.left + (clip_rect.width // 2)

                if boss_aim_at_head:
                    target_x = player_center_x
                    target_y = player_top
                    boss_aim_at_head = False
                else:
                    target_x = player_center_x
                    target_y = player_bottom
                    boss_aim_at_head = True

                dx = target_x - ex
                dy = target_y - ey
                dist = math.sqrt(dx*dx + dy*dy)
                if dist != 0:
                    dx /= dist
                    dy /= dist
                speed = 4
                vx = dx * speed
                vy = dy * speed

                enemy_lasers.append([ex, ey, vx, vy, "boss"])
                # Play the boss shooting sound
                sounds['boss_shoots'].play()
                print('boss_shoots')

        # COLLISIONS (player vs lasers)
        for el in enemy_lasers:
            el_rect = None
            if len(el) == 5 and el[4] == "boss":
                el_rect = BOSS_LASER_IMG.get_rect(topleft=(el[0], el[1]))
            elif len(el) == 4 and el[3] == "ship":
                el_rect = pygame.Rect(el[0], el[1], 2*SCALE_FACTOR, 2*SCALE_FACTOR)

            if el_rect and player_rect.colliderect(el_rect):
                overlap = False
                if len(el) == 5 and el[4] == "boss":
                    offset_x = el_rect.x - player_rect.x
                    offset_y = el_rect.y - player_rect.y
                    overlap = frame_mask.overlap(BOSS_LASER_MASK, (offset_x, offset_y))
                else:
                    overlap = True
                if overlap:
                    if not invincible:
                        lives -= 1
                        sounds['player_loses_life'].play()
                        if lives <= 0:
                            running = False
                            player_dying = True
                            sounds['player_dies'].play()
                            final_battle_music.stop()
                            print("player_dies")
                            pygame.time.wait(2000) 

                        else:
                            invincible = True
                            inv_timer = 0
                    if el in enemy_lasers:
                        enemy_lasers.remove(el)
                    break

        # Collisions (player lasers vs boss)
        if boss_active:
            # Decide boss facing
            if player_x > boss_x:
                boss_facing_right = True
            else:
                boss_facing_right = False

            if boss_facing_right:
                boss_img = BOSS_IDLE_L_FRAMES[boss_anim_index]
            else:
                boss_img = BOSS_IDLE_R_FRAMES[boss_anim_index]

            boss_rect = boss_img.get_rect(topleft=(boss_x, boss_y))
            for l in lasers:
                if l[3] == "player":
                    l_rect = PLAYER_LASER_IMG.get_rect(topleft=(l[0], l[1]))
                    if l_rect.colliderect(boss_rect) and not boss_invincible:
                        boss_hp -= 1
                        sounds["boss_loses_life"].play()
                        lasers.remove(l)
                        boss_invincible = True
                        boss_inv_timer  = 0
                        break

            if boss_hp <= 0:
                boss_dying = True
                sounds['boss_dies'].play()
                final_battle_music.stop()
                print("boss_dies")
                running = False
                pygame.time.wait(2000) 

        if invincible:
            inv_timer += 1
            if inv_timer > INV_TIME:
                invincible = False

        if boss_invincible:
            boss_inv_timer += 1
            if boss_inv_timer > BOSS_INV_TIME:
                boss_invincible = False

        # -----------------------------------------------------------------------------------
        # DRAW
        # -----------------------------------------------------------------------------------
        world_surf = pygame.Surface((WIDTH, HEIGHT))
        offset_far = camera_x * 0.3
        world_surf.blit(sky_texture_surface, (-offset_far, 0))

        offset_mid = camera_x * 0.6
        world_surf.blit(bg_layer_mid, (-offset_mid, 0))

        draw_ground(world_surf, camera_x)

        for s in ships:
            sx = s["x"] - camera_x
            sy = s["y"]
            if -50 < sx < WIDTH + 50:
                world_surf.blit(SHIP_IMG, (sx, sy))

        for el in enemy_lasers:
            if len(el) == 5 and el[4] == "boss":
                rx = el[0] - camera_x
                ry = el[1]
                world_surf.blit(BOSS_LASER_IMG, (rx, ry))
            elif len(el) == 4 and el[3] == "ship":
                rx = el[0] - camera_x
                ry = el[1]
                color_surf = pygame.Surface((2,2), pygame.SRCALPHA)
                pygame.draw.rect(color_surf, RED, (0,0,2,2))
                tmp = scale_surf(color_surf, factor=2)
                world_surf.blit(tmp, (rx, ry))

        if boss_active:
            bx = boss_x - camera_x
            by = boss_y
            draw_boss = True
            if boss_invincible:
                if (pygame.time.get_ticks() // 100) % 2 == 0:
                    draw_boss = False
            if -100 < bx < WIDTH + 100 and draw_boss:
                world_surf.blit(boss_img, (bx, by))

        draw_player = True
        if invincible:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                draw_player = False
        if draw_player:
            px = player_x - camera_x
            py = player_y
            world_surf.blit(frame_img, (px, py))

        for l in lasers:
            if l[3] == "player":
                lx = l[0] - camera_x
                ly = l[1]
                world_surf.blit(PLAYER_LASER_IMG, (lx, ly))

        for i in range(lives):
            offset_x = 5 + (LIFE_IMG.get_width() + 2)*i
            world_surf.blit(LIFE_IMG, (offset_x, 5))

        if boss_active:
            for i in range(boss_hp):
                x_off = 480 + (LIFE_IMG_BOSS.get_width()+2)*i
                y_off = LIFE_IMG_BOSS.get_height() - 10
                world_surf.blit(LIFE_IMG_BOSS, (x_off, y_off))

        # Draw countdown only after boss_enter_done and not boss_fight_begun
        if boss_active and boss_enter_done and not boss_fight_begun:
            sec = countdown_timer // FPS
            if   sec == 0: text = "3..."
            elif sec == 1: text = "2..."
            elif sec == 2: text = "1..."
            else:          text = "FIGHT!"
            txt_surf = font_large.render(text, True, WHITE)
            cx = (WIDTH - txt_surf.get_width())//2
            cy = (HEIGHT - txt_surf.get_height())//2
            world_surf.blit(txt_surf, (cx, cy))

        scaled_world = pygame.transform.scale(world_surf, (WIDTH*SCALE_FACTOR, HEIGHT*SCALE_FACTOR))
        DISPLAY.blit(scaled_world, (0, 0))
        pygame.display.flip()

    DISPLAY.fill(BLACK)
    font_big = pygame.font.SysFont("Arial", 16, bold=True)
    if boss_hp <= 0:
        msg = "YOU WON!"
        sounds['player_wins'].play()
        print("player_wins")
    else:
        msg = "GAME OVER"
        sounds['game_over'].play()
        print("game_over")
    msg_surf = font_big.render(msg, True, WHITE)
    DISPLAY.blit(msg_surf, ((WIDTH*SCALE_FACTOR)//2 - msg_surf.get_width()//2,
                            (HEIGHT*SCALE_FACTOR)//2 - msg_surf.get_height()//2))
    
    # Stop walking sound before exiting
    if is_walking_sound_playing:
        sounds["walk"].stop()
        is_walking_sound_playing = False

    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
