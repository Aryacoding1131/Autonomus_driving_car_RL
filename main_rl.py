# =========================================================
# SMART CITY RL AUTONOMOUS VEHICLE SIMULATION
# =========================================================

import pygame
import sys
import random
import math

pygame.init()

# =========================================================
# WINDOW
# =========================================================

WIDTH = 1600
HEIGHT = 950

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart City RL Simulation")

clock = pygame.time.Clock()

# =========================================================
# COLORS
# =========================================================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

GRAY = (130, 130, 130)

GREEN = (0, 255, 0)
RED = (255, 0, 0)

BLUE = (0, 120, 255)

ROAD = (45, 45, 45)
ROAD_BORDER = (90, 90, 90)

GRASS = (40, 160, 40)

YELLOW = (255, 255, 0)

WINDOW_COLOR = (180, 220, 255)

# =========================================================
# FONT
# =========================================================

font = pygame.font.SysFont("arial", 20)

# =========================================================
# ROAD SETTINGS
# =========================================================

ROAD_WIDTH = 120

horizontal_roads = [150, 340, 530, 720]
vertical_roads = [220, 520, 820, 1120, 1420]

# =========================================================
# CITY POINTS
# =========================================================

points = {

    "A": (220, 720),
    "B": (520, 720),
    "C": (820, 720),
    "D": (1120, 720),

    "E": (220, 530),
    "F": (520, 530),
    "G": (820, 530),
    "H": (1120, 530),

    "I": (220, 340),
    "J": (520, 340),
    "K": (820, 340),
    "L": (1120, 340),

    "M": (220, 150),
    "N": (520, 150),
    "O": (820, 150),
    "P": (1120, 150)
}

# =========================================================
# USER INPUT
# =========================================================

print("\nAvailable Points: A-P")

start = input("Enter Start Point: ").upper()
destination = input("Enter Destination Point: ").upper()

while start not in points or destination not in points:

    print("Invalid Input!")

    start = input("Enter Start Point: ").upper()
    destination = input("Enter Destination Point: ").upper()

# =========================================================
# RL SETTINGS
# =========================================================

LEARNING_RATE = 0.1
DISCOUNT = 0.95
EPSILON = 0.25

q_table = {}

episode_rewards = []

exploration_mode = ""

# =========================================================
# CREATE ROAD CONNECTIONS
# =========================================================

neighbors = {}

for name, (x, y) in points.items():

    connected = []

    for other, (ox, oy) in points.items():

        if x == ox and abs(y - oy) == 190:
            connected.append(other)

        if y == oy and abs(x - ox) == 300:
            connected.append(other)

    neighbors[name] = connected

# =========================================================
# Q FUNCTIONS
# =========================================================

def get_q_value(state, action):

    if (state, action) not in q_table:

        q_table[(state, action)] = 0

    return q_table[(state, action)]

def set_q_value(state, action, value):

    q_table[(state, action)] = value

# =========================================================
# CHOOSE ACTION
# =========================================================

def choose_action(state):

    global exploration_mode

    if random.uniform(0, 1) < EPSILON:

        exploration_mode = "EXPLORATION"

        return random.choice(neighbors[state])

    exploration_mode = "EXPLOITATION"

    values = []

    for nxt in neighbors[state]:

        values.append(
            get_q_value(state, nxt)
        )

    max_q = max(values)

    best_actions = []

    for nxt in neighbors[state]:

        if get_q_value(state, nxt) == max_q:

            best_actions.append(nxt)

    return random.choice(best_actions)

# =========================================================
# REWARD FUNCTION
# =========================================================

def get_reward(current, next_state):

    if next_state == destination:

        return 150

    cx, cy = points[current]
    nx, ny = points[next_state]
    dx, dy = points[destination]

    current_distance = math.sqrt(
        (cx - dx) ** 2 +
        (cy - dy) ** 2
    )

    next_distance = math.sqrt(
        (nx - dx) ** 2 +
        (ny - dy) ** 2
    )

    if next_distance < current_distance:

        return 15

    return -10

# =========================================================
# TRAIN RL
# =========================================================

print("\nTRAINING RL AGENT...")

for episode in range(200):

    current_state = start

    total_reward = 0

    for step in range(50):

        action = choose_action(current_state)

        reward = get_reward(current_state, action)

        total_reward += reward

        old_q = get_q_value(
            current_state,
            action
        )

        future_qs = []

        for nxt in neighbors[action]:

            future_qs.append(
                get_q_value(action, nxt)
            )

        max_future_q = max(future_qs) if future_qs else 0

        # Q LEARNING UPDATE

        new_q = old_q + LEARNING_RATE * (

            reward +
            DISCOUNT * max_future_q -
            old_q
        )

        set_q_value(
            current_state,
            action,
            new_q
        )

        print(
            f"[{exploration_mode}] "
            f"{current_state}->{action} | "
            f"Reward={reward} | "
            f"Q={round(new_q,2)}"
        )

        current_state = action

        if current_state == destination:

            break

    episode_rewards.append(total_reward)

