import pygame
import random
import sys

# Pygame initialiseren
pygame.init()

# Resolutie: Lage resolutie voor de 8-bit look, opgeschaald naar scherm
GAME_WIDTH, GAME_HEIGHT = 320, 240
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480

game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("8-Bit Pretpark Clown Shooter")

clock = pygame.time.Clock()

# Kleuren (8-bit arcade palet)
SKY_BLUE = (100, 160, 240)
GROUND_GRAY = (120, 120, 130)
PATH_YELLOW = (220, 200, 120)
WHITE = (255, 255, 255)
RED = (220, 40, 40)
DARK_RED = (150, 20, 20)
GREEN = (40, 180, 40)
BLACK = (0, 0, 0)
PURPLE = (140, 60, 180)

# Pretpark Attracties (Achtergronddecor)
attractions = [
    {"type": "reuzenrad", "x": 30, "y": 80},
    {"type": "achtbaan", "x": 140, "y": 90},
    {"type": "tent", "x": 250, "y": 100}
]

# 5 Personages die door het park wandelen (Walkthrough)
# Ze lopen op verschillende snelheden en hoogtes langs elkaar heen
characters = [
    {"x": random.randint(0, GAME_WIDTH), "y": 150, "speed": 0.8, "color": (230, 80, 80)},
    {"x": random.randint(0, GAME_WIDTH), "y": 160, "speed": 1.2, "color": (80, 200, 80)},
    {"x": random.randint(0, GAME_WIDTH), "y": 170, "speed": 0.5, "color": (80, 120, 230)},
    {"x": random.randint(0, GAME_WIDTH), "y": 180, "speed": 1.0, "color": (230, 220, 80)},
    {"x": random.randint(0, GAME_WIDTH), "y": 190, "speed": 0.7, "color": (200, 80, 200)},
]

# Clown variabelen
clown_x = 0
clown_y = 0
clown_visible = False
clown_timer = 0
clown_duration = 90  # Frames dat een clown zichtbaar blijft (~1.5 sec)

score = 0
font = pygame.font.SysFont("monospace", 12, bold=True)

def spawn_clown():
    global clown_x, clown_y, clown_visible, clown_timer
    clown_x = random.randint(20, GAME_WIDTH - 30)
    clown_y = random.randint(70, GAME_HEIGHT - 60)
    clown_visible = True
    clown_timer = clown_duration

# Game loop
running = True
while running:
    # 1. Events verwerken
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Klikpositie omrekenen naar de lage resolutie van de game
            mx, my = event.pos
            gx = int(mx * (GAME_WIDTH / SCREEN_WIDTH))
            gy = int(my * (GAME_HEIGHT / SCREEN_HEIGHT))
            
            # Check of op de clown is geklikt
            if clown_visible:
                clown_rect = pygame.Rect(clown_x, clown_y, 16, 20)
                if clown_rect.collidepoint(gx, gy):
                    score += 10
                    clown_visible = False

    # 2. Spellogica updaten
    # Personages laten wandelen
    for char in characters:
        char["x"] += char["speed"]
        if char["x"] > GAME_WIDTH + 10:
            char["x"] = -15  # Reset naar links als ze van het scherm lopen

    # Clown spawner logica
    if clown_visible:
        clown_timer -= 1
        if clown_timer <= 0:
            clown_visible = False
    else:
        # 2% kans per frame om een nieuwe clown te laten verschijnen
        if random.random() < 0.02:
            spawn_clown()

    # 3. Tekenen op het lage-resolutie canvas
    # Achtergrond & Lucht
    game_surface.fill(SKY_BLUE)
    
    # Wandelpad / Grond
    pygame.draw.rect(game_surface, GROUND_GRAY, (0, 130, GAME_WIDTH, GAME_HEIGHT - 130))
    pygame.draw.rect(game_surface, PATH_YELLOW, (0, 145, GAME_WIDTH, 65))

    # Attracties tekenen (8-bit stijl)
    for attr in attractions:
        if attr["type"] == "reuzenrad":
            pygame.draw.circle(game_surface, PURPLE, (attr["x"], attr["y"]), 25, 2)
            pygame.draw.line(game_surface, BLACK, (attr["x"], attr["y"]), (attr["x"] - 15, attr["y"] + 35), 2)
            pygame.draw.line(game_surface, BLACK, (attr["x"], attr["y"]), (attr["x"] + 15, attr["y"] + 35), 2)
        elif attr["type"] == "achtbaan":
            pygame.draw.arc(game_surface, RED, (attr["x"], attr["y"], 60, 40), 0, 3.14, 3)
            pygame.draw.line(game_surface, BLACK, (attr["x"] + 5, attr["y"] + 20), (attr["x"] + 5, attr["y"] + 40), 1)
            pygame.draw.line(game_surface, BLACK, (attr["x"] + 55, attr["y"] + 20), (attr["x"] + 55, attr["y"] + 40), 1)
        elif attr["type"] == "tent":
            pygame.draw.polygon(game_surface, DARK_RED, [(attr["x"], attr["y"] + 30), (attr["x"] + 20, attr["y"]), (attr["x"] + 40, attr["y"] + 30)])
            pygame.draw.rect(game_surface, WHITE, (attr["x"] + 5, attr["y"] + 30, 30, 15))

    # Wandelende personages tekenen
    for char in characters:
        x, y = int(char["x"]), int(char["y"])
        # Lichaam
        pygame.draw.rect(game_surface, char["color"], (x, y, 10, 14))
        # Hoofd
        pygame.draw.rect(game_surface, (255, 220, 180), (x + 1, y - 6, 8, 6))

    # Clown tekenen (indien actief)
    if clown_visible:
        # Clown lichaam
        pygame.draw.rect(game_surface, WHITE, (clown_x, clown_y, 16, 20))
        # Clown gezicht / hoed
        pygame.draw.rect(game_surface, RED, (clown_x + 6, clown_y + 4, 4, 4))  # Rode neus
        pygame.draw.rect(game_surface, PURPLE, (clown_x + 2, clown_y - 4, 12, 4))  # Hoedje
        pygame.draw.rect(game_surface, GREEN, (clown_x - 2, clown_y + 2, 4, 8))  # Groen haar links
        pygame.draw.rect(game_surface, GREEN, (clown_x + 14, clown_y + 2, 4, 8))  # Groen haar rechts

    # Crosshair / Vizier op de muispositie
    mx, my = pygame.mouse.get_pos()
    gx = int(mx * (GAME_WIDTH / SCREEN_WIDTH))
    gy = int(my * (GAME_HEIGHT / SCREEN_HEIGHT))
    pygame.draw.circle(game_surface, RED, (gx, gy), 4, 1)
    pygame.draw.line(game_surface, RED, (gx - 6, gy), (gx + 6, gy), 1)
    pygame.draw.line(game_surface, RED, (gx, gy - 6), (gx, gy + 6), 1)

    # Score tonen
    score_text = font.render(f"SCORE: {score}", True, BLACK)
    game_surface.blit(score_text, (5, 5))

    # 4. Canvas opschalen naar het scherm (voor de pixelart-look)
    scaled_surface = pygame.transform.scale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()