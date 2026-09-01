import pygame
import random
import sys
import numpy as np

# Pygame & Mixer initialiseren
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

# Resolutie van het originele pixel-art canvas
GAME_WIDTH, GAME_HEIGHT = 420, 240
SCREEN_WIDTH, SCREEN_HEIGHT = 840, 480

LOWER_ZONE_TOP = int(GAME_HEIGHT * 0.75)
GUIDE_BAR_TOP = int(GAME_HEIGHT * 0.88)

game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("8-Bit Pretpark Arcade - Sound & Controls")

clock = pygame.time.Clock()

# --- 8-BIT GELUIDSGENERATOR (Geen externe .wav bestanden nodig) ---
def generate_8bit_sound(freq_start, freq_end, duration, wave_type="square"):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    freqs = np.linspace(freq_start, freq_end, n_samples)
    
    if wave_type == "square":
        waveform = np.sign(np.sin(2 * np.pi * freqs * t))
    else:  # noise / miss
        waveform = np.random.uniform(-1, 1, n_samples)
        
    audio = (waveform * 32767 * 0.25).astype(np.int16)
    return pygame.sndarray.make_sound(audio)

# Geluiden aanmaken
snd_shoot = generate_8bit_sound(800, 200, 0.1, "square")
snd_hit = generate_8bit_sound(400, 1000, 0.15, "square")
snd_miss = generate_8bit_sound(150, 50, 0.08, "noise")

# Achtergrondafbeelding laden
try:
    bg_image = pygame.image.load("background.png").convert()
    bg_image = pygame.transform.scale(bg_image, (GAME_WIDTH, GAME_HEIGHT))
except pygame.error:
    print("Fout: 'background.png' niet gevonden. Plaats de afbeelding in dezelfde map!")
    sys.exit()

# Kleuren
WHITE = (255, 255, 255)
RED = (230, 30, 30)
BLACK = (0, 0, 0)
GREEN = (30, 200, 30)
PURPLE = (160, 50, 200)
YELLOW = (255, 230, 0)
CYAN = (0, 255, 255)
DARK_GRAY = (20, 20, 20)

scroll_y = 0
scroll_speed = 1.0

# 5 Personages
characters = [
    {"name": "M@lb",    "x": 30,  "y": LOWER_ZONE_TOP + 2, "speed_x": 0.8, "speed_y": 0.2, "dir_x": 1,  "dir_y": 1,  "score": 0, "hair": (120, 60, 20),  "shirt": (40, 120, 220), "pants": (20, 40, 100)},
    {"name": "GDJ",     "x": 100, "y": LOWER_ZONE_TOP + 8, "speed_x": 1.1, "speed_y": 0.3, "dir_x": -1, "dir_y": -1, "score": 0, "hair": (200, 140, 60), "shirt": (220, 50, 80),  "pants": (220, 50, 80)},
    {"name": "SHAUG",   "x": 180, "y": LOWER_ZONE_TOP + 5, "speed_x": 0.7, "speed_y": 0.2, "dir_x": 1,  "dir_y": 1,  "score": 0, "hair": (40, 40, 40),   "shirt": (30, 200, 160), "pants": (30, 30, 30)},
    {"name": "BambiFF", "x": 260, "y": LOWER_ZONE_TOP + 12,"speed_x": 0.9, "speed_y": 0.3, "dir_x": -1, "dir_y": -1, "score": 0, "hair": (160, 80, 40),  "shirt": (240, 140, 40), "pants": (50, 50, 50)},
    {"name": "Phertron","x": 340, "y": LOWER_ZONE_TOP + 4, "speed_x": 1.0, "speed_y": 0.2, "dir_x": 1,  "dir_y": 1,  "score": 0, "hair": (230, 200, 100),"shirt": (180, 50, 200), "pants": (20, 20, 20)},
]

active_shooter_idx = 0
shot_lines = []
clowns = []
total_hits = 0

font = pygame.font.SysFont("monospace", 10, bold=True)
guide_font = pygame.font.SysFont("monospace", 8, bold=True)

def spawn_clown():
    clowns.append({
        "x": random.randint(30, GAME_WIDTH - 40),
        "y": -20
    })

def perform_shot(shooter_indices, target_pos):
    global total_hits
    hit_registered = False

    # Geluid afspelen voor het afvuren
    snd_shoot.play()

    for idx in shooter_indices:
        shooter = characters[idx]
        start_pos = (int(shooter["x"]) + 4, int(shooter["y"]) + 4)
        shot_lines.append([start_pos, target_pos, 3])

    # Check of een clown geraakt is
    for clown in clowns[:]:
        clown_rect = pygame.Rect(clown["x"] - 4, clown["y"] - 4, 20, 24)
        if clown_rect.collidepoint(target_pos):
            clowns.remove(clown)
            characters[active_shooter_idx]["score"] += 10
            total_hits += 1
            hit_registered = True
            snd_hit.play()  # Hit geluid
            break

    # Geen clown geraakt
    if not hit_registered:
        snd_miss.play()  # Miss geluid

