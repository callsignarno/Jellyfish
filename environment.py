import pygame
import math
import random


class DeepSeaPredator:
    """
    Apex Deep-Sea Viperfish (*Chauliodus sloani*).
    Cruises through the ocean depth and can be detected by the jellyfish's
    mechanoreceptors and ocelli, triggering an escape reflex.
    """
    def __init__(self):
        self.active = False
        self.position = pygame.Vector2(-120.0, 350.0)
        self.velocity = pygame.Vector2(0.0, 0.0)
        self.speed = 110.0
        self.direction = 1  # 1 = left-to-right, -1 = right-to-left
        self.base_y = 350.0
        self.time = 0.0
        self.sensing_radius = 175.0
        self.body_length = 68.0

    def spawn(self, target_y=350.0, direction=1):
        """Spawn the predator to cruise through the scene near target_y."""
        self.active = True
        self.direction = direction
        self.base_y = float(target_y)
        self.position.y = float(target_y)
        self.position.x = -80.0 if direction > 0 else 1280.0
        self.velocity.x = self.speed * direction
        self.time = 0.0

    def update(self, dt):
        if not self.active:
            return

        self.time += dt
        self.position.x += self.velocity.x * dt
        # Sinuous undulating deep-sea cruising movement
        self.position.y = self.base_y + 16.0 * math.sin(self.time * 2.8)

        # Deactivate when swimming off screen
        if (self.direction > 0 and self.position.x > 1320.0) or \
           (self.direction < 0 and self.position.x < -120.0):
            self.active = False

    def draw(self, screen):
        if not self.active:
            return

        px = int(self.position.x)
        py = int(self.position.y)
        d = self.direction

        # Sinuous body undulation along length
        wave_tail = math.sin(self.time * 4.5) * 4.0

        # Streamlined predatory viperfish silhouette
        body_pts = [
            (px + 38 * d, py),                      # Jaws / Snout
            (px + 24 * d, py - 12),                 # Cranial crest
            (px - 12 * d, py - 8),                  # Dorsal ridge
            (px - 34 * d, py - 3 + wave_tail),      # Caudal peduncle
            (px - 46 * d, py - 13 + wave_tail * 1.5),# Upper tail fluke
            (px - 40 * d, py + wave_tail),          # Tail notch
            (px - 46 * d, py + 13 + wave_tail * 1.5),# Lower tail fluke
            (px - 34 * d, py + 3 + wave_tail),      # Lower caudal
            (px - 10 * d, py + 9),                  # Belly
            (px + 20 * d, py + 8),                  # Gular throat
        ]
        pygame.draw.polygon(screen, (16, 26, 38), body_pts)
        pygame.draw.lines(screen, (45, 70, 98), True, body_pts, 2)

        # Bioluminescent lateral line photophores (blue glowing dots)
        for i in range(6):
            gx = px - 18 * d + i * 7 * d
            gy = py + 2 + int(wave_tail * (1.0 - i / 6.0))
            pygame.draw.circle(screen, (100, 230, 255), (gx, gy), 2)
            pygame.draw.circle(screen, (220, 255, 255), (gx, gy), 1)

        # Predatory glowing amber eye
        eye_x = px + 24 * d
        eye_y = py - 4
        pygame.draw.circle(screen, (255, 65, 35), (eye_x, eye_y), 4)
        pygame.draw.circle(screen, (255, 230, 100), (eye_x, eye_y), 2)

        # Sinuous Photophore Lure on dorsal filament
        lure_w = math.sin(self.time * 3.5) * 6.0
        lure_x = px + 46 * d
        lure_y = py - 14 + int(lure_w)
        pygame.draw.line(screen, (55, 85, 115), (px + 26 * d, py - 9), (lure_x, lure_y), 2)
        pygame.draw.circle(screen, (90, 255, 215), (lure_x, lure_y), 3)
        pygame.draw.circle(screen, (255, 255, 255), (lure_x, lure_y), 1)

        # Tag
        font = pygame.font.Font(None, 18)
        lbl = font.render("Apex Predator (Viperfish)", True, (245, 120, 100))
        screen.blit(lbl, (px - 45, py - 28))


