import pygame
import math
import random
from muscle import Muscle


class Jellyfish:
    """
    Biological Model of a Cnidarian Medusa (Jellyfish).
    
    Features:
      - 8 Coronal striated muscle sectors mapped to Motor Neurons 12-19
      - Elastic mesoglea passive spring recoil (Zero ATP bell re-expansion)
      - Toroidal vortex ring shedding upon propulsive power strokes
      - 8 Radial canals with bioluminescent neural wave illumination
      - 8 Marginal Rhopalia (decentralized pacemakers + statocysts + ocelli)
      - Frilly 4-lobed oral arms and trailing multi-segment hydrodynamic tentacles
      - Gastrovascular digestion with glowing nutrient circulation
      - Real-time biomechanical telemetry (Reynolds number, elastic strain, thrust impulse)
    """

    def __init__(self, x, y):
        # Kinematics and Position
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)

        # Anatomy Geometry & Heading
        self.size = 84
        self.orientation = 0.0
        self.target_orientation = 0.0

        # Bell Contraction State (strictly driven by coronal muscles)
        self.time = 0.0
        self.contraction = 0.0
        self.prev_contraction = 0.0

        # Eight coronal muscle regions around the subumbrella rim
        self.muscles = [Muscle() for _ in range(8)]

        # Bilateral lateral steering weights for the 8 coronal muscle regions
        # Symmetrically balanced to 0.0 on uniform contraction:
        # Left muscles (15, 16): -0.75, -0.75 (sum = -1.5)
        # Center muscles (12, 17): 0.0, 0.0
        # Right muscles (13, 14, 18, 19): +0.375 * 4 = +1.5
        self.lateral_muscle_weights = [0.0, 0.375, 0.375, -0.75, -0.75, 0.0, 0.375, 0.375]

        # Biological Metabolism & Gastric Ingestion
        self.energy = 85.0              # Metabolic ATP reservoir (0.0 to 100.0%)
        self.digesting_particles = []   # Food boluses digesting in gastric cavity
        self.wake_particles = []        # Toroidal vortex and fluid wake particles
        self.bioluminescence_glow = 0.0 # Dynamic bioluminescent flash intensity

        # Biomechanical Telemetry
        self.reynolds_number = 180.0    # Intermediate Re ~ 100 - 400
        self.instant_thrust_mn = 0.0    # Thrust impulse in milli-Newtons
        self.elastic_strain_pct = 0.0   # Mesoglea elastic deformation %

        # Multi-Segment Flexible Trailing Tentacles (8 tentacles, 14 nodes each)
        self.tentacle_count = 8
        self.tentacle_nodes = 14
        self.tentacles = []
        for i in range(self.tentacle_count):
            nodes = [pygame.Vector2(x, y + j * 6.0) for j in range(self.tentacle_nodes)]
            self.tentacles.append(nodes)

    def feed(self, amount=25.0):
        """Called when food/plankton is captured and ingested into the manubrium."""
        self.energy = min(100.0, self.energy + amount)
        self.bioluminescence_glow = 1.0
        # Spawn glowing digestion boluses inside the gastric cavity
        for _ in range(5):
            self.digesting_particles.append({
                'ox': random.uniform(-7, 7),
                'oy': random.uniform(-14, 2),
                'life': random.uniform(3.5, 5.5),
                'max_life': 5.5,
                'color': (255, 235, 95)
            })

    def update(self, dt, motor_activations, current_velocity=None):
        self.time += dt

        # Store previous contraction to measure rate of power stroke
        self.prev_contraction = self.contraction
        prev_m_contractions = [m.contraction for m in self.muscles]

        # Apply motor signals to the 8 coronal muscles
        for muscle, activation in zip(self.muscles, motor_activations):
            muscle.activate(activation)
            muscle.update(dt)

        # Average bell contraction ratio
        self.contraction = sum(m.contraction for m in self.muscles) / len(self.muscles)
        self.elastic_strain_pct = self.contraction * 100.0

        # Contraction transition generates the propulsive jet impulse
        contraction_delta = max(0.0, self.contraction - self.prev_contraction)
        self.instant_thrust_mn = (contraction_delta * 320.0) / max(0.001, dt)

        # Reorient smoothly toward target orientation (driven by rhopalia & statoliths)
        diff = (self.target_orientation - self.orientation + math.pi) % (2 * math.pi) - math.pi
        turn_rate = 4.8
        self.orientation += max(-turn_rate * dt, min(turn_rate * dt, diff * 4.8 * dt))
        self.orientation = (self.orientation + math.pi) % (2 * math.pi) - math.pi

        # Omnidirectional power stroke impulse in direction of bell heading
        hx = math.sin(self.orientation)
        hy = -math.cos(self.orientation)
        self.velocity.x += 220.0 * contraction_delta * hx
        self.velocity.y += 220.0 * contraction_delta * hy

        # Lateral differential slip thrust from asymmetrical coronal muscle contraction
        lateral_delta = sum(
            w * max(0.0, m.contraction - prev_c)
            for w, m, prev_c in zip(self.lateral_muscle_weights, self.muscles, prev_m_contractions)
        )
        self.velocity.x += 800.0 * lateral_delta * (-hy)
        self.velocity.y += 800.0 * lateral_delta * hx

        # Environmental fluid drag from ambient water currents
        if current_velocity:
            self.velocity.x += (current_velocity.x - self.velocity.x) * 1.2 * dt
            self.velocity.y += (current_velocity.y - self.velocity.y) * 0.6 * dt

        # Hydrodynamic damping and gentle neutral/negative buoyancy sink
        self.velocity.y += 15.0 * dt
        damping = max(0.0, 1.0 - 1.8 * dt)
        self.velocity.y *= damping
        self.velocity.x *= damping

        # Update position
        self.position += self.velocity * dt

        # Water column screen boundaries (window height 700)
        if self.position.y < 120:
            self.position.y = 120
            if self.velocity.y < 0:
                self.velocity.y = 0.0
        elif self.position.y > 580:
            self.position.y = 580
            if self.velocity.y > 0:
                self.velocity.y = 0.0

        if self.position.x < 100:
            self.position.x = 100
            if self.velocity.x < 0:
                self.velocity.x = 0.0
        elif self.position.x > 850:
            self.position.x = 850
            if self.velocity.x > 0:
                self.velocity.x = 0.0

        # Instantaneous Reynolds number (Re = rho * v * L / mu)
        # 100 px ~ 0.08 m (8 cm bell); v in m/s = spd * 0.0008
        spd_mps = self.velocity.length() * 0.0008
        char_len_m = 0.08
        self.reynolds_number = max(35.0, (1025.0 * spd_mps * char_len_m) / 0.0014)

        # -------------------------
        # Metabolism & Digestion Update
        # -------------------------
        if contraction_delta > 0.0:
            self.energy = max(10.0, self.energy - 0.4 * contraction_delta)
            self.bioluminescence_glow = min(1.0, self.bioluminescence_glow + 0.35)

        self.bioluminescence_glow = max(0.0, self.bioluminescence_glow - dt * 1.2)

        for p in self.digesting_particles:
            p['life'] -= dt
            self.energy = min(100.0, self.energy + 2.5 * dt)
        self.digesting_particles = [p for p in self.digesting_particles if p['life'] > 0]

        # -------------------------
        # Toroidal Vortex Rings & Fluid Wake
        # -------------------------
        if contraction_delta > 0.015:
            jet_dir = pygame.Vector2(-hx, -hy)
            bw = self.size * (1.0 - 0.25 * self.contraction)
            perp = pygame.Vector2(-hy, hx)

            # Emit two counter-rotating toroidal vortex rings from left and right bell rims
            for side, curl_dir in ((-1, -1), (1, 1)):
                rim_pos = self.position + perp * (bw * 0.45 * side)
                for _ in range(4):
                    spd_p = random.uniform(40.0, 110.0)
                    jitter = pygame.Vector2(random.uniform(-0.25, 0.25), random.uniform(-0.25, 0.25))
                    vel = (jet_dir + jitter).normalize() * spd_p
                    if current_velocity:
                        vel += current_velocity * 0.4

                    self.wake_particles.append({
                        'pos': pygame.Vector2(rim_pos.x, rim_pos.y),
                        'vel': vel,
                        'life': 1.0,
                        'max_life': random.uniform(0.7, 1.2),
                        'radius': random.uniform(2.5, 5.0),
                        'curl': curl_dir * random.uniform(2.5, 5.5),
                        'color': (50, 235, 255)
                    })

        # Update vortex wake particles with rotational curl dynamics
        for wp in self.wake_particles:
            # Swirling angular momentum curl
            if 'curl' in wp:
                tangent = pygame.Vector2(-wp['vel'].y, wp['vel'].x).normalize() if wp['vel'].length_squared() > 0 else pygame.Vector2(0, 0)
                wp['vel'] += tangent * (wp['curl'] * 12.0 * dt)
            wp['pos'] += wp['vel'] * dt
            wp['life'] -= dt / wp['max_life']
            wp['radius'] += dt * 3.5
            wp['vel'] *= max(0.0, 1.0 - 1.2 * dt)
        self.wake_particles = [wp for wp in self.wake_particles if wp['life'] > 0]

        # -------------------------
        # Update Multi-Segment Hydrodynamic Tentacles
        # -------------------------
        bw = self.size * (1.0 - 0.25 * self.contraction)
        cos_o = math.cos(self.orientation)
        sin_o = math.sin(self.orientation)

        for i, tentacle in enumerate(self.tentacles):
            # Anchor at scalloped margin rim
            local_anchor_x = -bw / 2 + (bw / (self.tentacle_count - 1)) * i
            local_anchor_y = 0.0
            root_x = self.position.x + local_anchor_x * cos_o - local_anchor_y * sin_o
            root_y = self.position.y + local_anchor_x * sin_o + local_anchor_y * cos_o

            tentacle[0] = pygame.Vector2(root_x, root_y)

            # Propagate physics down the chain with fluid drag & inertial lagging
            target_seg_len = 5.2 * (1.0 - 0.2 * self.contraction)
            for j in range(1, len(tentacle)):
                prev = tentacle[j - 1]
                curr = tentacle[j]

                # Fluid undulation wave
                wave = math.sin(self.time * 2.8 + i * 0.8 + j * 0.45) * 1.8
                perp_vec = pygame.Vector2(-sin_o, cos_o) * wave

                # Current advection
                c_drift = current_velocity * (0.35 * dt) if current_velocity else pygame.Vector2(0, 0)

                # Segment relaxation toward target distance
                desired = prev + pygame.Vector2(sin_o, -cos_o) * target_seg_len + perp_vec + c_drift
                curr += (desired - curr) * max(0.0, min(1.0, 16.0 * dt))

                # Constrain distance
                dist = (curr - prev).length()
                if dist > 0.001:
                    curr = prev + (curr - prev).normalize() * target_seg_len
                tentacle[j] = curr

    def draw(self, screen):
        x = self.position.x
        y = self.position.y

        cos_o = math.cos(self.orientation)
        sin_o = math.sin(self.orientation)

        def rotate_pt(px, py):
            dx = px - x
            dy = py - y
            return (x + dx * cos_o - dy * sin_o, y + dx * sin_o + dy * cos_o)

        # -------------------------
        # 1. Toroidal Vortex Rings & Fluid Wake
        # -------------------------
        for wp in self.wake_particles:
            alpha = max(0, min(255, int(190 * wp['life'])))
            r = max(1, int(wp['radius']))
            px = int(wp['pos'].x)
            py = int(wp['pos'].y)
            v_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(v_surf, (*wp['color'], alpha), (r + 2, r + 2), r)
            pygame.draw.circle(v_surf, (220, 255, 255, alpha // 2), (r + 2, r + 2), max(1, r // 2))
            screen.blit(v_surf, (px - r - 2, py - r - 2))

        # -------------------------
        # 2. Trailing Multi-Segment Hydrodynamic Tentacles
        # -------------------------
        for i, tentacle in enumerate(self.tentacles):
            pts = [(int(p.x), int(p.y)) for p in tentacle]
            if len(pts) > 1:
                # Soft outer bioluminescent glow
                pygame.draw.lines(screen, (75, 175, 235), False, pts, 3)
                # Fine inner crystal core
                pygame.draw.lines(screen, (210, 245, 255), False, pts, 1)

                # Glowing terminal photophore bead at tentacle tip
                tip = pts[-1]
                pygame.draw.circle(screen, (100, 255, 230), tip, 2)

        # -------------------------
        # 3. Layered Translucent Bell & Anatomical Structures
        # Rendered on local alpha surface with rotation
        # -------------------------
        canvas_size = 280
        surf = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
        cx, cy = canvas_size // 2, canvas_size // 2

        bell_width = self.size * (1.0 - 0.25 * self.contraction)
        bell_height = self.size * 0.68 * (1.0 + 0.16 * self.contraction)

        # Outer Exumbrella Dome Polygon (with scalloped marginal lappets)
        dome_pts = []
        lappet_count = 16
        for i in range(lappet_count * 2 + 1):
            t = i / (lappet_count * 2)
            angle = math.pi + math.pi * t
            # Subtle scalloped rim modulation
            scallop = 1.0 + 0.035 * math.sin(t * math.pi * 16)
            px = cx + (bell_width / 2) * math.cos(angle) * scallop
            py = cy + (bell_height / 2) * math.sin(angle) * scallop
            dome_pts.append((px, py))

        dome_pts.append((cx + bell_width / 2, cy))
        dome_pts.append((cx - bell_width / 2, cy))

        # A. Outer Translucent Exumbrella (Gelatinous Mesoglea)
        base_alpha = int(125 + 45 * self.bioluminescence_glow)
        pygame.draw.polygon(
            surf,
            (85, 175, 240, base_alpha),
            dome_pts
        )

        # Iridescent Exumbrella Crown Highlight
        crown_w = bell_width * 0.65
        crown_h = bell_height * 0.45
        crown_rect = pygame.Rect(cx - crown_w / 2, cy - bell_height * 0.52, crown_w, crown_h)
        pygame.draw.ellipse(surf, (180, 230, 255, 45), crown_rect)

        # B. Subumbrella Inner Cavity
        sub_w = bell_width * 0.82
        sub_h = bell_height * 0.78
        sub_pts = []
        for i in range(21):
            angle = math.pi + (math.pi * i / 20)
            sub_pts.append((cx + (sub_w / 2) * math.cos(angle), cy + (sub_h / 2) * math.sin(angle)))
        sub_pts.append((cx + sub_w / 2, cy))
        sub_pts.append((cx - sub_w / 2, cy))
        pygame.draw.polygon(surf, (55, 125, 195, 80), sub_pts)

        # Coronal Striated Ring Muscle Rim
        muscle_alpha = int(70 + 130 * self.contraction)
        muscle_pts = [
            (cx - bell_width * 0.45, cy),
            (cx + bell_width * 0.45, cy)
        ]
        pygame.draw.line(surf, (90, 235, 255, muscle_alpha), muscle_pts[0], muscle_pts[1], 3)

        # C. 8 Radial Canals & Marginal Rhopalia (Decentralized Pacemakers)
        apex_pt = (cx, cy - bell_height * 0.46)
        for k in range(8):
            k_angle = math.pi + (math.pi * (k + 0.5) / 8)
            rim_k = (cx + (bell_width * 0.48) * math.cos(k_angle), cy + (bell_height * 0.48) * math.sin(k_angle))

            # Biological coupling: Canal glows with active motor neuron signal
            m_act = self.muscles[k].contraction
            glow = max(0.12, max(m_act, self.bioluminescence_glow * 0.75))

            canal_color = (
                int(40 + 200 * glow),
                int(185 + 70 * glow),
                255,
                int(95 + 160 * glow)
            )
            pygame.draw.line(surf, canal_color, apex_pt, rim_k, 2 if glow < 0.4 else 3)

            # Marginal Rhopalium (Pacemaker + Statolith + Ocellus photophore)
            rhop_col = (45, 255, 220, int(160 + 95 * glow))
            pygame.draw.circle(surf, rhop_col, (int(rim_k[0]), int(rim_k[1])), 4)
            # Statolith crystal core
            pygame.draw.circle(surf, (255, 255, 255, 220), (int(rim_k[0]), int(rim_k[1])), 2)

        # D. Central Gastric Sac (Manubrium) & Glowing Nutrient Digestion
        stomach_top = cy - bell_height * 0.48
        stomach_bot = cy + bell_height * 0.12
        stomach_w = 15 * (1.0 - 0.2 * self.contraction)
        stomach_rect = pygame.Rect(cx - stomach_w / 2, stomach_top, stomach_w, stomach_bot - stomach_top)
        pygame.draw.ellipse(surf, (195, 235, 255, 145), stomach_rect)
        pygame.draw.ellipse(surf, (225, 250, 255, 210), stomach_rect, 1)

        # Digestion Boluses inside stomach
        for p in self.digesting_particles:
            life_ratio = p['life'] / p['max_life']
            d_alpha = int(230 * life_ratio)
            d_rad = max(1, int(3.5 * life_ratio))
            d_x = int(cx + p['ox'])
            d_y = int(cy - 8 + p['oy'])
            pygame.draw.circle(surf, (*p['color'], d_alpha), (d_x, d_y), d_rad)
            pygame.draw.circle(surf, (255, 255, 210, d_alpha // 2), (d_x, d_y), d_rad + 2)

        # E. Four Frilly Undulating Oral Arms
        for a_idx in range(4):
            arm_pts = []
            arm_offset = (a_idx - 1.5) * 4.8
            arm_len = bell_height * 0.58
            for s in range(10):
                st = s / 9.0
                ax = cx + arm_offset + 5.0 * math.sin(self.time * 3.2 + a_idx * 1.4 + st * math.pi * 1.5)
                ay = stomach_bot + arm_len * st
                arm_pts.append((ax, ay))
            pygame.draw.lines(surf, (195, 235, 255, 165), False, arm_pts, 2)
            # Ruffled fringe
            for pt in arm_pts[3:]:
                pygame.draw.circle(surf, (215, 245, 255, 130), (int(pt[0]), int(pt[1])), 2)

        # F. Exumbrella Rim & Marginal Ring Canal Outline
        pygame.draw.lines(
            surf,
            (195, 240, 255, int(195 + 60 * self.bioluminescence_glow)),
            False,
            dome_pts,
            2
        )

        # -------------------------
        # Rotate and Blit Bell onto Screen
        # -------------------------
        rotated_surf = pygame.transform.rotate(surf, -math.degrees(self.orientation))
        rect = rotated_surf.get_rect(center=(int(x), int(y)))
        screen.blit(rotated_surf, rect)
