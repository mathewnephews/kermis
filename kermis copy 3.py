import pygame
import random
import sys

# Pygame initialiseren
pygame.init()

# Resolutie van het originele pixel-art canvas
GAME_WIDTH, GAME_HEIGHT = 420, 240
SCREEN_WIDTH, SCREEN_HEIGHT = 840, 480

game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("8-Bit Pretpark Arcade")

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

# Verticaal scrollende achtergrond offset
scroll_y = 0
scroll_speed = 1.0

# 5 Detailrijke 8-bit personages (Hoofd, haar, kleding, broek/rok)
characters = [
    {"x": 40, "y": 60, "speed": 0.6, "dir": 1, "hair": (120, 60, 20), "shirt": (40, 120, 220), "pants": (20, 40, 100)},
    {"x": 65, "y": 140, "speed": 0.9, "dir": -1, "hair": (200, 140, 60), "shirt": (220, 50, 80), "pants": (220, 50, 80)},
    {"x": 330, "y": 50, "speed": 0.5, "dir": 1, "hair": (40, 40, 40), "shirt": (30, 60, 160), "pants": (30, 30, 30)},
    {"x": 360, "y": 130, "speed": 0.8, "dir": -1, "hair": (160, 80, 40), "shirt": (200, 40, 60), "pants": (50, 50, 50)},
    {"x": 340, "y": 190, "speed": 0.7, "dir": 1, "hair": (230, 200, 100), "shirt": (120, 40, 160), "pants": (20, 20, 20)},
]

# Clown spawner instellingen
clown_x, clown_y = 0, 0
clown_visible = False
clown_timer = 0
clown_duration = 90  # ~1.5 sec zichtbaar

score = 100
font = pygame.font.SysFont("monospace", 12, bold=True)

def spawn_clown():
    global clown_x, clown_y, clown_visible, clown_timer
    # Clowns verschijnen op het gras of bij attracties
    clown_x = random.randint(110, GAME_WIDTH - 130)
    clown_y = random.randint(20, GAME_HEIGHT - 40)
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
            
            if clown_visible:
                clown_rect = pygame.Rect(clown_x - 2, clown_y - 2, 16, 20)
                if clown_rect.collidepoint(gx, gy):
                    score += 10
                    clown_visible = False

    # 2. Logic updates
    # Achtergrond verticaal laten scrollen
    scroll_y = (scroll_y + scroll_speed) % GAME_HEIGHT

    # Personages heen en weer laten lopen op de wandelpaden
    for char in characters:
        char["x"] += char["speed"] * char["dir"]
        # Binnen de paden (links of rechts) houden
        if char["x"] < 25 or (80 < char["x"] < 310) or char["x"] > 380:
            char["dir"] *= -1

    # Clown logica
    if clown_visible:
        clown_y += scroll_speed
        clown_timer -= 1
        if clown_timer <= 0 or clown_y > GAME_HEIGHT:
            clown_visible = False
    else:
        if random.random() < 0.025:
            spawn_clown()

    # 3. Drawing
    # Achtergrond doortrekken (scrolling loop)
    game_surface.blit(bg_image, (0, int(scroll_y)))
    game_surface.blit(bg_image, (0, int(scroll_y) - GAME_HEIGHT))

    # Pixelart Menselijke Figuurtjes tekenen
    for char in characters:
        cx, cy = int(char["x"]), int(char["y"])
        # Omtrek (Black outline voor 8-bit stijl)
        pygame.draw.rect(game_surface, BLACK, (cx - 1, cy - 1, 10, 16))
        # Hoofd & Haar
        pygame.draw.rect(game_surface, char["hair"], (cx, cy, 8, 4))
        pygame.draw.rect(game_surface, (255, 200, 160), (cx + 1, cy + 3, 6, 4))
        # Kleding (T-shirt / Jurk)
        pygame.draw.rect(game_surface, char["shirt"], (cx, cy + 7, 8, 4))
        # Broek / Benen
        pygame.draw.rect(game_surface, char["pants"], (cx + 1, cy + 11, 2, 3))
        pygame.draw.rect(game_surface, char["pants"], (cx + 5, cy + 11, 2, 3))

    # Clown (uit de afbeelding)
    if clown_visible:
        cx, cy = int(clown_x), int(clown_y)
        # Zwarte omtrek
        pygame.draw.rect(game_surface, BLACK, (cx - 1, cy - 1, 14, 18))
        # Lichaam / Kostuum
        pygame.draw.rect(game_surface, WHITE, (cx, cy, 12, 16))
        pygame.draw.rect(game_surface, PURPLE, (cx + 2, cy - 3, 8, 3))  # Hoedje
        pygame.draw.rect(game_surface, GREEN, (cx - 2, cy + 2, 3, 6))   # Haar links
        pygame.draw.rect(game_surface, GREEN, (cx + 11, cy + 2, 3, 6))  # Haar rechts
        pygame.draw.rect(game_surface, RED, (cx + 4, cy + 5, 4, 3))     # Neus / Mond

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

    # 4. Upscalen voor scherp pixel-art effect
    scaled = pygame.transform.scale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()