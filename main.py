import asyncio  # Added for browser compatibility
import random
import pygame

# 1. Initialize Pygame
pygame.init()

# 3. Create the Canvas
WIDTH, HEIGHT = 1400, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroid game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 80)

# 4. Color Definitions (RGB Format)
BACKGROUND_COLOR = (30, 30, 40)

# --- INITIALIZE GAME VARIABLES OUTSIDE THE LOOP ---
asteroid_img = pygame.image.load("assets/asteroid.jpeg")
spaceship = pygame.transform.scale(pygame.image.load("assets/spaceship.png"), (50, 50))

NUM_ASTEROIDS = 6
BULLET_SPEED = 10
SHIP_RADIUS = 20
START = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)


def make_asteroids():
    asteroids = []
    while len(asteroids) < NUM_ASTEROIDS:
        r = random.randint(20, 40)
        pos = pygame.math.Vector2(random.randint(r, WIDTH - r), random.randint(r, HEIGHT - r))
        if pos.distance_to(START) < 200:
            continue
        vel = pygame.math.Vector2(
            random.choice([-1, 1]) * random.randint(1, 3),
            random.choice([-1, 1]) * random.randint(1, 3),
        )
        img = pygame.transform.scale(asteroid_img, (r * 2, r * 2))
        asteroids.append({"pos": pos, "vel": vel, "r": r, "img": img})
    return asteroids


def move_asteroids(asteroids):
    for a in asteroids:
        a["pos"] += a["vel"]
        if a["pos"].x < a["r"]:
            a["vel"].x = abs(a["vel"].x)
        if a["pos"].x > WIDTH - a["r"]:
            a["vel"].x = -abs(a["vel"].x)
        if a["pos"].y < a["r"]:
            a["vel"].y = abs(a["vel"].y)
        if a["pos"].y > HEIGHT - a["r"]:
            a["vel"].y = -abs(a["vel"].y)

    for i in range(len(asteroids)):
        for j in range(i + 1, len(asteroids)):
            a, b = asteroids[i], asteroids[j]
            distance = a["pos"].distance_to(b["pos"])
            if 0 < distance < a["r"] + b["r"]:
                normal = (a["pos"] - b["pos"]).normalize()
                a["pos"] += normal
                b["pos"] -= normal
                m1, m2 = a["r"] ** 2, b["r"] ** 2
                v1, v2 = a["vel"].dot(normal), b["vel"].dot(normal)
                a["vel"] += normal * ((v1 * (m1 - m2) + 2 * m2 * v2) / (m1 + m2) - v1)
                b["vel"] += normal * ((v2 * (m2 - m1) + 2 * m1 * v1) / (m1 + m2) - v2)


def draw_message(text, color):
    for line, y_offset in [(text, -40), ("Press R to play again", 40)]:
        surface = font.render(line, True, color)
        screen.blit(surface, surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 + y_offset)))


async def main():
    while True:
        asteroids = make_asteroids()
        bullets = []
        position = pygame.math.Vector2(START)
        angle = 0
        speed = 0
        shoot_cooldown = 0  # Added to prevent spawning 60 bullets/sec
        state = "playing"

        restart = False
        while not restart:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            keys = pygame.key.get_pressed()

            if state == "playing":
                if keys[pygame.K_LEFT]:
                    angle += 3
                if keys[pygame.K_RIGHT]:
                    angle -= 3
                if keys[pygame.K_UP]:
                    speed += 1
                if keys[pygame.K_DOWN]:
                    speed -= 1

                forward = pygame.math.Vector2(0, -1).rotate(-angle)
                position += forward * speed
                speed *= 0.98
                position.x %= WIDTH
                position.y %= HEIGHT

                shoot_cooldown = max(0, shoot_cooldown - 1)
                if keys[pygame.K_SPACE] and shoot_cooldown == 0:
                    bullets.append([pygame.math.Vector2(position), forward * BULLET_SPEED])
                    shoot_cooldown = 12  # Delay frames between shots

                move_asteroids(asteroids)

                for b in bullets[:]:
                    b[0] += b[1]
                    if not (0 <= b[0].x <= WIDTH and 0 <= b[0].y <= HEIGHT):
                        bullets.remove(b)
                        continue
                    for a in asteroids:
                        if b[0].distance_to(a["pos"]) < a["r"]:
                            # Remove hit asteroid
                            asteroids.remove(a)
                            bullets.remove(b)
                            break

                if not asteroids:
                    state = "won"
                for a in asteroids:
                    if position.distance_to(a["pos"]) < a["r"] + SHIP_RADIUS:
                        state = "lost"

            elif keys[pygame.K_r]:
                restart = True

            # Clear screen with background color
            screen.fill(BACKGROUND_COLOR)

            for a in asteroids:
                screen.blit(a["img"], (a["pos"].x - a["r"], a["pos"].y - a["r"]))
            for b in bullets:
                pygame.draw.circle(screen, (255, 0, 0), (int(b[0].x), int(b[0].y)), 3)

            #spaceship
            rotated_ship = pygame.transform.rotate(spaceship, angle)
            screen.blit(rotated_ship, rotated_ship.get_rect(center=(position.x, position.y)))

            if state == "won":
                draw_message("You win!", (80, 220, 120))
            elif state == "lost":
                draw_message("Game over", (230, 80, 80))

            # Render changes onto the screen
            pygame.display.flip()

            clock.tick(60)  # Controls game speed (60 frames per second)
            await asyncio.sleep(0)  # CRITICAL: Web loop pause


asyncio.run(main())