class BackgroundCtenophore:
    """
    Bioluminescent Comb Jelly (*Beroe cucumis*) drifting passively in deep distance.
    Provides depth and living ecosystem atmosphere with iridescent rainbow cilia comb rows.
    """
    def __init__(self, x, y, spd):
        self.x = x
        self.y = y
        self.spd = spd
        self.time = random.uniform(0, math.pi * 2)
        self.size = random.uniform(16.0, 22.0)

    def update(self, dt, current):
        self.time += dt
        self.x += (self.spd + current.x * 0.25) * dt
        self.y += math.sin(self.time * 0.7) * 4.0 * dt
        if self.x > 1250:
            self.x = -60
            self.y = random.uniform(160, 480)

    def draw(self, screen):
        ix = int(self.x)
        iy = int(self.y)
        w = int(self.size)
        h = int(self.size * 1.5)

        # Translucent gelatinous ovoid
        c_surf = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(c_surf, (50, 120, 180, 50), (w // 2, h // 2, w, h))
        pygame.draw.ellipse(c_surf, (140, 210, 255, 80), (w // 2, h // 2, w, h), 1)

        # 4 Ctene comb rows refracting iridescent light
        for cr in range(4):
            frac = (cr + 0.5) / 4.0
            rx = int(w // 2 + w * (0.2 + 0.6 * frac))
            ry1 = h // 2 + 3
            ry2 = h // 2 + h - 3
            # Rainbow phase
            rb_phase = (self.time * 3.0 + cr) % 3.0
            if rb_phase < 1.0:
                col = (60, 240, 200, 120)
            elif rb_phase < 2.0:
                col = (100, 180, 255, 120)
            else:
                col = (240, 140, 255, 120)
            pygame.draw.line(c_surf, col, (rx, ry1), (rx, ry2), 1)

        screen.blit(c_surf, (ix - w, iy - h))


class Environment:
    """
    Simulated Deep-Sea Environment with Living Benthic Ecosystem.
    
    Models:
      - Epipelagic to Bathypelagic Depth, Hydrostatic Pressure & Thermocline
      - Fluid water currents (Calm, Eastward, Westward, Tidal Swell)
      - Volumetric caustic sunbeams downwelling from the twilight zone
      - 3-Layer Parallax Marine Snow (background, midground, foreground)
      - Hydrothermal Vent with convective rising mineral ash particles
      - Bioluminescent Benthic Sea-Pens swaying on the seafloor
      - Ambient Background Ctenophores (comb jellies)
      - Seafloor Reef Shelf and Apex Viperfish Predator
    """
    def __init__(self, width=1200, height=700):
        self.width = width
        self.height = height
        self.time = 0.0

        # Reference Depth Bounds
        self.surface_y = 120.0
        self.seabed_y = 580.0

        # Current Modes
        self.current_modes = [
            "Calm (0 px/s)",
            "Eastward (+22 px/s)",
            "Westward (-22 px/s)",
            "Tidal Swell"
        ]
        self.current_mode_index = 0
        self.current_vector = pygame.Vector2(0.0, 0.0)

        # -------------------------
        # 3-Layer Parallax Marine Snow Particles
        # -------------------------
        self.particles = []
        # Layer 0: Distant tiny snow (80 particles)
        for _ in range(80):
            self.particles.append({
                'x': random.uniform(0, width),
                'y': random.uniform(0, height),
                'size': 1,
                'layer': 0,
                'sink_speed': random.uniform(4.0, 8.0),
                'alpha': random.randint(40, 75)
            })
        # Layer 1: Midground snow (70 particles)
        for _ in range(70):
            self.particles.append({
                'x': random.uniform(0, width),
                'y': random.uniform(0, height),
                'size': 2,
                'layer': 1,
                'sink_speed': random.uniform(8.0, 15.0),
                'alpha': random.randint(80, 140)
            })
        # Layer 2: Foreground glowing organic aggregates (25 particles)
        for _ in range(25):
            self.particles.append({
                'x': random.uniform(0, width),
                'y': random.uniform(0, height),
                'size': 3,
                'layer': 2,
                'sink_speed': random.uniform(14.0, 22.0),
                'alpha': random.randint(150, 220)
            })

        # -------------------------
        # Hydrothermal Vent Smoke Particles
        # -------------------------
        self.vent_particles = []

        # -------------------------
        # Living Benthic Sea-Pens / Polyps on Seafloor
        # -------------------------
        self.sea_pens = [
            {'x': 340, 'base_y': 635, 'height': 38, 'glow_phase': 0.0, 'color': (60, 235, 210)},
            {'x': 420, 'base_y': 625, 'height': 48, 'glow_phase': 1.5, 'color': (90, 195, 255)},
            {'x': 750, 'base_y': 622, 'height': 42, 'glow_phase': 3.0, 'color': (140, 230, 255)},
            {'x': 840, 'base_y': 618, 'height': 52, 'glow_phase': 4.2, 'color': (65, 245, 185)},
            {'x': 980, 'base_y': 626, 'height': 36, 'glow_phase': 2.1, 'color': (120, 210, 255)}
        ]

        # -------------------------
        # Distant Background Comb Jellies (Ctenophores)
        # -------------------------
        self.ctenophores = [
            BackgroundCtenophore(240, 220, spd=8.0),
            BackgroundCtenophore(780, 380, spd=12.0)
        ]

        # -------------------------
        # Obstacle & Predator
        # -------------------------
        self.obstacle_rect = pygame.Rect(480, 520, 200, 45)
        self.predator = DeepSeaPredator()

    def cycle_current(self):
        """Cycle environmental current modes (Key 'C')."""
        self.current_mode_index = (self.current_mode_index + 1) % len(self.current_modes)

    def trigger_predator(self, target_y=350.0):
        """Spawn a predator pass (Key 'P')."""
        direction = 1 if random.random() > 0.5 else -1
        self.predator.spawn(target_y=target_y, direction=direction)

    def get_current_at(self, pos):
        """Calculate fluid velocity vector at a given position."""
        if self.current_mode_index == 1:
            return pygame.Vector2(22.0, 0.0)
        elif self.current_mode_index == 2:
            return pygame.Vector2(-22.0, 0.0)
        elif self.current_mode_index == 3:
            vx = 26.0 * math.sin(self.time * 0.75 + pos.y * 0.004)
            vy = 5.0 * math.cos(self.time * 0.5)
            return pygame.Vector2(vx, vy)
        return pygame.Vector2(0.0, 0.0)

    def get_conditions_at(self, pos):
        """
        Calculate depth, pressure, temperature, and darkness at a given position.
        """
        norm_depth = max(0.0, min(1.0, (pos.y - self.surface_y) / (self.seabed_y - self.surface_y)))
        depth_m = 200.0 + norm_depth * 2800.0
        pressure_atm = 1.0 + (depth_m / 10.0)
        temp_c = 20.0 - 16.0 * math.sqrt(norm_depth)
        darkness = 0.15 + 0.85 * norm_depth

        return {
            'depth_m': depth_m,
            'pressure_atm': pressure_atm,
            'temp_c': temp_c,
            'norm_depth': norm_depth,
            'darkness': darkness
        }

    def reset(self):
        self.current_mode_index = 0
        self.time = 0.0
        self.predator.active = False
        self.vent_particles = []

    def update(self, dt):
        self.time += dt
        self.current_vector = self.get_current_at(pygame.Vector2(self.width / 2, self.height / 2))

        # Update 3-Layer Parallax Marine Snow
        for p in self.particles:
            curr = self.get_current_at(pygame.Vector2(p['x'], p['y']))
            # Layer depth scaling
            depth_scale = 0.4 if p['layer'] == 0 else (0.8 if p['layer'] == 1 else 1.2)

            p['x'] += curr.x * depth_scale * dt
            p['y'] += (curr.y * depth_scale + p['sink_speed']) * dt

            if p['x'] < 0:
                p['x'] += self.width
            elif p['x'] > self.width:
                p['x'] -= self.width

            if p['y'] > self.height:
                p['y'] = 0
                p['x'] = random.uniform(0, self.width)

        # Update Hydrothermal Vent convective particles
        # Vent orifice at (222, 560)
        if random.random() < 0.65:
            self.vent_particles.append({
                'x': 222 + random.uniform(-4, 4),
                'y': 560.0,
                'vx': random.uniform(-6, 6),
                'vy': random.uniform(-35, -55),
                'life': 1.0,
                'max_life': random.uniform(2.2, 3.5),
                'radius': random.uniform(2.0, 4.0)
            })

        for vp in self.vent_particles:
            curr = self.get_current_at(pygame.Vector2(vp['x'], vp['y']))
            vp['x'] += (vp['vx'] + curr.x * 0.4) * dt
            vp['y'] += vp['vy'] * dt
            vp['life'] -= dt / vp['max_life']
            vp['radius'] += dt * 3.0
            vp['vy'] *= max(0.0, 1.0 - 0.4 * dt)
        self.vent_particles = [vp for vp in self.vent_particles if vp['life'] > 0]

        # Update background ctenophores
        for ct in self.ctenophores:
            ct.update(dt, self.current_vector)

        # Update predator
        self.predator.update(dt)

    def draw_atmosphere(self, screen, light_val):
        """Draw ambient ocean water with volumetric caustic light shafts."""
        lv = max(0.05, min(1.0, light_val))
        r = int(3 + 18 * lv)
        g = int(6 + 62 * lv)
        b = int(16 + 115 * lv)
        screen.fill((r, g, b))

        # Volumetric downwelling sunbeams piercing through twilight water
        if lv > 0.15:
            beam_surf = pygame.Surface((self.width, 220), pygame.SRCALPHA)
            alpha_base = int(65 * lv)

            for b_idx in range(6):
                # Animated caustic sway
                sway = math.sin(self.time * 0.8 + b_idx * 1.1) * 35.0
                bx_top = 100 + b_idx * 190 + sway
                bx_bot = bx_top + 65 + sway * 0.5
                beam_pts = [
                    (bx_top - 30, 0),
                    (bx_top + 30, 0),
                    (bx_bot + 65, 210),
                    (bx_bot - 45, 210)
                ]
                pygame.draw.polygon(beam_surf, (200, 235, 255, int(alpha_base * 0.35)), beam_pts)

            # Surface ambient downwelling band
            for y in range(0, 180, 6):
                fraction = 1.0 - (y / 180.0)
                band_alpha = int(alpha_base * (fraction ** 1.6))
                pygame.draw.line(beam_surf, (190, 230, 255, band_alpha), (0, y), (self.width, y), 6)

            screen.blit(beam_surf, (0, 0))

        # Draw distant background ctenophores
        for ct in self.ctenophores:
            ct.draw(screen)

    def draw_terrain(self, screen):
        """Draw seafloor bathymetry, hydrothermal vent, sea-pens, and reef shelf."""
        # 1. Seafloor Bed with layered sediment strata
        seabed_poly = [
            (0, 630),
            (150, 620),
            (320, 635),
            (480, 615),
            (680, 625),
            (900, 615),
            (1050, 630),
            (1200, 620),
            (1200, 700),
            (0, 700)
        ]
        pygame.draw.polygon(screen, (14, 21, 31), seabed_poly)
        pygame.draw.lines(screen, (32, 48, 68), False, seabed_poly[:-2], 2)

        # Sediment highlight line
        for i in range(len(seabed_poly) - 3):
            p1 = seabed_poly[i]
            p2 = seabed_poly[i + 1]
            pygame.draw.line(screen, (22, 35, 52), (p1[0], p1[1] + 6), (p2[0], p2[1] + 6), 2)

        # 2. Living Benthic Sea-Pens / Polyps
        curr_sway = self.current_vector.x * 0.25
        for sp in self.sea_pens:
            bx = sp['x']
            by = sp['base_y']
            h = sp['height']
            sway = math.sin(self.time * 2.2 + sp['glow_phase']) * 5.0 + curr_sway

            # Feathered stalk
            stalk_pts = [
                (bx, by),
                (bx + sway * 0.5, by - h * 0.5),
                (bx + sway, by - h)
            ]
            pygame.draw.lines(screen, (30, 75, 95), False, stalk_pts, 2)

            # Plumed bioluminescent side fronds
            frond_count = 6
            glow_intensity = 0.5 + 0.5 * math.sin(self.time * 1.8 + sp['glow_phase'])
            p_col = (
                int(sp['color'][0] * glow_intensity),
                int(sp['color'][1] * glow_intensity),
                int(sp['color'][2] * glow_intensity)
            )

            for f in range(frond_count):
                ft = f / frond_count
                fx = bx + sway * ft
                fy = by - h * ft
                flen = (1.0 - ft * 0.3) * 8.0
                pygame.draw.line(screen, p_col, (fx, fy), (fx - flen, fy - 3), 1)
                pygame.draw.line(screen, p_col, (fx, fy), (fx + flen, fy - 3), 1)

            # Bioluminescent crown node
            tip_x = int(bx + sway)
            tip_y = int(by - h)
            pygame.draw.circle(screen, p_col, (tip_x, tip_y), 3)
            pygame.draw.circle(screen, (255, 255, 255), (tip_x, tip_y), 1)

        # 3. Hydrothermal Vent Chimney
        vent_pts = [
            (210, 625),
            (216, 560),
            (228, 560),
            (236, 625)
        ]
        pygame.draw.polygon(screen, (22, 28, 38), vent_pts)
        pygame.draw.lines(screen, (45, 60, 80), True, vent_pts, 2)
        # Mineral sulfide crust detail
        pygame.draw.line(screen, (65, 80, 100), (218, 570), (220, 615), 1)
        pygame.draw.line(screen, (55, 75, 95), (225, 565), (227, 618), 1)

        # 4. Draw Vent Convective Ash Plume Particles
        for vp in self.vent_particles:
            alpha = max(0, min(255, int(180 * vp['life'])))
            r = max(1, int(vp['radius']))
            px = int(vp['x'])
            py = int(vp['y'])
            # Dark hot mineral particle fading to ocean
            ash_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            # Glowing core when young, dark billow when older
            if vp['life'] > 0.7:
                pygame.draw.circle(ash_surf, (240, 130, 60, alpha), (r + 1, r + 1), r)
            else:
                pygame.draw.circle(ash_surf, (40, 55, 70, alpha), (r + 1, r + 1), r)
            screen.blit(ash_surf, (px - r - 1, py - r - 1))

        # 5. Reef Obstacle Shelf
        rx, ry, rw, rh = self.obstacle_rect
        pygame.draw.rect(screen, (36, 50, 70), self.obstacle_rect, border_radius=10)
        pygame.draw.rect(screen, (58, 85, 115), self.obstacle_rect, width=2, border_radius=10)

        # Decorative reef boulders
        pygame.draw.circle(screen, (36, 50, 70), (rx + 40, ry + 5), 22)
        pygame.draw.circle(screen, (36, 50, 70), (rx + 110, ry), 28)
        pygame.draw.circle(screen, (36, 50, 70), (rx + 165, ry + 8), 18)
        pygame.draw.circle(screen, (58, 85, 115), (rx + 40, ry + 5), 22, 1)
        pygame.draw.circle(screen, (58, 85, 115), (rx + 110, ry), 28, 1)
        pygame.draw.circle(screen, (58, 85, 115), (rx + 165, ry + 8), 18, 1)

        font = pygame.font.Font(None, 18)
        reef_txt = font.render("Reef Shelf (Obstacle)", True, (140, 175, 205))
        screen.blit(reef_txt, (rx + 40, ry + 16))

    def draw_particles(self, screen):
        """Draw 3-layer parallax drifting marine snow."""
        for p in self.particles:
            px = int(p['x'])
            py = int(p['y'])
            sz = p['size']
            alpha = p['alpha']

            if sz >= 3:
                # Glowing soft snowflake
                snow_s = pygame.Surface((sz * 2 + 2, sz * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(snow_s, (180, 225, 255, alpha), (sz + 1, sz + 1), sz)
                pygame.draw.circle(snow_s, (255, 255, 255, alpha // 2), (sz + 1, sz + 1), 1)
                screen.blit(snow_s, (px - sz - 1, py - sz - 1))
            else:
                pygame.draw.circle(screen, (75, 105, 140), (px, py), sz)

    def draw_predator(self, screen):
        """Draw apex predator if active."""
        self.predator.draw(screen)