# Game loop
running = True
while running:
    level = total_hits // 10
    clown_base_speed = 0.4 + (level * 0.15)
    max_clowns = min(1 + level, 5)

    # 1. Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            # Selectie 1 t/m 5
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                active_shooter_idx = event.key - pygame.K_1
            
            # 'B' Toets: Enkelvoudig schot van de actieve schutter
            elif event.key == pygame.K_b:
                mx, my = pygame.mouse.get_pos()
                gx = int(mx * (GAME_WIDTH / SCREEN_WIDTH))
                gy = int(my * (GAME_HEIGHT / SCREEN_HEIGHT))
                perform_shot([active_shooter_idx], (gx, gy))

            # 'A' Toets: Teamaanval van alle 5 personages
            elif event.key == pygame.K_a:
                mx, my = pygame.mouse.get_pos()
                gx = int(mx * (GAME_WIDTH / SCREEN_WIDTH))
                gy = int(my * (GAME_HEIGHT / SCREEN_HEIGHT))
                perform_shot([0, 1, 2, 3, 4], (gx, gy))

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            gx = int(mx * (GAME_WIDTH / SCREEN_WIDTH))
            gy = int(my * (GAME_HEIGHT / SCREEN_HEIGHT))
            
            # Selecteer personage via muisklik
            hit_character = False
            for idx, char in enumerate(characters):
                char_rect = pygame.Rect(char["x"] - 2, char["y"] - 2, 12, 18)
                if char_rect.collidepoint(gx, gy):
                    active_shooter_idx = idx
                    hit_character = True
                    break
            
            if not hit_character:
                perform_shot([active_shooter_idx], (gx, gy))

    # 2. Logic updates
    scroll_y = (scroll_y + scroll_speed) % GAME_HEIGHT

    for char in characters:
        char["x"] += char["speed_x"] * char["dir_x"]
        if char["x"] < 10 or char["x"] > GAME_WIDTH - 20:
            char["dir_x"] *= -1

        char["y"] += char["speed_y"] * char["dir_y"]
        if char["y"] <= LOWER_ZONE_TOP or char["y"] >= GUIDE_BAR_TOP - 18:
            char["dir_y"] *= -1

    for clown in clowns[:]:
        clown["y"] += scroll_speed + clown_base_speed
        if clown["y"] > LOWER_ZONE_TOP:
            clowns.remove(clown)

    if len(clowns) < max_clowns:
        if random.random() < 0.02:
            spawn_clown()

    # 3. Drawing
    game_surface.blit(bg_image, (0, int(scroll_y)))
    game_surface.blit(bg_image, (0, int(scroll_y) - GAME_HEIGHT))

    for idx, char in enumerate(characters):
        cx, cy = int(char["x"]), int(char["y"])
        if idx == active_shooter_idx:
            pygame.draw.rect(game_surface, CYAN, (cx - 3, cy - 3, 14, 20), 1)

        pygame.draw.rect(game_surface, BLACK, (cx - 1, cy - 1, 10, 16))
        pygame.draw.rect(game_surface, char["hair"], (cx, cy, 8, 4))
        pygame.draw.rect(game_surface, (255, 200, 160), (cx + 1, cy + 3, 6, 4))
        pygame.draw.rect(game_surface, char["shirt"], (cx, cy + 7, 8, 4))
        pygame.draw.rect(game_surface, char["pants"], (cx + 1, cy + 11, 2, 3))
        pygame.draw.rect(game_surface, char["pants"], (cx + 5, cy + 11, 2, 3))

    for clown in clowns:
        cx, cy = int(clown["x"]), int(clown["y"])
        pygame.draw.rect(game_surface, BLACK, (cx - 3, cy - 5, 18, 24))
        pygame.draw.rect(game_surface, WHITE, (cx, cy, 12, 16))
        pygame.draw.rect(game_surface, GREEN, (cx - 3, cy - 1, 4, 8))
        pygame.draw.rect(game_surface, GREEN, (cx + 11, cy - 1, 4, 8))
        pygame.draw.rect(game_surface, PURPLE, (cx + 3, cy - 4, 6, 4))
        pygame.draw.rect(game_surface, YELLOW, (cx + 5, cy - 6, 2, 2))
        pygame.draw.rect(game_surface, RED, (cx + 4, cy + 3, 4, 4))
        pygame.draw.rect(game_surface, CYAN, (cx + 2, cy + 1, 2, 2))
        pygame.draw.rect(game_surface, CYAN, (cx + 8, cy + 1, 2, 2))
        pygame.draw.rect(game_surface, RED, (cx + 2, cy + 9, 8, 3))
        pygame.draw.rect(game_surface, YELLOW, (cx + 5, cy + 10, 2, 1))

    for line in shot_lines[:]:
        pygame.draw.line(game_surface, YELLOW, line[0], line[1], 2)
        line[2] -= 1
        if line[2] <= 0:
            shot_lines.remove(line)

    mx, my = pygame.mouse.get_pos()
    gx = int(mx * (GAME_WIDTH / SCREEN_WIDTH))
    gy = int(my * (GAME_HEIGHT / SCREEN_HEIGHT))
    pygame.draw.circle(game_surface, RED, (gx, gy), 5, 1)
    pygame.draw.line(game_surface, RED, (gx - 7, gy), (gx + 7, gy), 1)
    pygame.draw.line(game_surface, RED, (gx, gy - 7), (gx, gy + 7), 1)

    # Onderste gids-balk
    pygame.draw.rect(game_surface, DARK_GRAY, (0, GUIDE_BAR_TOP, GAME_WIDTH, GAME_HEIGHT - GUIDE_BAR_TOP))
    
    x_offset = 4
    for idx, char in enumerate(characters):
        label_color = char["shirt"]
        prefix = ">" if idx == active_shooter_idx else ""
        text_str = f"{prefix}{idx+1}:{char['name']}({char['score']})"
        
        name_txt = guide_font.render(text_str, True, label_color)
        game_surface.blit(name_txt, (x_offset, GUIDE_BAR_TOP + 8))
        x_offset += 83

    total_score = sum(c["score"] for c in characters)
    hud_text = font.render(f"SCORE: {total_score} | LEVEL: {level + 1} | [B]=Schiet [A]=Team", True, BLACK)
    game_surface.blit(hud_text, (8, 6))

    scaled = pygame.transform.scale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()