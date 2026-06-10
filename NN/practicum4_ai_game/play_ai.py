import os
import random
from pathlib import Path

import joblib
import numpy as np
import pygame
import tensorflow as tf

WIDTH, HEIGHT = 500, 650
ROAD_LEFT, ROAD_RIGHT = 70, 430
LANES = 3
LANE_WIDTH = (ROAD_RIGHT - ROAD_LEFT) / LANES
CAR_W, CAR_H = 46, 76
OBSTACLE_W, OBSTACLE_H = 44, 70
PLAYER_Y = HEIGHT - 115
PLAYER_SPEED = 6
FPS = 60
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "best_model.keras"
SCALER_PATH = PROJECT_ROOT / "models" / "scaler.joblib"
N_FEATURES = 6


def lane_center(lane):
    return ROAD_LEFT + LANE_WIDTH * lane + LANE_WIDTH / 2


def lane_from_x(x):
    center = x + CAR_W / 2
    lane = int((center - ROAD_LEFT) // LANE_WIDTH)
    return max(0, min(LANES - 1, lane))


class RoadObstacle:
    def __init__(self, y=None):
        self.reset(y)

    def reset(self, y=None):
        self.lane = random.randrange(LANES)
        self.kind = random.choice(["car", "cone"])
        self.w = OBSTACLE_W if self.kind == "car" else 34
        self.h = OBSTACLE_H if self.kind == "car" else 42
        self.x = lane_center(self.lane) - self.w / 2
        self.y = y if y is not None else random.randint(-500, -90)
        self.speed = random.randint(5, 10)

    def update(self, score):
        self.y += self.speed + min(score // 8, 5) * 0.35
        if self.y > HEIGHT + 40:
            self.reset(random.randint(-420, -90))
            return True
        return False

    @property
    def type_value(self):
        return 0 if self.kind == "car" else 1

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.w), int(self.h))


def nearest_obstacle(obstacles):
    approaching = [obstacle for obstacle in obstacles if obstacle.y < PLAYER_Y + CAR_H]
    return max(approaching or obstacles, key=lambda obstacle: obstacle.y)


def features(player_x, obstacles):
    obstacle = nearest_obstacle(obstacles)
    player_center = player_x + CAR_W / 2
    obstacle_center = obstacle.x + obstacle.w / 2
    player_lane = lane_from_x(player_x)
    lane_delta = obstacle.lane - player_lane
    return np.array(
        [[
            player_center / WIDTH,
            obstacle_center / WIDTH,
            obstacle.y / HEIGHT,
            lane_delta / (LANES - 1),
            obstacle.speed / 12,
            obstacle.type_value,
        ]]
    )


def draw_car(screen, rect, color, windshield=(170, 220, 255)):
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, windshield, (rect.x + 9, rect.y + 9, rect.w - 18, 18), border_radius=4)
    pygame.draw.rect(screen, (35, 35, 35), (rect.x + 5, rect.y + 12, 6, 18), border_radius=2)
    pygame.draw.rect(screen, (35, 35, 35), (rect.right - 11, rect.y + 12, 6, 18), border_radius=2)
    pygame.draw.rect(screen, (35, 35, 35), (rect.x + 5, rect.bottom - 30, 6, 18), border_radius=2)
    pygame.draw.rect(screen, (35, 35, 35), (rect.right - 11, rect.bottom - 30, 6, 18), border_radius=2)


def draw_cone(screen, rect):
    points = [(rect.centerx, rect.y), (rect.x, rect.bottom), (rect.right, rect.bottom)]
    pygame.draw.polygon(screen, (245, 132, 31), points)
    pygame.draw.rect(screen, (255, 235, 180), (rect.x + 6, rect.y + rect.h // 2, rect.w - 12, 6))


def draw_road(screen, score):
    screen.fill((31, 86, 55))
    pygame.draw.rect(screen, (42, 45, 50), (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
    pygame.draw.line(screen, (235, 235, 210), (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
    pygame.draw.line(screen, (235, 235, 210), (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)
    offset = (score * 8) % 46
    for lane in range(1, LANES):
        x = int(ROAD_LEFT + LANE_WIDTH * lane)
        for y in range(-46 + offset, HEIGHT, 46):
            pygame.draw.line(screen, (235, 235, 235), (x, y), (x, y + 24), 3)

def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Geen getraind model gevonden. Verzamel data en run daarna train_model.py")
    model = tf.keras.models.load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    if getattr(scaler, "n_features_in_", N_FEATURES) != N_FEATURES:
        raise ValueError(
            "Het gevonden model/scaler hoort nog bij het oude rock-spel. "
            "Verzamel opnieuw data met game_collect_data.py en run daarna train_model.py."
        )
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Auto Game - AI mode")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    player_x = lane_center(1) - CAR_W / 2
    obstacles = [
        RoadObstacle(-140),
        RoadObstacle(-360),
        RoadObstacle(-590),
    ]
    score = 0
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        X = scaler.transform(features(player_x, obstacles))
        action = int(np.argmax(model.predict(X, verbose=0)[0]))
        if action == 0:
            player_x -= PLAYER_SPEED
        elif action == 2:
            player_x += PLAYER_SPEED
        player_x = max(ROAD_LEFT + 6, min(ROAD_RIGHT - CAR_W - 6, player_x))

        for obstacle in obstacles:
            if obstacle.update(score):
                score += 1

        player_rect = pygame.Rect(int(player_x), PLAYER_Y, CAR_W, CAR_H)
        if any(player_rect.colliderect(obstacle.rect) for obstacle in obstacles):
            print("AI game over! Score:", score)
            running = False

        draw_road(screen, score)
        for obstacle in obstacles:
            if obstacle.kind == "car":
                draw_car(screen, obstacle.rect, (190, 55, 65), windshield=(230, 230, 245))
            else:
                draw_cone(screen, obstacle.rect)
        draw_car(screen, player_rect, (45, 210, 135))
        label = ["links", "stil", "rechts"][action]
        text = font.render(f"AI mode | Score: {score} | Actie: {label}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