print("\nTRAINING COMPLETE!")

# =========================================================
# CREATE BEST PATH
# =========================================================

path_nodes = []

current = start

visited = set()

while current != destination:

    visited.add(current)

    best_next = None

    best_q = -999999

    for nxt in neighbors[current]:

        q = get_q_value(current, nxt)

        if q > best_q and nxt not in visited:

            best_q = q
            best_next = nxt

    if best_next is None:

        break

    path_nodes.append(best_next)

    current = best_next

path = []

for node in path_nodes:

    path.append(points[node])

# =========================================================
# MAIN CAR
# =========================================================

car_x, car_y = points[start]

car_speed = 3

car_angle = 0

# =========================================================
# MORE TRAFFIC SIGNALS
# =========================================================

signals = []

for vx in vertical_roads:

    for hy in horizontal_roads:

        signals.append({

            "x": vx,
            "y": hy,

            "state": random.choice([
                "RED",
                "GREEN"
            ]),

            "timer": random.randint(0, 200),

            "duration": random.randint(180, 420)
        })

# =========================================================
# TRAFFIC VEHICLES
# =========================================================

traffic_vehicles = []

for y in horizontal_roads:

    for i in range(6):

        traffic_vehicles.append({

            "x": random.randint(0, WIDTH),

            "y": y - 25,

            "speed": random.randint(2, 5),

            "direction": "horizontal",

            "color": random.choice([
                RED,
                BLUE,
                GREEN,
                YELLOW,
                (255,120,0),
                (180,0,255)
            ])
        })

for x in vertical_roads:

    for i in range(6):

        traffic_vehicles.append({

            "x": x + 25,

            "y": random.randint(0, HEIGHT),

            "speed": random.randint(2, 5),

            "direction": "vertical",

            "color": random.choice([
                RED,
                BLUE,
                GREEN,
                YELLOW,
                (255,120,0),
                (180,0,255)
            ])
        })

# =========================================================
# DRAW BUILDINGS
# =========================================================

