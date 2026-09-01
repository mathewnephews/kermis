import pygame
import random
import sys
import math
import array
import asyncio

# Pygame & Mixer initialiseren
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

# Resolutie
GAME_WIDTH, GAME_HEIGHT = 420, 240
SCREEN_WIDTH, SCREEN_HEIGHT = 840, 480

LOWER_ZONE_TOP = int(GAME_HEIGHT * 0.65)
GUIDE_BAR_TOP = int(GAME_HEIGHT * 0.88)

game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("8-Bit Pretpark Arcade - Web Edition")

clock = pygame.time.Clock()

# --- 8-BIT GELUIDSGENERATOR ---
def generate_8bit_sound(freq_start, freq_end, duration, wave_type="square"):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    
    for i in range(n_samples):
        t = i / sample_rate
        progress = i / n_samples
        freq = freq_start + (freq_end - freq_start) * progress
        
        if wave_type == "square":
            value = 1 if (math.sin(2 * math.pi * freq * t) >= 0) else -1
        else:
            value = random.uniform(-1, 1)
            
        sample = int(value * 8000)
        buf.append(sample)
        
    return pygame.mixer.Sound(buffer=buf)

# Mario Dying Sound
async def play_mario_die_sound():
    notes = [(400, 0.12), (300, 0.12), (200, 0.12), (100, 0.35)]
    for freq, duration in notes:
        snd = generate_8bit_sound(freq, freq - 20, duration, "square")
        snd.play()
        await asyncio.sleep(duration)

# Geluiden
snd_shoot = generate_8bit_sound(800, 200, 0.1, "square")
snd_hit = generate_8bit_sound(400, 1000, 0.15, "square")
snd_miss = generate_8bit_sound(150, 50, 0.08, "noise")
snd_die = generate_8bit_sound(300, 80, 0.25, "square")

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
GRAY = (100, 100, 100)

scroll_y = 0
scroll_speed = 1.0

group_center_x = GAME_WIDTH // 2
group_center_y = LOWER_ZONE_TOP + 15

characters = [
    {"name": "M@lb",    "key_name": "A", "key": pygame.K_a, "rel_x": -35, "rel_y": 0,  "alive": True, "respawn_counter": 0, "score": 0, "hair": (120, 60, 20),  "shirt": (40, 120, 220), "pants": (20, 40, 100)},
    {"name": "GDJ",     "key_name": "R", "key": pygame.K_r, "rel_x": -18, "rel_y": 5,  "alive": True, "respawn_counter": 0, "score": 0, "hair": (200, 140, 60), "shirt": (220, 50, 80),  "pants": (220, 50, 80)},
    {"name": "SHAUG",   "key_name": "C", "key": pygame.K_c, "rel_x": 0,   "rel_y": -3, "alive": True, "respawn_counter": 0, "score": 0, "hair": (40, 40, 40),   "shirt": (30, 200, 160), "pants": (30, 30, 30)},
    {"name": "BambiFF", "key_name": "U", "key": pygame.K_u, "rel_x": 18,  "rel_y": 6,  "alive": True, "respawn_counter": 0, "score": 0, "hair": (160, 80, 40),  "shirt": (240, 140, 40), "pants": (50, 50, 50)},
    {"name": "Phertron","key_name": "P", "key": pygame.K_p, "rel_x": 35,  "rel_y": 1,  "alive": True, "respawn_counter": 0, "score": 0, "hair": (230, 200, 100),"shirt": (180, 50, 200), "pants": (20, 20, 20)},
]

active_shooter_idx = 0
shot_lines = []
clowns = []
total_hits = 0
game_over = False

font = pygame.font.SysFont("monospace", 10, bold=True)
game_over_font = pygame.font.SysFont("monospace", 24, bold=True)
guide_font = pygame.font.SysFont("monospace", 8, bold=True)

def spawn_clown():
    clowns.append({
        "x": random.randint(30, GAME_WIDTH - 40),
        "y": -20
    })

