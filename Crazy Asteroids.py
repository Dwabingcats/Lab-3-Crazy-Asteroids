import asyncio  # Added for browser compatibility
import random
import sys
import pygame

# 1. Initialize Pygame
pygame.init()

# 3. Create the Canvas
WINDOW_HEIGHT = 700
WINDOW_WIDTH = 1400
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Asteroid game")
clock = pygame.time.Clock()


# 4. Color Definitions (RGB Format)
BACKGROUND_COLOR = (30, 30, 40)

# --- INITIALIZE GAME VARIABLES OUTSIDE THE LOOP ---
asteroid_img = pygame.image.load("assets/asteroid.jpeg")
asteroid_img = pygame.transform.scale(asteroid_img, (60, 60))
spaceship = pygame.image.load("assets/spaceship.png")
spaceship = pygame.transform.scale(spaceship, (50, 50))

angle = 0
spaceship_x = 500
spaceship_y = 500
SHIP_SPEED = 0

NUM_ASTEROIDS = 6
positions = []
velocities = []
radii = []
masses = []
asteroid_imgs = []


bullets = []
bullet_speed = 10


for i in range(NUM_ASTEROIDS):
    r = random.randint(20, 40)
    radii.append(r)
    masses.append(r**2)
    x = random.randint(r, WINDOW_WIDTH - r * 2)
    y = random.randint(r, WINDOW_HEIGHT - r * 2)
    positions.append(pygame.math.Vector2(x, y))
    velocities.append(
        pygame.math.Vector2(
            random.choice([-1, 1]) * random.randint(1, 3),
            random.choice([-1, 1]) * random.randint(1, 3),
        )
    )
    asteroid_imgs.append(pygame.transform.scale(asteroid_img, (r * 2, r * 2)))


async def main():
    global angle, bullets, bullet_speed, SHIP_SPEED
    position = pygame.math.Vector2(spaceship_x, spaceship_y)
    running = True

    shoot_cooldown = 0  # Added to prevent spawning 60 bullets/sec

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player_rect = pygame.Rect(position.x - 25, position.y - 25, 50, 50)

        for i in range(len(positions)):
            positions[i] += velocities[i]
            if (
                positions[i].x < 0
                or positions[i].x > WINDOW_WIDTH - radii[i] * 2
            ):
                velocities[i].x *= -1
            if (
                positions[i].y < 0
                or positions[i].y > WINDOW_HEIGHT - radii[i] * 2
            ):
                velocities[i].y *= -1

        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                c1 = positions[i] + pygame.math.Vector2(radii[i], radii[i])
                c2 = positions[j] + pygame.math.Vector2(radii[j], radii[j])

                if c1.distance_to(c2) < radii[i] + radii[j]:
                    normal = (c1 - c2).normalize()
                    positions[i] += normal
                    positions[j] -= normal
                    v1 = velocities[i].dot(normal)
                    v2 = velocities[j].dot(normal)
                    m1, m2 = masses[i], masses[j]
                    new_v1 = (v1 * (m1 - m2) + 2 * m2 * v2) / (m1 + m2)
                    new_v2 = (v2 * (m2 - m1) + 2 * m1 * v1) / (m1 + m2)
                    velocities[i] += normal * (new_v1 - v1)
                    velocities[j] += normal * (new_v2 - v2)

            asteroid_rect = pygame.Rect(
                positions[i].x, positions[i].y, radii[i] * 2, radii[i] * 2
            )
            if player_rect.colliderect(asteroid_rect):
                print("Collision detected!")
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            angle += 3
        if keys[pygame.K_RIGHT]:
            angle -= 3

        forward = pygame.math.Vector2(1, 0).rotate(-angle + 270)
        backward = pygame.math.Vector2(1, 0).rotate(-angle + 90)

        if keys[pygame.K_UP]:
            SHIP_SPEED += 1
        if keys[pygame.K_DOWN]:
            SHIP_SPEED -= 1
        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        if keys[pygame.K_SPACE] and shoot_cooldown == 0:
            bullets.append(
                [
                    pygame.math.Vector2(position.x, position.y),
                    pygame.math.Vector2(forward),
                ]
            )
            shoot_cooldown = 12  # Delay frames between shots

        position += forward * SHIP_SPEED
        SHIP_SPEED *= 0.98
        position.x %= WINDOW_WIDTH
        position.y %= WINDOW_HEIGHT

        # Clear screen with background color
        screen.fill(BACKGROUND_COLOR)

        for i in range(len(positions)):
            screen.blit(asteroid_imgs[i], (positions[i].x, positions[i].y))

        #spaceship
        rotated_ship = pygame.transform.rotate(spaceship, angle)
        ship_rect = rotated_ship.get_rect(center=(position.x, position.y))
        screen.blit(rotated_ship, ship_rect.topleft)


        for b in bullets[:]:
            b[0] += b[1] * bullet_speed
            pygame.draw.circle(
                screen, (255, 0, 0), (int(b[0].x), int(b[0].y)), 3
            )
            if (
                b[0].x < 0
                or b[0].x > WINDOW_WIDTH
                or b[0].y < 0
                or b[0].y > WINDOW_HEIGHT
            ):
                bullets.remove(b)


        for b in bullets[:]:
            bullet_rect = pygame.Rect(b[0].x - 2, b[0].y - 2, 4, 4)
            for i in range(len(positions) - 1, -1, -1):
                ast_rect = pygame.Rect(
                    positions[i].x, positions[i].y, radii[i] * 2, radii[i] * 2
                )

                if bullet_rect.colliderect(ast_rect):
                    if b in bullets:
                        bullets.remove(b)

                    # Remove hit asteroid
                    positions.pop(i)
                    velocities.pop(i)
                    radii.pop(i)
                    masses.pop(i)
                    asteroid_imgs.pop(i)
                    break

        # Render changes onto the screen
        pygame.display.flip()

        clock.tick(60)  # Controls game speed (60 frames per second)
        await asyncio.sleep(0)  # CRITICAL: Web loop pause

    pygame.quit()
    sys.exit()


asyncio.run(main())