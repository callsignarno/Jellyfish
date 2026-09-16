import pygame
from jellyfish import Jellyfish

pygame.init()

# -------------------------
# Window configuration
# -------------------------

WIDTH = 1200
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jellyfish Deep-Sea Neural Simulation")

# -------------------------
# Simulation configuration
# -------------------------

clock = pygame.time.Clock()
FPS = 60

running = True
paused = False

# Font for simulation information
font = pygame.font.Font(None, 28)

# Create the jellyfish
jellyfish = Jellyfish(WIDTH // 2, HEIGHT // 2)

# -------------------------
# Deep-sea particles
# -------------------------

import random

particles = []

for _ in range(100):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.randint(1, 2)

    particles.append((x, y, size))


# -------------------------
# Main simulation loop
# -------------------------

while running:

    # Handle events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            # Space = pause/unpause
            if event.key == pygame.K_SPACE:
                paused = not paused

            # R = reset
            elif event.key == pygame.K_r:
                paused = False

    # -------------------------
    # Update simulation
    # -------------------------

    if not paused:
        jellyfish.update(1 / FPS)

    # -------------------------
    # Draw
    # -------------------------

    # Deep-sea background
    screen.fill((5, 10, 25))

    # Draw deep-sea particles
    for x, y, size in particles:
        pygame.draw.circle(screen, (40, 50, 70), (x, y), size)

    # Draw the jellyfish
    jellyfish.draw(screen)

    # Simulation status
    status = "PAUSED" if paused else "RUNNING"

    status_text = font.render(
        f"Simulation: {status}",
        True,
        (200, 220, 255)
    )

    fps_text = font.render(
        f"FPS: {clock.get_fps():.1f}",
        True,
        (200, 220, 255)
    )

    screen.blit(status_text, (20, 20))
    screen.blit(fps_text, (20, 50))

    # Update display
    pygame.display.flip()

    # Maintain target FPS
    clock.tick(FPS)


# -------------------------
# Shutdown
# -------------------------

pygame.quit()