def perform_shot(shooter_indices, target_pos=None):
    global total_hits
    hit_registered = False

    valid_shooters = [i for i in shooter_indices if characters[i]["alive"]]
    if not valid_shooters:
        return

    snd_shoot.play()

    for idx in valid_shooters:
        char = characters[idx]
        cx = int(group_center_x + char["rel_x"])
        cy = int(group_center_y + char["rel_y"])
        start_pos = (cx + 4, cy)

        end_pos = target_pos if target_pos else (cx + 4, 0)
        shot_lines.append([start_pos, end_pos, 3])

        for clown in clowns[:]:
            clown_rect = pygame.Rect(clown["x"] - 4, clown["y"] - 4, 20, 24)
            is_hit = clown_rect.collidepoint(end_pos) if target_pos else (clown_rect.left <= start_pos[0] <= clown_rect.right and clown_rect.bottom >= 0)
            
            if is_hit and clown in clowns:
                clowns.remove(clown)
                char["score"] += 10
                total_hits += 1
                hit_registered = True
                snd_hit.play()
                
                for c in characters:
                    if not c["alive"]:
                        c["respawn_counter"] += 1
                        if c["respawn_counter"] >= 2:
                            c["alive"] = True
                            c["respawn_counter"] = 0
                break

    if not hit_registered and valid_shooters:
        snd_miss.play()

def shoot_nearest_clown():
    if not clowns:
        perform_shot([active_shooter_idx])
        return

    sorted_clowns = sorted(clowns, key=lambda c: c["y"], reverse=True)
    target_clown = sorted_clowns[0]
    target_pos = (target_clown["x"] + 6, target_clown["y"] + 8)

    perform_shot([active_shooter_idx], target_pos)

