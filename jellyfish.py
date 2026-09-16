import pygame
import math


class Jellyfish:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)

        self.size = 80
        self.orientation = 0

        self.time = 0
        self.contraction = 0
        self.contraction_speed = 3

    def update(self, dt):
        self.time += dt

        self.contraction = (
            1 - math.cos(self.time * self.contraction_speed)
        ) / 2

        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt

    def draw(self, screen):

        x = self.position.x
        y = self.position.y

        # -------------------------
        # Bell
        # -------------------------

        bell_width = self.size * (1 - 0.25 * self.contraction)
        bell_height = self.size * 0.65 * (1 + 0.15 * self.contraction)

        points = []

        # Upper curved portion
        for i in range(21):
            angle = math.pi + (math.pi * i / 20)

            px = x + (bell_width / 2) * math.cos(angle)
            py = y + (bell_height / 2) * math.sin(angle)

            points.append((px, py))

        # Bottom edge of the bell
        points.append((x + bell_width / 2, y))
        points.append((x - bell_width / 2, y))

        pygame.draw.polygon(
            screen,
            (120, 190, 240),
            points
        )

        # Bell outline
        pygame.draw.lines(
            screen,
            (180, 225, 255),
            False,
            points,
            2
        )

        # -------------------------
        # Tentacles
        # -------------------------

        tentacle_count = 7

        for i in range(tentacle_count):

            # Spread tentacles across the bell
            start_x = (
                x
                - bell_width / 2
                + (bell_width / (tentacle_count - 1)) * i
            )

            start_y = y

            # Slight variation in length
            length = (55 + 10 * math.sin(i)) * (1 - 0.20 * self.contraction)

            points = []

            # Create a slightly wavy tentacle
            segments = 12

            for j in range(segments + 1):

                t = j / segments

                px = start_x + 8 * math.sin(t * math.pi * 2 + i)
                py = start_y + length * t

                points.append((px, py))

            pygame.draw.lines(
                screen,
                (150, 210, 255),
                False,
                points,
                3
            )