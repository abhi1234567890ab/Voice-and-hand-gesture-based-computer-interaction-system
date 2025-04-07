import pygame
import random
import cv2
import mediapipe as mp
import threading
import numpy as np
import time

# Game Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 700
GAME_WIDTH = 600
CAM_WIDTH = 600
HEIGHT = 700
LANES = [100, 250, 400]
CAR_WIDTH, CAR_HEIGHT = 50, 100
FPS = 60

# Colors
WHITE = (255, 255, 255)
ROAD_COLOR = (50, 50, 50)
LANE_COLOR = (255, 255, 255)
RED = (200, 0, 0)

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("2D Car Game with Camera")

# Load images
player_car = pygame.image.load("player_car.png")
player_car = pygame.transform.scale(player_car, (CAR_WIDTH, CAR_HEIGHT))

enemy_car = pygame.image.load("enemy.png")
enemy_car = pygame.transform.scale(enemy_car, (CAR_WIDTH, CAR_HEIGHT))

# Player properties
player_x = LANES[1]
player_y = HEIGHT - 150
is_jumping = False
jump_start_time = 0
jump_duration = 1.0  # in seconds

# Game variables
enemies = []
enemy_speed = 2.5  # Slower starting speed
spawn_rate = 100
score = 0
font = pygame.font.Font(None, 36)

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
camera_frame = np.zeros((HEIGHT, CAM_WIDTH, 3), dtype=np.uint8)  # Placeholder

# Hand tracking thread
def track_hand():
    global player_x, camera_frame, is_jumping, jump_start_time

    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (CAM_WIDTH, HEIGHT))
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        lane_width = CAM_WIDTH // 3
        for i in range(1, 3):
            cv2.line(frame, (lane_width * i, 0), (lane_width * i, HEIGHT), (255, 255, 255), 2)

        if results.multi_hand_landmarks:
            for lm in results.multi_hand_landmarks:
                index_x = int(lm.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * CAM_WIDTH)
                wrist_y = lm.landmark[mp_hands.HandLandmark.WRIST].y

                # Lane detection
                if index_x < lane_width:
                    player_x = LANES[0]
                elif index_x < 2 * lane_width:
                    player_x = LANES[1]
                else:
                    player_x = LANES[2]

                # Raise hand jump detection (if hand lifted high)
                if wrist_y < 0.2 and not is_jumping:
                    is_jumping = True
                    jump_start_time = time.time()

        camera_frame = frame.copy()
        if not pygame.get_init():
            break

    cap.release()
    cv2.destroyAllWindows()

# Start hand tracking thread
threading.Thread(target=track_hand, daemon=True).start()

def spawn_enemy():
    global enemies
    if len(enemies) >= 2:
        return  # Prevent overcrowding

    occupied_lanes = [enemy[0] for enemy in enemies if enemy[1] < 200]
    available_lanes = [lane for lane in LANES if lane not in occupied_lanes]

    if available_lanes:
        lane = random.choice(available_lanes)
        enemies.append([lane, -CAR_HEIGHT])

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill((0, 0, 0))

    # Draw camera
    cam_surface = pygame.surfarray.make_surface(cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB).swapaxes(0, 1))
    screen.blit(cam_surface, (0, 0))

    # Draw road
    pygame.draw.rect(screen, ROAD_COLOR, (CAM_WIDTH, 0, GAME_WIDTH, HEIGHT))
    for lane_x in [CAM_WIDTH + 175, CAM_WIDTH + 325]:
        pygame.draw.line(screen, LANE_COLOR, (lane_x, 0), (lane_x, HEIGHT), 5)

    # Score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (CAM_WIDTH + 20, 20))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and not is_jumping:
        is_jumping = True
        jump_start_time = time.time()

    # Enemy logic
    if random.randint(1, spawn_rate) < 3:
        spawn_enemy()

    for enemy in enemies:
        enemy[1] += enemy_speed
        screen.blit(enemy_car, (CAM_WIDTH + enemy[0], enemy[1]))

    # Collision
    if not is_jumping:
        for enemy in enemies:
            if player_y < enemy[1] + CAR_HEIGHT and player_y + CAR_HEIGHT > enemy[1]:
                if player_x == enemy[0]:
                    running = False

    # Jump logic
    if is_jumping and (time.time() - jump_start_time > jump_duration):
        is_jumping = False

    # Player car
    jump_offset = 30 if is_jumping else 0
    screen.blit(player_car, (CAM_WIDTH + player_x, player_y - jump_offset))

    # Clean up enemies
    enemies = [e for e in enemies if e[1] < HEIGHT]
    score += 1

    # Difficulty scale
    if score % 500 == 0:
        enemy_speed += 0.2
    if score % 1000 == 0 and spawn_rate > 30:
        spawn_rate -= 5

    pygame.display.update()
    clock.tick(FPS)

# Game Over
screen.fill(ROAD_COLOR)
game_over_text = font.render("Game Over!", True, RED)
screen.blit(game_over_text, (CAM_WIDTH + GAME_WIDTH // 2 - 80, HEIGHT // 2 - 20))
pygame.display.update()
pygame.time.delay(3000)
pygame.quit()
