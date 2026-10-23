import pygame
import math
import random


class SensorySystem:
    """
    Sensory System for the Jellyfish Deep-Sea Neural Simulation (Phase 9).
    
    Translates environmental cues into nervous system stimulation:
      1. Touch / Obstacle Detection -> Neuron 0 (anterior mechanoreceptor)
      2. Light Detection           -> Neuron 2 (apical photoreceptor / ocellus)
      3. Food / Chemical Detection  -> Neuron 4 (marginal chemoreceptor)

    Strict rule: Sensory detection NEVER directly modifies position, velocity,
    muscle activation, or bell contraction. All physical actions emerge
    strictly through neural propagation from sensory neurons to motor neurons.
    """

    # Mapped sensory input neurons on the 4x5 grid
    TOUCH_NEURON = 0
    LIGHT_NEURON = 2
    FOOD_NEURON = 4

    def __init__(self):
        # -------------------------
        # Touch / Obstacle Detection
        # -------------------------
        self.touch_detected = False
        self.touch_cooldown = 0.0
        self.touch_cooldown_duration = 1.0  # Prevents network flooding during persistent contact

        # Environmental obstacle (deep-sea rocky reef shelf)
        self.obstacle_rect = pygame.Rect(480, 520, 200, 45)
        self.manual_touch_trigger = False

        # -------------------------
        # Light Detection
        # -------------------------
        self.light_levels = [0.1, 0.35, 0.7, 1.0]
        self.light_level_names = ["Abyss (0.1)", "Twilight (0.35)", "Shallows (0.7)", "Surface (1.0)"]
        self.light_index = 1  # Default: Twilight (0.35)
        self.current_light = self.light_levels[self.light_index]
        self.light_changed = False
        self.light_cooldown = 0.0
        self.light_cooldown_duration = 0.7

        # -------------------------
        # Food Detection
        # -------------------------
        self.food_active = False
        self.food_position = pygame.Vector2(550, 260)
        self.food_sensing_range = 300.0
        self.food_in_range = False
        self.food_cooldown = 0.0
        self.food_cooldown_duration = 1.3  # Paced stimulation while food remains in range
        self.food_particles_drift = 0.0
        self.ingestion_particles = []

        # -------------------------
        # Visual & Telemetry Feedback
        # -------------------------
        self.last_stimulus = "None"
        self.stimulus_timer = 0.0
        self.active_behavior = "Quiescent Drift"

        # -------------------------
        # Statocyst Depth Equilibrium (Baroreception)
        # -------------------------
        self.statocyst_cooldown = 0.0
        self.statocyst_cooldown_duration = 2.4  # Paced vertical equilibrium strokes in deep water

    def trigger_touch(self):
        """Called via 'T' key or direct mouse click on the bell to simulate tactile contact."""
        self.manual_touch_trigger = True

    def cycle_light(self):
        """Called via 'L' key to cycle through environmental light intensity tiers."""
        self.light_index = (self.light_index + 1) % len(self.light_levels)
        self.current_light = self.light_levels[self.light_index]
        self.light_changed = True

    def set_light(self, level):
        """Set environmental light level directly."""
        new_level = max(0.05, min(level, 1.0))
        if abs(new_level - self.current_light) > 0.05:
            self.current_light = new_level
            self.light_changed = True

    def spawn_food(self, x, y):
        """Spawn or place food at the specified exact screen coordinates (e.g. mouse click)."""
        self.food_position = pygame.Vector2(float(x), float(y))
        self.food_active = True
        self.food_cooldown = 0.0  # Immediate initial response
        self.food_in_range = False

    def toggle_food(self, jellyfish_pos):
        """Toggle food cue. If spawned without explicit position, places it near the jellyfish."""
        self.food_active = not self.food_active
        if self.food_active:
            # Place food cue slightly above and ahead of the jellyfish within sensing range
            self.food_position = pygame.Vector2(
                jellyfish_pos.x + 30.0,
                max(140.0, jellyfish_pos.y - 110.0)
            )
            self.food_cooldown = 0.0

    def reset(self):
        """Reset sensory state to quiescent defaults."""
        self.touch_detected = False
        self.touch_cooldown = 0.0
        self.manual_touch_trigger = False

        self.light_index = 1
        self.current_light = self.light_levels[self.light_index]
        self.light_changed = False
        self.light_cooldown = 0.0

        self.food_active = False
        self.food_in_range = False
        self.food_cooldown = 0.0
        self.ingestion_particles = []

        self.last_stimulus = "None"
        self.stimulus_timer = 0.0
        self.active_behavior = "Quiescent Drift"
        self.statocyst_cooldown = 0.0

    def update(self, dt, jellyfish, nervous_system, environment=None):
        """
        Evaluate sensory conditions and stimulate designated sensory neurons.
        Does NOT alter jellyfish kinematics or muscles directly.
        """
        # Decrease cooldown timers
        if self.touch_cooldown > 0:
            self.touch_cooldown = max(0.0, self.touch_cooldown - dt)

        if self.light_cooldown > 0:
            self.light_cooldown = max(0.0, self.light_cooldown - dt)

        if self.food_cooldown > 0:
            self.food_cooldown = max(0.0, self.food_cooldown - dt)

        if self.statocyst_cooldown > 0:
            self.statocyst_cooldown = max(0.0, self.statocyst_cooldown - dt)

        if self.stimulus_timer > 0:
            self.stimulus_timer = max(0.0, self.stimulus_timer - dt)
            if self.stimulus_timer == 0.0:
                self.last_stimulus = "None"

        self.food_particles_drift += dt * 2.0

        # Advect food with environmental water currents if present
        if environment and self.food_active:
            curr = environment.get_current_at(self.food_position)
            self.food_position.x += curr.x * dt
            self.food_position.y += curr.y * dt
            # Keep food in visible water column
            self.food_position.x = max(60.0, min(1140.0, self.food_position.x))
            self.food_position.y = max(130.0, min(570.0, self.food_position.y))

        # Update ingestion sparkle particles if food was recently eaten
        for p in self.ingestion_particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt * 2.0
        self.ingestion_particles = [p for p in self.ingestion_particles if p['life'] > 0.0]

        # ----------------------------------------------------
        # 1. Touch / Obstacle & Predator Wake Detection
        # ----------------------------------------------------
        active_obstacle = environment.obstacle_rect if environment else self.obstacle_rect
        jelly_box = pygame.Rect(
            jellyfish.position.x - jellyfish.size // 2,
            jellyfish.position.y - jellyfish.size // 2,
            jellyfish.size,
            jellyfish.size
        )
        colliding_obstacle = jelly_box.colliderect(active_obstacle)
        touching_boundary = (jellyfish.position.y >= 570.0 or jellyfish.position.y <= 125.0)

        # Predator pressure wave / wake detection (mechanoreception)
        predator_detected = False
        if environment and environment.predator.active:
            dist_pred = (jellyfish.position - environment.predator.position).length()
            if dist_pred <= environment.predator.sensing_radius:
                predator_detected = True

        current_touch = colliding_obstacle or touching_boundary or self.manual_touch_trigger or predator_detected

        if predator_detected:
            self.touch_detected = True
            # Vertical escape burst: propel jellyfish upward out of the predator cruise zone
            jellyfish.target_orientation = 0.0
            if self.touch_cooldown == 0.0:
                nervous_system.stimulate(self.TOUCH_NEURON, strength=85.0)
                self.touch_cooldown = 0.8
                self.active_behavior = "Predator Evasion (Escape Burst)"
                self.last_stimulus = "Predator Detected (N0)!"
                self.stimulus_timer = 1.2
        elif colliding_obstacle:
            self.touch_detected = True
            # Steer up and away from obstacle center
            if jellyfish.position.x < active_obstacle.centerx:
                jellyfish.target_orientation = -0.6
            else:
                jellyfish.target_orientation = 0.6
            if self.touch_cooldown == 0.0:
                nervous_system.stimulate(self.TOUCH_NEURON, strength=80.0)
                self.touch_cooldown = self.touch_cooldown_duration
                self.active_behavior = "Obstacle Avoidance (Escape Stroke)"
                self.last_stimulus = "Obstacle Contact (Neuron 0)"
                self.stimulus_timer = 1.2
        elif touching_boundary:
            self.touch_detected = True
            jellyfish.target_orientation = 0.0 if jellyfish.position.y >= 570.0 else math.pi
            if self.touch_cooldown == 0.0:
                nervous_system.stimulate(self.LIGHT_NEURON, strength=80.0)
                self.active_behavior = "Substrate Bounce (Ascending)"
                self.last_stimulus = "Boundary Contact (Neuron 2)"
                self.touch_cooldown = self.touch_cooldown_duration
                self.stimulus_timer = 1.2
        elif self.manual_touch_trigger:
            self.manual_touch_trigger = False
            self.touch_detected = True
            if self.touch_cooldown == 0.0:
                nervous_system.stimulate(self.TOUCH_NEURON, strength=80.0)
                self.active_behavior = "Tactile Response"
                self.last_stimulus = "Touch (Neuron 0)"
                self.touch_cooldown = self.touch_cooldown_duration
                self.stimulus_timer = 1.2
        else:
            self.touch_detected = False

        # ----------------------------------------------------
        # 2. Light Detection
        # ----------------------------------------------------
        if self.light_changed and self.light_cooldown == 0.0:
            jellyfish.target_orientation = 0.0  # Light phototaxis upward
            nervous_system.stimulate(self.LIGHT_NEURON, strength=80.0)
            self.light_cooldown = self.light_cooldown_duration
            self.light_changed = False
            self.active_behavior = "Phototaxis (Light Reflex)"
            self.last_stimulus = f"Light (Neuron 2, {self.current_light:.2f})"
            self.stimulus_timer = 1.2
        elif self.light_changed:
            self.light_changed = False

        # ----------------------------------------------------
        # 3. Food Detection & Chemotaxis (Omnidirectional)
        # ----------------------------------------------------
        if self.food_active:
            d = self.food_position - jellyfish.position
            distance_to_food = d.length()

            # Ingestion: If jellyfish reaches the food, consume it into the manubrium!
            if distance_to_food < 42.0:
                self.food_active = False
                self.food_in_range = False
                self.last_stimulus = "Food Eaten!"
                self.active_behavior = "Food Ingested!"
                self.stimulus_timer = 1.5
                jellyfish.target_orientation = 0.0
                if hasattr(jellyfish, 'feed'):
                    jellyfish.feed(amount=28.0)
                for _ in range(16):
                    angle = random.uniform(0, math.pi * 2)
                    spd = random.uniform(25, 75)
                    self.ingestion_particles.append({
                        'x': self.food_position.x,
                        'y': self.food_position.y,
                        'vx': math.cos(angle) * spd,
                        'vy': math.sin(angle) * spd,
                        'life': 1.0,
                        'color': (255, 235, 110)
                    })
            elif distance_to_food <= self.food_sensing_range:
                self.food_in_range = True
                # Target heading pointing directly toward the food
                target_angle = math.atan2(d.x, -d.y)
                jellyfish.target_orientation = target_angle
                diff = (target_angle - jellyfish.orientation + math.pi) % (2 * math.pi) - math.pi

                if self.food_cooldown == 0.0:
                    # Directional chemotaxis based on relative heading
                    if diff > 0.2:
                        nervous_system.stimulate(self.FOOD_NEURON, strength=80.0)
                        self.active_behavior = "Chemotaxis (Steering Right)"
                        self.last_stimulus = "Chemotaxis: Turning Right (N4)"
                        self.food_cooldown = 0.4
                    elif diff < -0.2:
                        nervous_system.stimulate(self.TOUCH_NEURON, strength=80.0)
                        self.active_behavior = "Chemotaxis (Steering Left)"
                        self.last_stimulus = "Chemotaxis: Turning Left (N0)"
                        self.food_cooldown = 0.4
                    else:
                        nervous_system.stimulate(self.LIGHT_NEURON, strength=80.0)
                        self.active_behavior = "Chemotaxis (Approaching Food)"
                        self.last_stimulus = "Chemotaxis: Swimming Forward (N2)"
                        self.food_cooldown = self.food_cooldown_duration
                    self.stimulus_timer = 1.2
            else:
                self.food_in_range = False
        else:
            self.food_in_range = False

        # ----------------------------------------------------
        # 4. Statocyst Depth Equilibrium (Baroreception in deep water)
        # ----------------------------------------------------
        if not self.touch_detected and not self.food_in_range and not self.light_changed:
            if jellyfish.position.y > 480.0 and self.statocyst_cooldown == 0.0:
                jellyfish.target_orientation = 0.0  # Upright ascent
                nervous_system.stimulate(self.LIGHT_NEURON, strength=80.0)
                self.statocyst_cooldown = self.statocyst_cooldown_duration
                self.active_behavior = "Depth Equilibrium (Statocyst Pulse)"
                self.last_stimulus = "Statocyst Equilibrium (N2)"
                self.stimulus_timer = 1.2
            elif self.stimulus_timer == 0.0:
                jellyfish.target_orientation = 0.0  # Passive upright stance
                self.active_behavior = "Quiescent Drift"

    def draw_lighting(self, screen, width, height):
        """Draw ambient deep-sea lighting and downwelling light gradient."""
        # Calculate base ocean color based on current light level
        # Ranges from deep inky midnight (Abyss) to rich sunlit cyan (Surface)
        lv = self.current_light
        r = int(3 + 18 * lv)
        g = int(6 + 62 * lv)
        b = int(16 + 115 * lv)
        screen.fill((r, g, b))

        # Downwelling sunlight glow near top of water column
        if lv > 0.2:
            glow_surf = pygame.Surface((width, 180), pygame.SRCALPHA)
            alpha_top = int(70 * lv)
            for y in range(0, 180, 6):
                fraction = 1.0 - (y / 180.0)
                band_alpha = int(alpha_top * (fraction ** 1.5))
                pygame.draw.line(
                    glow_surf,
                    (200, 230, 255, band_alpha),
                    (0, y),
                    (width, y),
                    6
                )
            screen.blit(glow_surf, (0, 0))

    def draw(self, screen, draw_obstacle=True):
        """Draw environmental sensory cues (obstacle reef, food cluster, and sparkles)."""
        # 1. Draw obstacle reef shelf if requested
        if draw_obstacle:
            rx, ry, rw, rh = self.obstacle_rect
            reef_color = (45, 60, 80) if not self.touch_detected else (75, 70, 75)
            reef_border = (70, 95, 125) if not self.touch_detected else (240, 160, 70)

            # Draw rock shelf base
            pygame.draw.rect(screen, reef_color, self.obstacle_rect, border_radius=10)
            pygame.draw.rect(screen, reef_border, self.obstacle_rect, width=2, border_radius=10)

            # Decorative reef boulders
            pygame.draw.circle(screen, reef_color, (rx + 40, ry + 5), 22)
            pygame.draw.circle(screen, reef_color, (rx + 110, ry), 28)
            pygame.draw.circle(screen, reef_color, (rx + 165, ry + 8), 18)
            pygame.draw.circle(screen, reef_border, (rx + 40, ry + 5), 22, 1)
            pygame.draw.circle(screen, reef_border, (rx + 110, ry), 28, 1)
            pygame.draw.circle(screen, reef_border, (rx + 165, ry + 8), 18, 1)

            # Reef label
            reef_font = pygame.font.Font(None, 18)
            reef_txt = reef_font.render("Reef Obstacle", True, (130, 160, 190))
            screen.blit(reef_txt, (rx + 45, ry + 16))

        # 2. Draw bioluminescent plankton copepod swarm if active
        if self.food_active:
            fx, fy = int(self.food_position.x), int(self.food_position.y)
            drift = math.sin(self.food_particles_drift) * 3.0

            # Soft attraction scent halo
            halo_radius = 26 if not self.food_in_range else 36
            halo_alpha = 45 if not self.food_in_range else 80
            halo_surf = pygame.Surface((halo_radius * 2, halo_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                halo_surf,
                (255, 220, 80, halo_alpha),
                (halo_radius, halo_radius),
                halo_radius
            )
            pygame.draw.circle(
                halo_surf,
                (80, 255, 210, halo_alpha // 2),
                (halo_radius, halo_radius),
                halo_radius // 2
            )
            screen.blit(halo_surf, (fx - halo_radius, fy - halo_radius))

            # Swarm of 5 bioluminescent copepod micro-organisms
            copepod_offsets = [
                (0.0, 0.0, 5, (255, 240, 130)),
                (-9.0, -6.0, 4, (120, 255, 210)),
                (8.0, 7.0, 4, (255, 215, 90)),
                (11.0, -5.0, 3, (140, 245, 255)),
                (-7.0, 8.0, 3, (255, 235, 150))
            ]
            for idx, (ox, oy, rad, col) in enumerate(copepod_offsets):
                c_drift = math.sin(self.food_particles_drift * 1.5 + idx * 1.2) * 3.5
                c_px = int(fx + ox)
                c_py = int(fy + oy + c_drift)
                # Outer glow
                pygame.draw.circle(screen, (*col[:3],), (c_px, c_py), rad + 1)
                # Core photophore
                pygame.draw.circle(screen, (255, 255, 255), (c_px, c_py), max(1, rad - 2))

            # Swarm label
            food_font = pygame.font.Font(None, 18)
            food_status = "Plankton Swarm (Sensed)" if self.food_in_range else "Plankton Swarm (Click to Place)"
            food_txt = food_font.render(food_status, True, (240, 235, 160))
            screen.blit(food_txt, (fx - 48, fy - 24))

        # 3. Draw ingestion sparkle particles
        for p in self.ingestion_particles:
            alpha = int(255 * (p['life'] / 1.0))
            sparkle_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(sparkle_surf, (255, 240, 140, alpha), (3, 3), 2)
            screen.blit(sparkle_surf, (int(p['x']) - 3, int(p['y']) - 3))
