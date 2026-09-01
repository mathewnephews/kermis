import pygame
import random
import sys

# Pygame initialiseren
pygame.init()

# Low-resolution canvas (vertical orientation) scaled up for 8-bit look
GAME_WIDTH, GAME_HEIGHT = 240, 320
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 640

game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("8-Bit Vertical Park Shooter")

clock = pygame.time.Clock()

# Colors (8-bit palette)
GRASS_GREEN = (60, 160, 60)
ROAD_GRAY = (90, 90, 100)
ROAD_SIDE = (220, 200, 120)
WHITE = (255, 255, 255)
RED = (220, 40, 40)
DARK_RED = (150, 20, 20)
GREEN = (40, 180, 40)        # <-- Added this line
BLUE = (60, 120, 220)
BLACK = (0, 0, 0)
PURPLE = (140, 60, 180)

# Scrolling environment properties
scroll_speed = 1.5
road_x_start = 40
road_width = 160

# Park Attractions scrolling from top to bottom
attractions = [
    {"type": "reuzenrad", "x": 10, "y": -50},
    {"type": "tent", "x": 190, "y": -200},
    {"type": "achtbaan", "x": 15, "y": -350},
    {"type": "tent", "x": 185, "y": -500}
]

# 5 Characters walking left <-> right on the road
characters = [
    {"x": random.randint(road_x_start, road_x_start + road_width - 10), "y": 140, "speed": 0.8, "dir": 1, "color": (230, 80, 80)},
    {"x": random.randint(road_x_start, road_x_start + road_width - 10), "y": 170, "speed": 1.2, "dir": -1, "color": (80, 200, 80)},
    {"x": random.randint(road_x_start, road_x_start + road_width - 10), "y": 200, "speed": 0.6, "dir": 1, "color": (80, 120, 230)},
    {"x": random.randint(road_x_start, road_x_start + road_width - 10), "y": 230, "speed": 1.0, "dir": -1, "color": (230, 220, 80)},
    {"x": random.randint(road_x_start, road_x_start + road_width - 10), "y": 260, "speed": 0.7, "dir": 1, "color": (200, 80, 200)},
]

# Clown variables
clown_x = 0
clown_y = 0
clown_visible = False
clown_timer = 0
clown_duration = 80

score = 0
font = pygame.font.SysFont("monospace", 12, bold=True)

def spawn_clown():
    global clown_x, clown_y, clown_visible, clown_timer
    clown_x = random.randint(road_x_start + 10, road_x_start + road_width - 20)
    clown_y = random.randint(30, GAME_HEIGHT - 50)
    clown_visible = True
    clown_timer = clown_duration

# Game loop
running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            gx = int(mx * (GAME_WIDTH / SCREEN_WIDTH))
            gy = int(my * (GAME_HEIGHT / SCREEN_HEIGHT))
            
            if clown_visible:
                clown_rect = pygame.Rect(clown_x, clown_y, 16, 18)
                if clown_rect.collidepoint(gx, gy):
                    score += 10
                    clown_visible = False

    # 2. Game Logic Updates
    # Move characters left <-> right along the road
    for char in characters:
        char["x"] += char["speed"] * char["dir"]
        # Bounce off road boundaries
        if char["x"] <= road_x_start + 5 or char["x"] >= (road_x_start + road_width - 15):
            char["dir"] *= -1

    # Scroll background attractions top -> down
    for attr in attractions:
        attr["y"] += scroll_speed
        if attr["y"] > GAME_HEIGHT + 50:
            attr["y"] = -150  # Loop back to top

    # Clown scroll & spawn logic
    if clown_visible:
        clown_y += scroll_speed  # Clown moves down with the environment
        clown_timer -= 1
        if clown_timer <= 0 or clown_y > GAME_HEIGHT:
            clown_visible = False
    else:
        if random.random() < 0.025:
            spawn_clown()

    # 3. Drawing
    # Grass Background
    game_surface.fill(GRASS_GREEN)
    
    # Vertical Road
    pygame.draw.rect(game_surface, ROAD_SIDE, (road_x_start - 4, 0, road_width + 8, GAME_HEIGHT))
    pygame.draw.rect(game_surface, ROAD_GRAY, (road_x_start, 0, road_width, GAME_HEIGHT))

    # Top-Down Attractions
    for attr in attractions:
        x, y = attr["x"], int(attr["y"])
        if attr["type"] == "reuzenrad":
            pygame.draw.circle(game_surface, PURPLE, (x + 15, y + 15), 18, 3)
            pygame.draw.circle(game_surface, BLACK, (x + 15, y + 15), 4)
        elif attr["type"] == "achtbaan":
            pygame.draw.rect(game_surface, RED, (x, y, 30, 40), 3)
            pygame.draw.line(game_surface, BLACK, (x, y + 20), (x + 30, y + 20), 2)
        elif attr["type"] == "tent":
            pygame.draw.rect(game_surface, DARK_RED, (x, y, 35, 25))
            pygame.draw.rect(game_surface, WHITE, (x + 5, y + 5, 25, 15))

    # Top-down walking characters
    for char in characters:
        cx, cy = int(char["x"]), int(char["y"])
        # Body / Shoulders
        pygame.draw.rect(game_surface, char["color"], (cx, cy, 10, 10))
        # Head (viewed from above)
        pygame.draw.circle(game_surface, (255, 220, 180), (cx + 5, cy + 5), 3)

    # Top-down Clown
    if clown_visible:
        cy = int(clown_y)
        pygame.draw.rect(game_surface, WHITE, (clown_x, cy, 14, 14))
        pygame.draw.circle(game_surface, RED, (clown_x + 7, cy + 7), 3)  # Red hair/nose center
        pygame.draw.rect(game_surface, GREEN, (clown_x - 2, cy + 2, 3, 10))  # Wild hair
        pygame.draw.rect(game_surface, GREEN, (clown_x + 13, cy + 2, 3, 10))

    # Crosshair
    mx, my = pygame.mouse.get_pos()
    gx = int(mx * (GAME_WIDTH / SCREEN_WIDTH))
    gy = int(my * (GAME_HEIGHT / SCREEN_HEIGHT))
    pygame.draw.circle(game_surface, RED, (gx, gy), 4, 1)
    pygame.draw.line(game_surface, RED, (gx - 5, gy), (gx + 5, gy), 1)
    pygame.draw.line(game_surface, RED, (gx, gy - 5), (gx, gy + 5), 1)

    # Score Overlay
    score_text = font.render(f"SCORE: {score}", True, WHITE)
    game_surface.blit(score_text, (5, 5))

    # 4. Upscale to screen resolution
    scaled_surface = pygame.transform.scale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()