import pygame
import sys
import random
import heapq

pygame.init()

# ------------------------------------------------
# SCREEN SETTINGS
# ------------------------------------------------
WIDTH = 900
HEIGHT = 700
CELL = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monyet Mencari Makanan")

font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 72)

# ------------------------------------------------
# LOAD IMAGES
# ------------------------------------------------
try:
    img_hewan = pygame.image.load("hewan.png")
    img_hewan = pygame.transform.scale(img_hewan, (CELL, CELL))

    img_buah = pygame.image.load("buah.png")
    img_buah = pygame.transform.scale(img_buah, (CELL, CELL))
except:
    print("Pastikan file 'hewan.png' dan 'buah.png' ada di folder!")
    sys.exit()

# ------------------------------------------------
# HEURISTIC
# ------------------------------------------------
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# ------------------------------------------------
# A* PATHFINDING (ANTI MUSUH)
# ------------------------------------------------
def astar(start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            node = current
            while node in came_from:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return path

        x, y = current
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

        for nx, ny in neighbors:

            # JANGAN LEWATI MUSUH SAAT MODE BANTUAN
            if (nx, ny) == tuple(enemy_pos):
                continue

            if 0 <= nx < WIDTH//CELL and 0 <= ny < HEIGHT//CELL:
                new_cost = g[current] + 1
                if (nx, ny) not in g or new_cost < g[(nx, ny)]:
                    g[(nx, ny)] = new_cost
                    priority = new_cost + heuristic((nx, ny), goal)
                    heapq.heappush(open_set, (priority, (nx, ny)))
                    came_from[(nx, ny)] = current

    return []

# ------------------------------------------------
# RESET FUNCTION
# ------------------------------------------------
def reset_game():
    return (
        [5, 5],  # player
        [random.randint(0, WIDTH//CELL - 1),
         random.randint(0, HEIGHT//CELL - 1)],  # food
        [1, 1],  # enemy
        0,       # score
        1,       # level
        10,      # speed
        False, None, 0  # game_end, end_text, level_timer
    )

# INITIAL VALUES
player_pos, food_pos, enemy_pos, score, level, speed, game_end, end_text, level_timer = reset_game()
clock = pygame.time.Clock()
enemy_move_timer = 0

# ------------------------------------------------
# AUTO MODE (BANTUAN)
# ------------------------------------------------
auto_mode = False
auto_path = []

# ------------------------------------------------
# GAME LOOP
# ------------------------------------------------
while True:
    dt = clock.tick(speed)
    level_timer -= dt
    enemy_move_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_end:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                player_pos, food_pos, enemy_pos, score, level, speed, game_end, end_text, level_timer = reset_game()
            continue

        # --------------------------------------------------
        # TOMBOL BANTUAN (H)
        # --------------------------------------------------
        if event.type == pygame.KEYDOWN and not game_end:
            if event.key == pygame.K_h:
                auto_path = astar(tuple(player_pos), tuple(food_pos))
                if len(auto_path) > 0:
                    auto_mode = True

        # Manual movement ketika TIDAK dalam auto mode
        if not auto_mode and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player_pos[1] -= 1
            if event.key == pygame.K_DOWN:
                player_pos[1] += 1
            if event.key == pygame.K_LEFT:
                player_pos[0] -= 1
            if event.key == pygame.K_RIGHT:
                player_pos[0] += 1

            player_pos[0] = max(0, min(player_pos[0], WIDTH//CELL - 1))
            player_pos[1] = max(0, min(player_pos[1], HEIGHT//CELL - 1))

    if not game_end:

        # ------------------------------
        # AUTO MODE GERAK
        # ------------------------------
        if auto_mode and len(auto_path) > 0:
            next_step = auto_path.pop(0)
            player_pos = [next_step[0], next_step[1]]

            if player_pos == food_pos:
                auto_mode = False

        # Player makan makanan
        if player_pos == food_pos:
            score += 1
            food_pos = [random.randint(0, WIDTH//CELL - 1),
                        random.randint(0, HEIGHT//CELL - 1)]
            auto_mode = False

        # Enemy mengejar player
        if enemy_move_timer > 350:
            enemy_move_timer = 0
            enemy_path = astar(tuple(enemy_pos), tuple(player_pos))
            if len(enemy_path) > 0:
                enemy_pos = list(enemy_path[0])

        # ------------------------------------------------
        # GAME OVER (TIDAK BERLAKU saat AUTO MODE)
        # ------------------------------------------------
        if not auto_mode and player_pos == enemy_pos:
            game_end = True
            end_text = "GAME OVER"

        # Level System
        if score >= level * 3:
            level += 1
            speed += 2
            level_timer = 1500

        if level > 2:
            game_end = True
            end_text = "YOU WIN!"

    # ------------------------------------------------
    # DRAWING
    # ------------------------------------------------
    bg_color = [
        (240, 240, 240),
        (220, 240, 255),
        (255, 240, 220)
    ][min(level-1, 2)]
    screen.fill(bg_color)

    # GRID
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, (180, 180, 180), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, (180, 180, 180), (0, y), (WIDTH, y))

    # AUTO PATH
    if auto_mode:
        for px, py in auto_path:
            pygame.draw.rect(screen, (150, 220, 255), (px*CELL, py*CELL, CELL, CELL))

    # PATH MANUAL
    food_path = astar(tuple(player_pos), tuple(food_pos))
    for px, py in food_path:
        pygame.draw.rect(screen, (120, 200, 255), (px*CELL, py*CELL, CELL, CELL))

    # PLAYER
    screen.blit(img_hewan, (player_pos[0]*CELL, player_pos[1]*CELL))

    # FOOD
    screen.blit(img_buah, (food_pos[0]*CELL, food_pos[1]*CELL))

    # ENEMY
    pygame.draw.rect(screen, (200, 0, 0),
                     (enemy_pos[0]*CELL, enemy_pos[1]*CELL, CELL, CELL))

    # UI
    screen.blit(font.render(f"Score : {score}", True, (0, 0, 0)), (10, 10))

    if level <= 2:
        screen.blit(font.render(f"Level : {level}", True, (0, 0, 0)), (10, 40))

    screen.blit(font.render("Tekan H = Bantuan Cari Jalur Tercepat", True, (0, 0, 0)), (10, 70))

    if level_timer > 0 and level <= 2:
        text = big_font.render(f"LEVEL {level}!", True, (255, 0, 0))
        screen.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 50))

    # END SCREEN
    if game_end:
        font_big = pygame.font.Font(None, 130)

        # OUTLINE
        outline = font_big.render(end_text, True, (0, 0, 0))
        for ox, oy in [(-5,0),(5,0),(0,-5),(0,5)]:
            screen.blit(outline, outline.get_rect(center=(WIDTH//2 + ox, HEIGHT//2 + oy - 50)))

        # TEKS UTAMA
        if end_text == "GAME OVER":
            color = (255, 0, 0)
        else:
            color = (0, 255, 0)

        text = font_big.render(end_text, True, color)
        screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))

        screen.blit(font.render("Tekan R untuk Restart", True, (0, 0, 0)),
                    (WIDTH//2 - 130, HEIGHT//2 + 40))

    pygame.display.flip()