# Async Main Function voor Webbrowser / Pygbag
async def main():
    global scroll_y, group_center_x, group_center_y, active_shooter_idx, total_hits, game_over

    running = True
    mario_sound_played = False

    while running:
        level = total_hits // 10
        clown_base_speed = 0.4 + (level * 0.15)
        max_clowns = min(1 + level, 5)

        # 1. Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN and not game_over:
                for idx, char in enumerate(characters):
                    if event.key == char["key"]:
                        active_shooter_idx = idx
                        perform_shot([idx])

                if event.key == pygame.K_z:
                    perform_shot([0, 1, 2, 3, 4])

                elif event.key == pygame.K_x:
                    shoot_nearest_clown()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                perform_shot([active_shooter_idx])

        if not game_over:
            # 2. Beweging
            keys = pygame.key.get_pressed()
            speed = 2.0

            if keys[pygame.K_LEFT]:
                group_center_x -= speed
            if keys[pygame.K_RIGHT]:
                group_center_x += speed
            if keys[pygame.K_UP]:
                group_center_y -= speed
            if keys[pygame.K_DOWN]:
                group_center_y += speed

            mx, my = pygame.mouse.get_pos()
            gx = int(mx * (GAME_WIDTH / SCREEN_WIDTH))
            gy = int(my * (GAME_HEIGHT / SCREEN_HEIGHT))
            
            group_center_x += (gx - group_center_x) * 0.1
            group_center_y += (gy - group_center_y) * 0.1

            group_center_x = max(50, min(GAME_WIDTH - 50, group_center_x))
            group_center_y = max(LOWER_ZONE_TOP + 10, min(GUIDE_BAR_TOP - 20, group_center_y))

            # 3. Logic updates
            scroll_y = (scroll_y + scroll_speed) % GAME_HEIGHT

            for clown in clowns[:]:
                clown["y"] += scroll_speed + clown_base_speed
                clown_rect = pygame.Rect(clown["x"] - 3, clown["y"] - 3, 18, 22)

                for char in characters:
                    if char["alive"]:
                        cx = int(group_center_x + char["rel_x"])
                        cy = int(group_center_y + char["rel_y"])
                        char_rect = pygame.Rect(cx - 1, cy - 1, 10, 16)
                        
                        if clown_rect.colliderect(char_rect):
                            char["alive"] = False
                            char["respawn_counter"] = 0
                            snd_die.play()
                            if clown in clowns:
                                clowns.remove(clown)
                            break

                if clown["y"] > LOWER_ZONE_TOP + 30 and clown in clowns:
                    clowns.remove(clown)

            # Check op Game Over
            if all(not c["alive"] for c in characters):
                game_over = True

            if len(clowns) < max_clowns:
                if random.random() < 0.02:
                    spawn_clown()
        
        elif game_over and not mario_sound_played:
            mario_sound_played = True
            pygame.mixer.stop()
            await play_mario_die_sound()

        # 4. Drawing
        game_surface.blit(bg_image, (0, int(scroll_y)))
        game_surface.blit(bg_image, (0, int(scroll_y) - GAME_HEIGHT))

        for idx, char in enumerate(characters):
            cx = int(group_center_x + char["rel_x"])
            cy = int(group_center_y + char["rel_y"])

            if char["alive"]:
                if idx == active_shooter_idx:
                    pygame.draw.rect(game_surface, CYAN, (cx - 3, cy - 3, 14, 20), 1)

                pygame.draw.rect(game_surface, BLACK, (cx - 1, cy - 1, 10, 16))
                pygame.draw.rect(game_surface, char["hair"], (cx, cy, 8, 4))
                pygame.draw.rect(game_surface, (255, 200, 160), (cx + 1, cy + 3, 6, 4))
                pygame.draw.rect(game_surface, char["shirt"], (cx, cy + 7, 8, 4))
                pygame.draw.rect(game_surface, char["pants"], (cx + 1, cy + 11, 2, 3))
                pygame.draw.rect(game_surface, char["pants"], (cx + 5, cy + 11, 2, 3))
            else:
                pygame.draw.rect(game_surface, GRAY, (cx, cy + 4, 8, 10))
                pygame.draw.line(game_surface, RED, (cx, cy + 2), (cx + 8, cy + 12), 2)
                pygame.draw.line(game_surface, RED, (cx + 8, cy + 2), (cx, cy + 12), 2)

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

        pygame.draw.circle(game_surface, RED, (gx, gy), 5, 1)
        pygame.draw.line(game_surface, RED, (gx - 7, gy), (gx + 7, gy), 1)
        pygame.draw.line(game_surface, RED, (gx, gy - 7), (gx, gy + 7), 1)

        pygame.draw.rect(game_surface, DARK_GRAY, (0, GUIDE_BAR_TOP, GAME_WIDTH, GAME_HEIGHT - GUIDE_BAR_TOP))
        
        x_offset = 4
        for idx, char in enumerate(characters):
            label_color = char["shirt"] if char["alive"] else GRAY
            prefix = ">" if idx == active_shooter_idx else ""
            status = f"({char['score']})" if char["alive"] else f"(DEAD:{char['respawn_counter']}/2)"
            text_str = f"{prefix}[{char['key_name']}]{char['name']}{status}"
            
            name_txt = guide_font.render(text_str, True, label_color)
            game_surface.blit(name_txt, (x_offset, GUIDE_BAR_TOP + 8))
            x_offset += 83

        total_score = sum(c["score"] for c in characters)
        hud_text = font.render(f"SCORE: {total_score} | LEVEL: {level + 1} | [Z]=All [X]=Lock", True, BLACK)
        game_surface.blit(hud_text, (8, 6))

        if game_over:
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            game_surface.blit(overlay, (0, 0))

            go_text = game_over_font.render("GAME OVER", True, RED)
            game_surface.blit(go_text, (GAME_WIDTH // 2 - 70, GAME_HEIGHT // 2 - 20))
            
            sub_text = font.render(f"FINAL SCORE: {total_score}", True, WHITE)
            game_surface.blit(sub_text, (GAME_WIDTH // 2 - 50, GAME_HEIGHT // 2 + 15))

        scaled = pygame.transform.scale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (0, 0))

        pygame.display.flip()
        clock.tick(60)
        
        # ESSENTIEEL VOOR BROWSER / PYGBAG:
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

# Start het spel via de asyncio loop
asyncio.run(main())