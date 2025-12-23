import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Screen
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Falling Objects Deluxe + High Score")

# Colors
BG_COLOR = (0, 0, 20)
PLAYER_COLOR = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)
OBJECT_TYPES = {
    "red": {"color": (255, 0, 0), "points": 1, "speed": 5},
    "blue": {"color": (0, 0, 255), "points": 3, "speed": 4},
    "green": {"color": (0, 255, 0), "points": 5, "speed": 3}
}
POWERUP_TYPES = {
    "double": {"color": (255, 105, 180)},
    "speed": {"color": (0, 255, 255)}
}

# Clock
clock = pygame.time.Clock()
FPS = 60

# Font
font = pygame.font.SysFont("Arial", 24)

# Player
player_width = 60
player_height = 30
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_speed = 7
normal_speed = player_speed

# Falling objects
objects = []
object_width = 40
object_height = 30
spawn_event = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_event, 700)

# Power-ups
powerups = []
powerup_width = 30
powerup_height = 30
powerup_spawn_event = pygame.USEREVENT + 2
pygame.time.set_timer(powerup_spawn_event, 10000)
double_points_active = False
speed_boost_active = False
powerup_timer = 0
powerup_duration = 5000

# Particles
particles = []

# Stars
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)] for _ in range(50)]

# Score
score = 0
highscore_file = "highscore.txt"

# Load high score
if os.path.exists(highscore_file):
    with open(highscore_file, "r") as f:
        try:
            high_score = int(f.read())
        except:
            high_score = 0
else:
    high_score = 0

# Draw player
def draw_player(x, y):
    pygame.draw.rect(screen, PLAYER_COLOR, (x, y, player_width, player_height))

# Draw objects
def draw_objects():
    for obj in objects:
        pygame.draw.rect(screen, OBJECT_TYPES[obj["type"]]["color"], obj["rect"])

# Draw power-ups
def draw_powerups():
    for pu in powerups:
        pygame.draw.rect(screen, POWERUP_TYPES[pu["type"]]["color"], pu["rect"])

# Draw stars
def draw_stars():
    screen.fill(BG_COLOR)
    for star in stars:
        pygame.draw.circle(screen, (255,255,255), (star[0], star[1]), star[2])
        star[1] += 1
        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = 0
            star[2] = random.randint(1, 3)

# Particle effects
def create_particles(x, y, color):
    for _ in range(15):
        particles.append({"x": x, "y": y, "vx": random.uniform(-2,2), "vy": random.uniform(-2,2), "color": color, "life": random.randint(20,40)})

def draw_particles():
    for p in particles[:]:
        pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), 3)
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1
        if p["life"] <= 0:
            particles.remove(p)

# Game over
def game_over():
    global score, high_score
    if score > high_score:
        high_score = score
        with open(highscore_file, "w") as f:
            f.write(str(high_score))
    over_text = font.render(f"Game Over! Score: {score} | High Score: {high_score}", True, TEXT_COLOR)
    screen.blit(over_text, [WIDTH//6, HEIGHT//2])
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

# Main loop
def main():
    global player_x, objects, score, powerups
    global double_points_active, speed_boost_active, powerup_timer, player_speed
    running = True
    difficulty_timer = pygame.time.get_ticks()

    while running:
        draw_stars()
        current_time = pygame.time.get_ticks()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == spawn_event:
                obj_type = random.choice(list(OBJECT_TYPES.keys()))
                x = random.randint(0, WIDTH - object_width)
                y = -object_height
                obj_rect = pygame.Rect(x, y, object_width, object_height)
                objects.append({"rect": obj_rect, "type": obj_type})
            if event.type == powerup_spawn_event:
                pu_type = random.choice(list(POWERUP_TYPES.keys()))
                x = random.randint(0, WIDTH - powerup_width)
                y = -powerup_height
                pu_rect = pygame.Rect(x, y, powerup_width, powerup_height)
                powerups.append({"rect": pu_rect, "type": pu_type})

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x - player_speed > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x + player_speed + player_width < WIDTH:
            player_x += player_speed

        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

        # Move objects
        for obj in objects[:]:
            obj["rect"].y += OBJECT_TYPES[obj["type"]]["speed"]
            if obj["rect"].colliderect(player_rect):
                gained = OBJECT_TYPES[obj["type"]]["points"]
                if double_points_active:
                    gained *= 2
                score += gained
                create_particles(obj["rect"].centerx, obj["rect"].centery, OBJECT_TYPES[obj["type"]]["color"])
                objects.remove(obj)
            elif obj["rect"].top > HEIGHT:
                game_over()

        # Move power-ups
        for pu in powerups[:]:
            pu["rect"].y += 3
            if pu["rect"].colliderect(player_rect):
                if pu["type"] == "double":
                    double_points_active = True
                    powerup_timer = current_time
                elif pu["type"] == "speed":
                    speed_boost_active = True
                    powerup_timer = current_time
                    player_speed = normal_speed * 2
                create_particles(pu["rect"].centerx, pu["rect"].centery, POWERUP_TYPES[pu["type"]]["color"])
                powerups.remove(pu)
            elif pu["rect"].top > HEIGHT:
                powerups.remove(pu)

        # Check power-up durations
        if double_points_active and current_time - powerup_timer > powerup_duration:
            double_points_active = False
        if speed_boost_active and current_time - powerup_timer > powerup_duration:
            speed_boost_active = False
            player_speed = normal_speed

        # Increase difficulty every 10 seconds
        if current_time - difficulty_timer > 10000:
            for obj_type in OBJECT_TYPES:
                OBJECT_TYPES[obj_type]["speed"] += 1
            difficulty_timer = current_time

        # Draw everything
        draw_player(player_x, player_y)
        draw_objects()
        draw_powerups()
        draw_particles()

        # Draw score and high score
        score_text = font.render(f"Score: {score} | High Score: {high_score}", True, TEXT_COLOR)
        screen.blit(score_text, [10, 10])
        if double_points_active:
            dp_text = font.render("Double Points!", True, (255,105,180))
            screen.blit(dp_text, [10, 40])
        if speed_boost_active:
            sp_text = font.render("Speed Boost!", True, (0,255,255))
            screen.blit(sp_text, [10, 70])

        pygame.display.update()
        clock.tick(FPS)

main()


