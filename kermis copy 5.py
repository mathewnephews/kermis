import pygame
import random
import sys

# Pygame initialiseren
pygame.init()

# Resolutie van het originele pixel-art canvas
GAME_WIDTH, GAME_HEIGHT = 420, 240
SCREEN_WIDTH, SCREEN_HEIGHT = 840, 480

# Definieer de zone voor de personages (iets hoger geplaatst)
LOWER_ZONE_TOP = int(GAME_HEIGHT * 0.75)  # Vanaf 75% van de hoogte
GUIDE_BAR_TOP = int(GAME_HEIGHT * 0.90)   # Onderste 10% gereserveerd voor de gids

game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("8-Bit Pretpark Arcade - Character Selection")

clock = pygame.time.Clock()

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

# Scrollende achtergrond
scroll_y = 0
scroll_speed = 1.0

# 5 Personages met hun unieke namen en herkenbare kleuren
characters = [
    {"name": "1:M@lb",    "x": 30,  "y": LOWER_ZONE_TOP + 2, "speed_x": 0.8, "speed_y": 0.2, "dir_x": 1,  "dir_y": 1,  "hair": (120, 60, 20),  "shirt": (40, 120, 220), "pants": (20, 40, 100)},
    {"name": "2:GDJ",     "x": 100, "y": LOWER_ZONE_TOP + 8, "speed_x": 1.1, "speed_y": 0.3, "dir_x": -1, "dir_y": -1, "hair": (200, 140, 60), "shirt": (220, 50, 80),  "pants": (220, 50, 80)},
    {"name": "3:SHAUG",   "x": 180, "y": LOWER_ZONE_TOP + 5, "speed_x": 0.7, "speed_y": 0.2, "dir_x": 1,  "dir_y": 1,  "hair": (40, 40, 40),   "shirt": (30, 200, 160), "pants": (30, 30, 30)},
    {"name": "4:BambiFF", "x": 260, "y": LOWER_ZONE_TOP + 12,"speed_x": 0.9, "speed_y": 0.3, "dir_x": -1, "dir_y": -1, "hair": (160, 80, 40),  "shirt": (240, 140, 40), "pants": (50, 50, 50)},
    {"name": "5:Phertron","x": 340, "y": LOWER_ZONE_TOP + 4, "speed_x": 1.0, "speed_y": 0.2, "dir_x": 1,  "dir_y": 1,  "hair": (230, 200, 100),"shirt": (180, 50, 200), "pants": (20, 20, 20)},
]

# De actieve schutter (standaard personage 1 / index 0)
active_shooter_idx = 0

# Visueel schooteffect
shot_line = None

# Clown variabelen
clown_x, clown_y = 0, 0
clown_visible = False
clown_timer = 0
clown_duration = 90

score = 100
font = pygame.font.SysFont("monospace", 10, bold=True)
guide_font = pygame.font.SysFont("monospace", 8, bold=True)

def spawn_clown():
    global clown_x, clown_y, clown_visible, clown_timer
    clown_x = random.randint(30, GAME_WIDTH - 40)
    clown_y = random.randint(20, LOWER_ZONE_TOP - 35)
    clown_visible = True
    clown_timer = clown_duration