def draw_buildings():

    buildings = [

        (40, 40, 120, 80, "SHOP"),
        (350, 40, 150, 80, "MALL"),
        (650, 40, 120, 80, "HOTEL"),
        (1280, 40, 180, 80, "HOSPITAL"),

        (40, 800, 150, 90, "BANK"),
        (350, 800, 160, 90, "OFFICE"),
        (650, 800, 140, 90, "MARKET"),
        (1250, 800, 200, 90, "APARTMENT")
    ]

    for b in buildings:

        x, y, w, h, name = b

        pygame.draw.rect(
            screen,
            GRAY,
            (x, y, w, h),
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            BLACK,
            (x, y, w, h),
            3,
            border_radius=10
        )

        # WINDOWS
        for wx in range(x + 10, x + w - 20, 30):

            for wy in range(y + 10, y + h - 20, 25):

                pygame.draw.rect(
                    screen,
                    WINDOW_COLOR,
                    (wx, wy, 15, 15)
                )

        text = font.render(
            name,
            True,
            BLACK
        )

        screen.blit(
            text,
            (x + 15, y + h//2 - 10)
        )

# =========================================================
# DRAW CITY
# =========================================================

def draw_city():

    screen.fill(GRASS)

    # ROADS
    for y in horizontal_roads:

        pygame.draw.rect(
            screen,
            ROAD,
            (
                50,
                y - ROAD_WIDTH // 2,
                1500,
                ROAD_WIDTH
            )
        )

        pygame.draw.rect(
            screen,
            ROAD_BORDER,
            (
                50,
                y - ROAD_WIDTH // 2,
                1500,
                ROAD_WIDTH
            ),
            4
        )

    for x in vertical_roads:

        pygame.draw.rect(
            screen,
            ROAD,
            (
                x - ROAD_WIDTH // 2,
                50,
                ROAD_WIDTH,
                850
            )
        )

        pygame.draw.rect(
            screen,
            ROAD_BORDER,
            (
                x - ROAD_WIDTH // 2,
                50,
                ROAD_WIDTH,
                850
            ),
            4
        )

    # LANE MARKINGS
    for y in horizontal_roads:

        for x in range(50, 1550, 60):

            pygame.draw.line(
                screen,
                WHITE,
                (x, y),
                (x + 30, y),
                5
            )

    for x in vertical_roads:

        for y in range(50, 900, 60):

            pygame.draw.line(
                screen,
                WHITE,
                (x, y),
                (x, y + 30),
                5
            )

# =========================================================
# DRAW SIGNALS
# =========================================================

def draw_signals():

    for signal in signals:

        pygame.draw.rect(
            screen,
            BLACK,
            (
                signal["x"] - 8,
                signal["y"] - 70,
                16,
                50
            )
        )

        pygame.draw.circle(
            screen,
            RED if signal["state"] == "RED"
            else (80,0,0),

            (
                signal["x"],
                signal["y"] - 55
            ),

            7
        )

        pygame.draw.circle(
            screen,
            GREEN if signal["state"] == "GREEN"
            else (0,80,0),

            (
                signal["x"],
                signal["y"] - 35
            ),

            7
        )

# =========================================================
# UPDATE SIGNALS
# =========================================================

def update_signals():

    for signal in signals:

        signal["timer"] += 1

        if signal["timer"] > signal["duration"]:

            signal["timer"] = 0

            signal["duration"] = random.randint(
                180,
                420
            )

            if signal["state"] == "GREEN":

                signal["state"] = "RED"

            else:

                signal["state"] = "GREEN"

# =========================================================
# DRAW REALISTIC VEHICLES
# =========================================================

def draw_traffic():

    for vehicle in traffic_vehicles:

        surface = pygame.Surface(
            (50, 24),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            surface,
            vehicle["color"],
            (0, 0, 50, 24),
            border_radius=8
        )

        pygame.draw.rect(
            surface,
            WINDOW_COLOR,
            (12, 5, 24, 12),
            border_radius=4
        )

        pygame.draw.circle(surface, BLACK, (10,22), 4)
        pygame.draw.circle(surface, BLACK, (40,22), 4)

        if vehicle["direction"] == "vertical":

            surface = pygame.transform.rotate(
                surface,
                -90
            )

        screen.blit(
            surface,
            (
                vehicle["x"],
                vehicle["y"]
            )
        )

# =========================================================
# MOVE TRAFFIC
# =========================================================

def move_traffic():

    for vehicle in traffic_vehicles:

        stop_vehicle = False

        for signal in signals:

            if signal["state"] == "RED":

                # HORIZONTAL
                if vehicle["direction"] == "horizontal":

                    distance_x = signal["x"] - vehicle["x"]

                    same_lane = abs(
                        vehicle["y"] - (signal["y"] - 25)
                    ) < 35

                    if 0 < distance_x < 90 and same_lane:

                        stop_vehicle = True

                # VERTICAL
                else:

                    distance_y = signal["y"] - vehicle["y"]

                    same_lane = abs(
                        vehicle["x"] - (signal["x"] + 25)
                    ) < 35

                    if 0 < distance_y < 90 and same_lane:

                        stop_vehicle = True

        if not stop_vehicle:

            if vehicle["direction"] == "horizontal":

                vehicle["x"] += vehicle["speed"]

                if vehicle["x"] > WIDTH + 100:

                    vehicle["x"] = -100

            else:

                vehicle["y"] += vehicle["speed"]

                if vehicle["y"] > HEIGHT + 100:

                    vehicle["y"] = -100

# =========================================================
# MAIN CAR SIGNAL STOP
# =========================================================

def stop_for_red_signal():

    for signal in signals:

        if signal["state"] == "RED":

            distance = math.sqrt(
                (car_x - signal["x"]) ** 2 +
                (car_y - signal["y"]) ** 2
            )

            if distance < 60:

                return True

    return False

# =========================================================
# DRAW MAIN RL TAXI
# =========================================================

def draw_main_car():

    taxi_surface = pygame.Surface(
        (65, 35),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        taxi_surface,
        (255,215,0),
        (0,0,65,35),
        border_radius=10
    )

    pygame.draw.rect(
        taxi_surface,
        WINDOW_COLOR,
        (15,8,32,15),
        border_radius=4
    )

    pygame.draw.circle(
        taxi_surface,
        BLACK,
        (12,32),
        5
    )

    pygame.draw.circle(
        taxi_surface,
        BLACK,
        (52,32),
        5
    )

    text = pygame.font.SysFont(
        "arial",
        13,
        bold=True
    ).render(
        "RL TAXI",
        True,
        BLACK
    )

    taxi_surface.blit(text, (10, 10))

    rotated = pygame.transform.rotate(
        taxi_surface,
        -car_angle
    )

    rect = rotated.get_rect(
        center=(car_x, car_y)
    )

    screen.blit(
        rotated,
        rect.topleft
    )

# =========================================================
# MOVE MAIN CAR
# =========================================================

def move_car():

    global car_x
    global car_y
    global car_angle
    global path

    if len(path) == 0:

        return

    if stop_for_red_signal():

        return

    tx, ty = path[0]

    dx = tx - car_x
    dy = ty - car_y

    distance = math.sqrt(
        dx * dx +
        dy * dy
    )

    if distance > 3:

        car_x += (
            dx / distance
        ) * car_speed

        car_y += (
            dy / distance
        ) * car_speed

        car_angle = math.degrees(
            math.atan2(-dy, dx)
        )

    else:

        path.pop(0)

# =========================================================
# DRAW PATH
# =========================================================

def draw_path():

    if len(path) == 0:

        return

    current_pos = (car_x, car_y)

    for p in path:

        pygame.draw.line(
            screen,
            BLUE,
            current_pos,
            p,
            5
        )

        current_pos = p

# =========================================================
# MAIN LOOP
# =========================================================

running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()
            sys.exit()

    move_car()

    move_traffic()

    update_signals()

    draw_city()

    draw_buildings()

    draw_path()

    draw_traffic()

    draw_signals()

    draw_main_car()

    pygame.display.update()
