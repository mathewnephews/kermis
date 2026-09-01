import pygame
import random
import sys

# Pygame initialiseren
pygame.init()

# Resolutie van het originele pixel-art canvas
GAME_WIDTH, GAME_HEIGHT = 420, 240
SCREEN_WIDTH, SCREEN_HEIGHT = 840, 480

# Definieer de onderste 1/5e van het scherm voor de personages
LOWER_ZONE_TOP = int(GAME_HEIGHT * 0.8)  # Vanaf 80% van de hoogte

game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("8-Bit Pretpark Arcade - Shooter Mechanic")

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
RED = (220, 40, 40)
BLACK = (0, 0, 0)
GREEN = (40, 180, 40)
PURPLE = (140, 60, 180)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Verticaal scrollende achtergrond offset
scroll_y = 0
scroll_speed = 1.0

# 5 Personages beperkt tot de onderste 1/5e van het scherm
characters = [
    {"x": 30, "y": LOWER_ZONE_TOP + 5, "speed_x": 0.8, "speed_y": 0.3, "dir_x": 1, "dir_y": 1, "hair": (120, 60, 20), "shirt": (40, 120, 220), "pants": (20, 40, 100)},
    {"x": 100, "y": LOWER_ZONE_TOP + 15, "speed_x": 1.1, "speed_y": 0.4, "dir_x": -1, "dir_y": -1, "hair": (200, 140, 60), "shirt": (220, 50, 80), "pants": (220, 50, 80)},
    {"x": 180, "y": LOWER_ZONE_TOP + 10, "speed_x": 0.7, "speed_y": 0.2, "dir_x": 1, "dir_y": 1, "hair": (40, 40, 40), "shirt": (30, 60, 160), "pants": (30, 30, 30)},
    {"x": 260, "y": LOWER_ZONE_TOP + 20, "speed_x": 0.9, "speed_y": 0.5, "dir_x": -1, "dir_y": -1, "hair": (160, 80, 40), "shirt": (200, 40, 60), "pants": (50, 50, 50)},
    {"x": 340, "y": LOWER_ZONE_TOP + 8, "speed_x": 1.0, "speed_y": 0.3, "dir_x": 1, "dir_y": 1, "hair": (230, 200, 100), "shirt": (120, 40, 160), "pants": (20, 20, 20)},
]

# De actieve schutter (index in characters-lijst, None indien nog geen gekozen)
active_shooter_idx = None

# Visueel schooteffect (lijn van schutter naar doel)
shot_line = None  # Slaat op: ((start_x, start_y), (target_x, target_y), timer)

# Clown spawner instellingen
clown_x, clown_y = 0, 0
clown_visible = False
clown_timer = 0
clown_duration = 90

score = 100
font = pygame.font.SysFont("monospace", 12, bold=True)

def spawn_clown():
    global clown_x, clown_y, clown_visible, clown_timer
    # Clowns verschijnen in het speelveld boven de 1/5e zone
    clown_x = random.randint(30, GAME_WIDTH - 40)
    clown_y = random.randint(20, LOWER_ZONE_TOP - 30)
    clown_visible = True
    clown_timer = clown_duration

# Game loop
running = True
while running:
    # 1. Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            gx = int(mx * (GAME_WIDTH / SCREEN_WIDTH))
            gy = int(my * (GAME_HEIGHT / SCREEN_HEIGHT))
            
            # Check eerst of er op een van de 5 figuurtjes is geklikt
            hit_character = False
            for idx, char in enumerate(characters):
                char_rect = pygame.Rect(char["x"] - 2, char["y"] - 2, 12, 18)
                if char_rect.collidepoint(gx, gy):
                    active_shooter_idx = idx  # Deze figuur wordt de nieuwe schutter
                    hit_character = True
                    break
            
            # Als er niet op een personage is geklikt, vuur een schot af
            if not hit_character:
                start_pos = (gx, gy)
                
                # Als er een schutter is geselecteerd, vertrekt de kogel vanaf de schutter
                if active_shooter_idx is not None:
                    shooter = characters[active_shooter_idx]
                    start_pos = (int(shooter["x"]) + 4, int(shooter["y"]) + 4)
                
                # Stel een visuele schietlijn in (3 frames zichtbaar)
                shot_line = [start_pos, (gx, gy), 3]

                # Check of clown geraakt is
                if clown_visible:
                    clown_rect = pygame.Rect(clown_x - 2, clown_y - 2, 16, 20)
                    if clown_rect.collidepoint(gx, gy):
                        score += 10
                        clown_visible = False

    # 2. Logic updates
    # Achtergrond verticaal laten scrollen
    scroll_y = (scroll_y + scroll_speed) % GAME_HEIGHT

    # Personages laten bewegen binnen het onderste 1/5e gedeelte
    for char in characters:
        # Horizontale beweging
        char["x"] += char["speed_x"] * char["dir_x"]
        if char["x"] < 10 or char["x"] > GAME_WIDTH - 20:
            char["dir_x"] *= -1

        # Verticale beweging (beperkt tot onderste 1/5e)
        char["y"] += char["speed_y"] * char["dir_y"]
        if char["y"] <= LOWER_ZONE_TOP or char["y"] >= GAME_HEIGHT - 18:
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

    # Visuele markering voor de 1/5e zone aan de onderkant
    pygame.draw.line(game_surface, YELLOW, (0, LOWER_ZONE_TOP), (GAME_WIDTH, LOWER_ZONE_TOP), 1)

    # Pixelart Personages tekenen
    for idx, char in enumerate(characters):
        cx, cy = int(char["x"]), int(char["y"])
        
        # Markering als dit de actieve schutter is
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

    # Clown
    if clown_visible:
        cx, cy = int(clown_x), int(clown_y)
        pygame.draw.rect(game_surface, BLACK, (cx - 1, cy - 1, 14, 18))
        pygame.draw.rect(game_surface, WHITE, (cx, cy, 12, 16))
        pygame.draw.rect(game_surface, PURPLE, (cx + 2, cy - 3, 8, 3))
        pygame.draw.rect(game_surface, GREEN, (cx - 2, cy + 2, 3, 6))
        pygame.draw.rect(game_surface, GREEN, (cx + 11, cy + 2, 3, 6))
        pygame.draw.rect(game_surface, RED, (cx + 4, cy + 5, 4, 3))

    # Schietlijn / Kogel spoor tekenen
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