# Game loop
running = True
while running:
    # 1. Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Toetsenbord selectie (1 t/m 5)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                active_shooter_idx = 0
            elif event.key == pygame.K_2:
                active_shooter_idx = 1
            elif event.key == pygame.K_3:
                active_shooter_idx = 2
            elif event.key == pygame.K_4:
                active_shooter_idx = 3
            elif event.key == pygame.K_5:
                active_shooter_idx = 4

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            gx = int(mx * (GAME_WIDTH / SCREEN_WIDTH))
            gy = int(my * (GAME_HEIGHT / SCREEN_HEIGHT))
            
            # Muisklik op personage selecteert deze ook
            hit_character = False
            for idx, char in enumerate(characters):
                char_rect = pygame.Rect(char["x"] - 2, char["y"] - 2, 12, 18)
                if char_rect.collidepoint(gx, gy):
                    active_shooter_idx = idx
                    hit_character = True
                    break
            
            # Schieten
            if not hit_character:
                shooter = characters[active_shooter_idx]
                start_pos = (int(shooter["x"]) + 4, int(shooter["y"]) + 4)
                
                shot_line = [start_pos, (gx, gy), 3]

                if clown_visible:
                    clown_rect = pygame.Rect(clown_x - 4, clown_y - 4, 20, 24)
                    if clown_rect.collidepoint(gx, gy):
                        score += 10
                        clown_visible = False

    # 2. Logic updates
    scroll_y = (scroll_y + scroll_speed) % GAME_HEIGHT

    # Personages laten bewegen in de verhoogde zone
    for char in characters:
        char["x"] += char["speed_x"] * char["dir_x"]
        if char["x"] < 10 or char["x"] > GAME_WIDTH - 20:
            char["dir_x"] *= -1

        char["y"] += char["speed_y"] * char["dir_y"]
        if char["y"] <= LOWER_ZONE_TOP or char["y"] >= GUIDE_BAR_TOP - 18:
            char["dir_y"] *= -1

    # Clown logica
    if clown_visible:
        clown_y += scroll_speed
        clown_timer -= 1
        if clown_timer <= 0 or clown_y > LOWER_ZONE_TOP:
            clown_visible = False
    else:
        if random.random() < 0.025:
            spawn_clown()

    # 3. Drawing
    # Achtergrond
    game_surface.blit(bg_image, (0, int(scroll_y)))
    game_surface.blit(bg_image, (0, int(scroll_y) - GAME_HEIGHT))

    # Pixelart Personages
    for idx, char in enumerate(characters):
        cx, cy = int(char["x"]), int(char["y"])
        
        # Cyan kader rondom de momenteel actieve schutter
        if idx == active_shooter_idx:
            pygame.draw.rect(game_surface, CYAN, (cx - 3, cy - 3, 14, 20), 1)

        # Omtrek
        pygame.draw.rect(game_surface, BLACK, (cx - 1, cy - 1, 10, 16))
        # Hoofd & Haar
        pygame.draw.rect(game_surface, char["hair"], (cx, cy, 8, 4))
        pygame.draw.rect(game_surface, (255, 200, 160), (cx + 1, cy + 3, 6, 4))
        # Kleding
        pygame.draw.rect(game_surface, char["shirt"], (cx, cy + 7, 8, 4))
        # Benen
        pygame.draw.rect(game_surface, char["pants"], (cx + 1, cy + 11, 2, 3))
        pygame.draw.rect(game_surface, char["pants"], (cx + 5, cy + 11, 2, 3))

    # Clowneske Clown
    if clown_visible:
        cx, cy = int(clown_x), int(clown_y)
        # Zwarte outline
        pygame.draw.rect(game_surface, BLACK, (cx - 3, cy - 5, 18, 24))
        # Wit gezicht/pak
        pygame.draw.rect(game_surface, WHITE, (cx, cy, 12, 16))
        # Grote wilde groene pruik aan de zijkanten
        pygame.draw.rect(game_surface, GREEN, (cx - 3, cy - 1, 4, 8))
        pygame.draw.rect(game_surface, GREEN, (cx + 11, cy - 1, 4, 8))
        # Paars feesthoedje met gele punt
        pygame.draw.rect(game_surface, PURPLE, (cx + 3, cy - 4, 6, 4))
        pygame.draw.rect(game_surface, YELLOW, (cx + 5, cy - 6, 2, 2))
        # Grote rode neus
        pygame.draw.rect(game_surface, RED, (cx + 4, cy + 3, 4, 4))
        # Schmink / Ogen
        pygame.draw.rect(game_surface, CYAN, (cx + 2, cy + 1, 2, 2))
        pygame.draw.rect(game_surface, CYAN, (cx + 8, cy + 1, 2, 2))
        # Rode Strik / Vlinderdas
        pygame.draw.rect(game_surface, RED, (cx + 2, cy + 9, 8, 3))
        pygame.draw.rect(game_surface, YELLOW, (cx + 5, cy + 10, 2, 1))

    # Schietlijn
    if shot_line and shot_line[2] > 0:
        pygame.draw.line(game_surface, YELLOW, shot_line[0], shot_line[1], 2)
        shot_line[2] -= 1

    # Vizier / Crosshair
    mx, my = pygame.mouse.get_pos()
    gx = int(mx * (GAME_WIDTH / SCREEN_WIDTH))
    gy = int(my * (GAME_HEIGHT / SCREEN_HEIGHT))
    pygame.draw.circle(game_surface, RED, (gx, gy), 5, 1)
    pygame.draw.line(game_surface, RED, (gx - 7, gy), (gx + 7, gy), 1)
    pygame.draw.line(game_surface, RED, (gx, gy - 7), (gx, gy + 7), 1)

    # Onderste gids-balk voor toetsenbordbesturing
    pygame.draw.rect(game_surface, DARK_GRAY, (0, GUIDE_BAR_TOP, GAME_WIDTH, GAME_HEIGHT - GUIDE_BAR_TOP))
    
    # Render gidsnamen in de kleur van hun t-shirt
    x_offset = 6
    for idx, char in enumerate(characters):
        # Markeer de geselecteerde naam met een haakje/kleur
        label_color = char["shirt"]
        prefix = ">" if idx == active_shooter_idx else ""
        text_str = f"{prefix}{char['name']}"
        
        name_txt = guide_font.render(text_str, True, label_color)
        game_surface.blit(name_txt, (x_offset, GUIDE_BAR_TOP + 6))
        x_offset += 82  # Afstand tussen de namen op de onderbalk

    # Score
    score_text = font.render(f"SCORE: {score}", True, BLACK)
    game_surface.blit(score_text, (8, 6))

    # 4. Upscalen naar scherm
    scaled = pygame.transform.scale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()