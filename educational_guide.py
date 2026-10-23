import pygame
import math


class EducationalGuide:
    """
    Interactive Educational Field Guide & Anatomical Dissection System.
    
    Explains the evolutionary wonder of Cnidarian neurobiology:
    How jellyfish have survived for 500+ million years and perform complex
    locomotion, sensory orientation, and feeding without a brain.
    """

    TABS = [
        "1. NO BRAIN PARADIGM",
        "2. RHOPALIA & SENSORS",
        "3. NERVE NET WAVES",
        "4. VORTEX PROPULSION",
        "5. GASTROVASCULAR CAVITY"
    ]

    def __init__(self, width=1200, height=700):
        self.width = width
        self.height = height

        # Guide Modal State
        self.show_guide = False
        self.active_tab = 0

        # Anatomy Callouts Mode
        self.show_anatomy = False
        self.hovered_pin = None
        self.selected_pin = None

        # Simulation Time Dilation (for scientific observation)
        self.speed_modes = [1.0, 0.5, 0.25]
        self.speed_mode_index = 0
        self.time_scale = 1.0

        # Guided Interactive Lessons (1 to 5)
        self.active_lesson = None
        self.lesson_timer = 0.0
        self.lesson_banner = ""
        self.lesson_explanation = ""
        self.lesson_step = 0

        # Cached anatomical pin definitions (relative to jellyfish position and heading)
        # Each item: (id, name, local_offset_fn, category, summary, detail)
        self.pins_meta = [
            {
                'id': 'rhopalia',
                'name': 'Marginal Rhopalia (8x Pacemakers)',
                'offset': lambda sz, c: (sz * 0.46, -sz * 0.05),
                'category': 'DECENTRALIZED SENSORY HUB',
                'summary': 'Decentralized pacemakers + statocysts + ocelli around the rim.',
                'detail': 'Without a brain, jellyfish rely on 8 sensory rhopalia around the rim. '
                          'Each houses a microscopic calcium-carbonate statolith (gravity/tilt sensor), '
                          'rhopalial ocellus (photoreceptor), and pacemaker neurons that spontaneously '
                          'fire rhythmic action potentials. The fastest pacemaker entrains the bell!'
            },
            {
                'id': 'coronal_muscles',
                'name': 'Coronal Ring Muscles',
                'offset': lambda sz, c: (sz * 0.22, -sz * 0.18),
                'category': 'NEUROMUSCULAR EFFECTOR',
                'summary': 'Striated circular muscle bands driving the jet power stroke.',
                'detail': 'Striated coronal ring muscles directly beneath the subumbrella '
                          'receive inputs from the Motor Nerve Net (MNN). Synchronous firing '
                          'constricts bell diameter by up to 25%, ejecting water through the '
                          'aperture to propel the animal forward.'
            },
            {
                'id': 'mesoglea',
                'name': 'Exumbrella Mesoglea Dome',
                'offset': lambda sz, c: (0.0, -sz * 0.42),
                'category': 'PASSIVE ELASTIC SPRING',
                'summary': '95% water gelatinous matrix providing elastic spring recoil.',
                'detail': 'Jellyfish have NO antagonistic extensor muscles. Instead, '
                          'the thick collagenous mesoglea acts as an elastic spring: '
                          'active muscle contraction deforms the mesoglea, and stored elastic '
                          'strain energy automatically pops the bell back open for free (0 ATP)!'
            },
            {
                'id': 'radial_canals',
                'name': '8 Radial Canals',
                'offset': lambda sz, c: (-sz * 0.28, -sz * 0.22),
                'category': 'GASTROVASCULAR CIRCULATION',
                'summary': 'Combined digestive and circulatory distribution conduits.',
                'detail': 'Lacking blood vessels or a heart, jellyfish distribute digested nutrients '
                          'through 8 ciliated radial canals radiating outward from the stomach '
                          'to the marginal ring canal, directly feeding coronal muscles and rhopalia.'
            },
            {
                'id': 'manubrium',
                'name': 'Manubrium & Gastric Cavity',
                'offset': lambda sz, c: (0.0, -sz * 0.12),
                'category': 'CENTRAL DIGESTIVE STALK',
                'summary': 'Hanging digestive tube and nutrient absorption chamber.',
                'detail': 'The manubrium serves as mouth, stomach, and waste vent. Captured prey '
                          'is engulfed into the gastric cavity where digestive enzymes break down '
                          'copepods and zooplankton. Bioluminescent boluses glow as they digest.'
            },
            {
                'id': 'oral_arms',
                'name': 'Frilly Oral Arms (4x)',
                'offset': lambda sz, c: (sz * 0.14, sz * 0.22),
                'category': 'PREY CAPTURE & INGESTION',
                'summary': 'Ribbon-like feeding appendages transferring food to mouth.',
                'detail': 'Four undulating oral arms hang below the manubrium. Laden with stinging '
                          'nematocysts and sticky mucus cells, they snag swimming prey and guide '
                          'it directly into the oral aperture through ciliary currents.'
            },
            {
                'id': 'tentacles',
                'name': 'Marginal Tentacles',
                'offset': lambda sz, c: (-sz * 0.44, sz * 0.35),
                'category': 'MECHANORECEPTIVE PERIMETER',
                'summary': 'Fine sensory and defensive filaments trailing in fluid currents.',
                'detail': 'Flexible trailing tentacles sense physical contact, water currents, and '
                          'predator wakes. Mechanoreceptive tactile cues stimulate Neuron 0, '
                          'triggering a fast escape burst wave through the diffuse nerve net.'
            }
        ]

    def toggle_guide(self):
        """Toggle educational field guide modal."""
        self.show_guide = not self.show_guide

    def toggle_anatomy(self):
        """Toggle anatomical callout pins overlay."""
        self.show_anatomy = not self.show_anatomy

    def cycle_speed(self):
        """Cycle simulation time dilation (1.0x -> 0.5x -> 0.25x)."""
        self.speed_mode_index = (self.speed_mode_index + 1) % len(self.speed_modes)
        self.time_scale = self.speed_modes[self.speed_mode_index]
        return self.time_scale

    def start_lesson(self, lesson_id, jellyfish, nervous_system, sensory_system, environment):
        """
        Launch an interactive guided educational experiment.
        """
        self.active_lesson = lesson_id
        self.lesson_timer = 0.0
        self.lesson_step = 0

        # Temporarily slow time to 0.5x for clear observation
        self.time_scale = 0.5
        self.speed_mode_index = 1

        if lesson_id == 1:
            # Lesson 1: Rhopalial Pacemaker Pulse
            self.lesson_banner = "LESSON 1: THE DECENTRALIZED PACEMAKER PULSE"
            self.lesson_explanation = (
                "Watch the marginal Rhopalium (Pacemaker) fire an action potential. "
                "Notice how the wave sweeps through the Diffuse Nerve Net (DNN) into Motor Neurons 12-19, "
                "triggering a coordinated symmetrical bell contraction WITHOUT any brain command!"
            )
            # Stimulate sensory neuron to initiate clean forward wave
            nervous_system.stimulate(0, strength=85.0)

        elif lesson_id == 2:
            # Lesson 2: Statolith Gravity Righting Reflex
            self.lesson_banner = "LESSON 2: GRAVITATIONAL STATOLITH RIGHTING REFLEX"
            self.lesson_explanation = (
                "The jellyfish has been tilted 55°. Heavy calcium-carbonate STATOLITH crystals inside the "
                "rhopalia shift under gravity, pressing sensory hair cells. Unilateral muscle contractions "
                "generate differential steering thrust to upright the jellyfish automatically!"
            )
            jellyfish.orientation = 0.95  # Tilt bell to right
            jellyfish.target_orientation = 0.0
            # Stimulate right-side sensory neuron
            nervous_system.stimulate(4, strength=85.0)

        elif lesson_id == 3:
            # Lesson 3: Tactile Noxious Escape Burst
            self.lesson_banner = "LESSON 3: TACTILE AVOIDANCE & ESCAPE BURST"
            self.lesson_explanation = (
                "Simulating a mechanical collision! Mechanoreceptors on the bell margin trigger rapid "
                "depolarization of Neuron 0. A high-amplitude wave propagates across the coronal margin, "
                "generating an explosive escape jet impulse to evade the threat."
            )
            sensory_system.trigger_touch()

        elif lesson_id == 4:
            # Lesson 4: Chemotaxis & Gastric Digestion
            self.lesson_banner = "LESSON 4: CHEMOTAXIS & GASTROVASCULAR DIGESTION"
            self.lesson_explanation = (
                "Bioluminescent copepod plankton spawned ahead! Chemoreceptive neurons detect the food "
                "chemical plume. The jellyfish turns toward the scent, captures it into the manubrium, "
                "and glowing nutrient boluses diffuse through the 8 radial canals."
            )
            # Spawn food in front of jellyfish
            target_x = jellyfish.position.x + 85.0
            target_y = max(180.0, jellyfish.position.y - 120.0)
            sensory_system.spawn_food(target_x, target_y)

        elif lesson_id == 5:
            # Lesson 5: Patch-Clamp Electrophysiology
            self.lesson_banner = "LESSON 5: ELECTROPHYSIOLOGY & REFRACTORY GATING"
            self.lesson_explanation = (
                "Micro-electrode inserted! Watch the oscilloscope traces: CH1 (Sensory) spikes from -70 mV "
                "to +30 mV. The 0.15s refractory hyperpolarization prevents back-echo loops, ensuring clean "
                "forward-traveling waves. Notice the synaptic conduction delay to CH2 (Motor)!"
            )
            nervous_system.stimulate(0, strength=90.0)

    def update(self, dt, jellyfish, nervous_system, sensory_system, environment):
        """Update active lesson progression and timers."""
        if self.active_lesson is not None:
            self.lesson_timer += dt
            # Auto-conclude lesson after 7 seconds, returning to 1.0x speed
            if self.lesson_timer >= 7.0:
                self.active_lesson = None
                self.lesson_banner = ""
                self.lesson_explanation = ""
                self.time_scale = 1.0
                self.speed_mode_index = 0

    def handle_click(self, mx, my, jellyfish):
        """
        Check if user clicked an educational UI widget or anatomy pin.
        Returns True if the event was consumed.
        """
        # 1. Guide Modal interaction
        if self.show_guide:
            # Modal bounding box (centered)
            mw, mh = 880, 520
            mx_start = (self.width - mw) // 2
            my_start = (self.height - mh) // 2

            # Close button [X] at top-right
            close_rect = pygame.Rect(mx_start + mw - 38, my_start + 12, 26, 26)
            if close_rect.collidepoint(mx, my):
                self.show_guide = False
                return True

            # Tab bar buttons
            tab_y = my_start + 50
            tab_h = 32
            tab_w = (mw - 40) // len(self.TABS)
            for idx, _ in enumerate(self.TABS):
                tab_rect = pygame.Rect(mx_start + 20 + idx * tab_w, tab_y, tab_w - 4, tab_h)
                if tab_rect.collidepoint(mx, my):
                    self.active_tab = idx
                    return True

            # Click inside modal absorbs click
            if pygame.Rect(mx_start, my_start, mw, mh).collidepoint(mx, my):
                return True

        # 2. Anatomy Pins interaction
        if self.show_anatomy:
            cos_o = math.cos(jellyfish.orientation)
            sin_o = math.sin(jellyfish.orientation)
            jx = jellyfish.position.x
            jy = jellyfish.position.y
            sz = jellyfish.size
            c = jellyfish.contraction

            for pin in self.pins_meta:
                ox, oy = pin['offset'](sz, c)
                px = jx + ox * cos_o - oy * sin_o
                py = jy + ox * sin_o + oy * cos_o
                # Check hit radius 14 px
                if (mx - px) ** 2 + (my - py) ** 2 <= 14 ** 2:
                    self.selected_pin = pin['id'] if self.selected_pin != pin['id'] else None
                    return True

        return False

    def update_hover(self, mx, my, jellyfish):
        """Track hovered anatomy pin for instant tooltips."""
        if not self.show_anatomy:
            self.hovered_pin = None
            return

        cos_o = math.cos(jellyfish.orientation)
        sin_o = math.sin(jellyfish.orientation)
        jx = jellyfish.position.x
        jy = jellyfish.position.y
        sz = jellyfish.size
        c = jellyfish.contraction

        self.hovered_pin = None
        for pin in self.pins_meta:
            ox, oy = pin['offset'](sz, c)
            px = jx + ox * cos_o - oy * sin_o
            py = jy + ox * sin_o + oy * cos_o
            if (mx - px) ** 2 + (my - py) ** 2 <= 14 ** 2:
                self.hovered_pin = pin
                break

    def draw_anatomy_pins(self, screen, jellyfish):
        """
        Render interactive glowing anatomical leader pins and callout tooltips
        anchored directly to the moving jellyfish.
        """
        if not self.show_anatomy:
            return

        jx = jellyfish.position.x
        jy = jellyfish.position.y
        sz = jellyfish.size
        c = jellyfish.contraction
        cos_o = math.cos(jellyfish.orientation)
        sin_o = math.sin(jellyfish.orientation)

        font_sm = pygame.font.Font(None, 18)
        font_bld = pygame.font.Font(None, 20)

        # Draw glowing pins
        for pin in self.pins_meta:
            ox, oy = pin['offset'](sz, c)
            px = jx + ox * cos_o - oy * sin_o
            py = jy + ox * sin_o + oy * cos_o

            is_active = (self.hovered_pin and self.hovered_pin['id'] == pin['id']) or (self.selected_pin == pin['id'])

            # Soft pulsing halo
            pulse = 1.0 + 0.25 * math.sin(pygame.time.get_ticks() * 0.006 + ox)
            pin_r = 7 if not is_active else 9
            color = (50, 240, 220) if not is_active else (255, 235, 120)

            # Draw outer glow
            halo_surf = pygame.Surface((36, 36), pygame.SRCALPHA)
            halo_alpha = 110 if is_active else 55
            pygame.draw.circle(halo_surf, (*color, halo_alpha), (18, 18), int(pin_r * pulse + 3))
            screen.blit(halo_surf, (px - 18, py - 18))

            # Draw solid core pin
            pygame.draw.circle(screen, color, (int(px), int(py)), pin_r)
            pygame.draw.circle(screen, (10, 25, 40), (int(px), int(py)), 3)

            # Compact label tag next to pin - only when active
            if is_active:
                lbl_surf = font_sm.render(pin['name'].split('(')[0].strip(), True, (255, 245, 140))
                screen.blit(lbl_surf, (px + 12, py - 8))

        # If a pin is hovered or selected, render floating scientific info card
        focus_pin = self.hovered_pin or next((p for p in self.pins_meta if p['id'] == self.selected_pin), None)
        if focus_pin:
            ox, oy = focus_pin['offset'](sz, c)
            px = jx + ox * cos_o - oy * sin_o
            py = jy + ox * sin_o + oy * cos_o

            # Position card nicely without going off screen
            card_w, card_h = 320, 130
            card_x = max(20, min(self.width - card_w - 20, px + 25))
            card_y = max(60, min(self.height - card_h - 60, py - 40))

            # Leader line from pin to card
            pygame.draw.line(screen, (70, 200, 240, 180), (px, py), (card_x, card_y + 20), 1)

            # Semi-translucent card surface
            card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            card.fill((12, 22, 36, 235))
            pygame.draw.rect(card, (60, 180, 220, 240), (0, 0, card_w, card_h), 1, border_radius=8)

            # Category badge
            cat_txt = font_sm.render(focus_pin['category'], True, (255, 215, 90))
            card.blit(cat_txt, (14, 10))

            # Pin title
            title_txt = font_bld.render(focus_pin['name'], True, (220, 245, 255))
            card.blit(title_txt, (14, 28))

            # Divider line
            pygame.draw.line(card, (50, 90, 120), (14, 48), (card_w - 14, 48), 1)

            # Word-wrap detail text
            detail_words = focus_pin['detail'].split(' ')
            line = ""
            dy = 54
            for word in detail_words:
                test_line = line + word + " "
                if font_sm.size(test_line)[0] > card_w - 28:
                    card.blit(font_sm.render(line, True, (185, 215, 235)), (14, dy))
                    line = word + " "
                    dy += 16
                else:
                    line = test_line
            if line:
                card.blit(font_sm.render(line, True, (185, 215, 235)), (14, dy))

            screen.blit(card, (card_x, card_y))

    def draw_active_lesson_banner(self, screen):
        """Render prominent top banner during guided educational experiments."""
        if self.active_lesson is None:
            return

        bw, bh = 760, 68
        bx = (self.width - bw) // 2
        by = 56

        banner = pygame.Surface((bw, bh), pygame.SRCALPHA)
        banner.fill((10, 24, 40, 240))
        pygame.draw.rect(banner, (255, 215, 80, 250), (0, 0, bw, bh), 2, border_radius=8)

        font_hdr = pygame.font.Font(None, 22)
        font_sub = pygame.font.Font(None, 17)

        title_s = font_hdr.render(self.lesson_banner, True, (255, 230, 100))
        banner.blit(title_s, (14, 8))

        # Progress bar
        rem = max(0.0, 1.0 - (self.lesson_timer / 7.0))
        pygame.draw.line(banner, (255, 215, 80), (14, 28), (14 + int((bw - 28) * rem), 28), 2)

        # Subtitle explanation
        sub_s = font_sub.render(self.lesson_explanation[:105] + ("..." if len(self.lesson_explanation) > 105 else ""), True, (210, 235, 255))
        banner.blit(sub_s, (14, 34))

        screen.blit(banner, (bx, by))

    def draw_modal(self, screen):
        """
        Draw rich museum-grade Field Guide modal dialog.
        """
        if not self.show_guide:
            return

        mw, mh = 900, 530
        mx = (self.width - mw) // 2
        my = (self.height - mh) // 2

        # Dim backdrop
        dim = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        dim.fill((5, 12, 20, 185))
        screen.blit(dim, (0, 0))

        # Main Modal Box
        modal = pygame.Surface((mw, mh), pygame.SRCALPHA)
        modal.fill((10, 20, 32, 248))
        pygame.draw.rect(modal, (60, 180, 225, 240), (0, 0, mw, mh), 2, border_radius=12)

        font_title = pygame.font.Font(None, 28)
        font_h2 = pygame.font.Font(None, 22)
        font_p = pygame.font.Font(None, 19)
        font_sm = pygame.font.Font(None, 17)

        # Header Title
        title_txt = font_title.render("JELLYFISH NEUROBIOLOGY ACADEMY: LIFE WITHOUT A BRAIN", True, (120, 240, 255))
        modal.blit(title_txt, (24, 18))

        sub_txt = font_sm.render("A Beginner-Friendly Scientific Guide to 500 Million Years of Decentralized Intelligence", True, (150, 185, 215))
        modal.blit(sub_txt, (24, 44))

        # Close button [X]
        pygame.draw.rect(modal, (180, 50, 50, 220), (mw - 44, 16, 26, 26), border_radius=4)
        x_txt = font_title.render("×", True, (255, 255, 255))
        modal.blit(x_txt, (mw - 38, 14))

        # Tabs Header
        tab_y = 68
        tab_w = (mw - 48) // len(self.TABS)
        tab_h = 30
        for i, tab_title in enumerate(self.TABS):
            is_cur = (i == self.active_tab)
            t_col = (20, 48, 72, 230) if is_cur else (12, 25, 40, 160)
            b_col = (80, 220, 255) if is_cur else (40, 75, 105)
            pygame.draw.rect(modal, t_col, (24 + i * tab_w, tab_y, tab_w - 4, tab_h), border_top_left_radius=6, border_top_right_radius=6)
            pygame.draw.rect(modal, b_col, (24 + i * tab_w, tab_y, tab_w - 4, tab_h), 1, border_top_left_radius=6, border_top_right_radius=6)
            txt_c = (255, 240, 130) if is_cur else (150, 180, 210)
            t_surf = font_sm.render(tab_title, True, txt_c)
            modal.blit(t_surf, (28 + i * tab_w, tab_y + 8))

        # Content Box
        content_rect = pygame.Rect(24, tab_y + tab_h, mw - 48, mh - (tab_y + tab_h) - 24)
        pygame.draw.rect(modal, (14, 28, 44, 210), content_rect, border_radius=6)
        pygame.draw.rect(modal, (45, 90, 130), content_rect, 1, border_radius=6)

        # Tab Content Rendering
        cx = 44
        cy = tab_y + tab_h + 18

        if self.active_tab == 0:
            # 1. No Brain Paradigm
            h_surf = font_h2.render("How Does an Animal Navigate, Hunt, and Survive with ZERO Brain?", True, (245, 225, 120))
            modal.blit(h_surf, (cx, cy))
            cy += 28

            paragraphs = [
                "• THE CEPHALIZATION MYTH: Humans assume complex behavior requires a central cortex. "
                "Jellyfish prove otherwise! Over 500 million years ago, ancient cnidarians pioneered the "
                "very first nervous system in animal evolution: a decentralized, interconnected Nerve Net.",

                "• EMBODIED INTELLIGENCE: In a brainless creature, the body IS the computation. Sensory receptors "
                "are woven directly into the motor tissue. An environmental cue (touch, light, food chemistry) "
                "instantly triggers a wave of electrical depolarization that sweeps radially across the net.",

                "• DAMAGE TOLERANCE: Cut a mammal's brain, and functions cease. Cut a jellyfish in half, and both "
                "halves continue pulsing and coordinating independently! Each rhopalium margin hub can sustain "
                "autonomous rhythmic propulsion.",

                "• TAKEAWAY: Nature solved robotics and autonomous control half a billion years ago without needing "
                "a central processing unit (CPU). Intelligence is emergent, distributed, and fluid."
            ]
            for p in paragraphs:
                words = p.split(' ')
                line = ""
                for w in words:
                    if font_p.size(line + w + " ")[0] > mw - 100:
                        modal.blit(font_p.render(line, True, (200, 230, 255)), (cx, cy))
                        cy += 20
                        line = w + " "
                    else:
                        line += w + " "
                if line:
                    modal.blit(font_p.render(line, True, (200, 230, 255)), (cx, cy))
                    cy += 24

        elif self.active_tab == 1:
            # 2. Rhopalia & Statoliths
            h_surf = font_h2.render("The 8 Rhopalia: Pacemakers, Gravity Statoliths & Vision Clubs", True, (245, 225, 120))
            modal.blit(h_surf, (cx, cy))
            cy += 28

            paragraphs = [
                "• 8 SENSORY MARGIN HUBS: Spaced symmetrically around the bell rim are 8 club-like sensory organs "
                "called RHOPALIA. Each acts as a miniature, autonomous decision-making hub.",

                "• STATOCYST GRAVITY SENSING: Inside each rhopalium rests a dense microscopic crystal of calcium "
                "carbonate called a STATOLITH. When the jellyfish tilts, gravity pulls the statolith down onto ciliated "
                "sensory hair cells, triggering asymmetric coronal muscle pulses that right the animal upright!",

                "• DECENTRALIZED PACEMAKERS: No central clock tells the jellyfish when to pulse. Instead, pacemaker "
                "neurons inside each rhopalium oscillate spontaneously. Whichever rhopalium reaches firing threshold "
                "first launches an action potential wave that resets (entrains) all other pacemakers.",

                "• RHOPALIAL OCELLI: Pigmented ocelli detect ambient downwelling sunlight, driving phototaxis upward "
                "into productive ocean photic zones."
            ]
            for p in paragraphs:
                words = p.split(' ')
                line = ""
                for w in words:
                    if font_p.size(line + w + " ")[0] > mw - 100:
                        modal.blit(font_p.render(line, True, (200, 230, 255)), (cx, cy))
                        cy += 20
                        line = w + " "
                    else:
                        line += w + " "
                if line:
                    modal.blit(font_p.render(line, True, (200, 230, 255)), (cx, cy))
                    cy += 24

        elif self.active_tab == 2:
            # 3. Traveling Waves & Gating
            h_surf = font_h2.render("Nerve Net Waves: Bidirectional Synapses & Refractory Gating", True, (245, 225, 120))
            modal.blit(h_surf, (cx, cy))
            cy += 28

            paragraphs = [
                "• BIDIRECTIONAL SYNAPSES: Unlike mammalian chemical synapses which only transmit one way (axodendritic), "
                "jellyfish nerve net synapses are unpolarized or bidirectional. Signals can travel in any direction!",

                "• THE PROBLEM OF ECHO SEIZURES: In a bidirectional grid, a firing neuron would stimulate its neighbor, "
                "which would immediately fire right back into the first neuron, creating an infinite, lethal echo loop.",

                "• THE SOLUTION — REFRACTORY GATING: After firing an action potential, a neuron enters a refractory state "
                "(0.15s) where membrane voltage hyperpolarizes (-80 mV) and cannot fire again. This forces signals to travel "
                "ONLY forward as a clean traveling wave, completely preventing reverberating feedback!",

                "• LIVE OSCILLOSCOPE: Check the patch-clamp oscilloscope at the right of your screen: CH1 (Sensory N0) "
                "depolarizes across threshold (1.0V / -55 mV), triggering the propagation delay to CH2 (Motor N12)."
            ]
            for p in paragraphs:
                words = p.split(' ')
                line = ""
                for w in words:
                    if font_p.size(line + w + " ")[0] > mw - 100:
                        modal.blit(font_p.render(line, True, (200, 230, 255)), (cx, cy))
                        cy += 20
                        line = w + " "
                    else:
                        line += w + " "
                if line:
                    modal.blit(font_p.render(line, True, (200, 230, 255)), (cx, cy))
                    cy += 24

        elif self.active_tab == 3:
            # 4. Vortex Hydrodynamics
            h_surf = font_h2.render("Biomechanics: Elastic Mesoglea & Toroidal Vortex Rings", True, (245, 225, 120))
            modal.blit(h_surf, (cx, cy))
            cy += 28

            paragraphs = [
                "• THE SPRING RECOIL (MESOGLEA): Jellyfish contain zero antagonistic muscles. When circular striated "
                "muscles contract, they squeeze the elastic, gelatinous mesoglea. When muscles relax, the mesoglea's "
                "stored elastic strain automatically snaps the bell back open with ZERO metabolic energy cost!",

                "• STARTING & STOPPING VORTICES: As the bell contracts, a high-pressure jet ejects from the subumbrella, "
                "curling around the margin into a 'starting vortex ring' that pushes the jellyfish forward. As the bell "
                "re-expands, a 'stopping vortex ring' forms, recovering momentum from the water column.",

                "• REYNOLDS NUMBER (Re ~ 200): Jellyfish swim in an intermediate regime where both inertial and viscous "
                "forces govern flow. They are recognized by biomechanists as the most energy-efficient swimmers on Earth!"
            ]
            for p in paragraphs:
                words = p.split(' ')
                line = ""
                for w in words:
                    if font_p.size(line + w + " ")[0] > mw - 100:
                        modal.blit(font_p.render(line, True, (200, 230, 255)), (cx, cy))
                        cy += 20
                        line = w + " "
                    else:
                        line += w + " "
                if line:
                    modal.blit(font_p.render(line, True, (200, 230, 255)), (cx, cy))
                    cy += 24

        elif self.active_tab == 4:
            # 5. Gastrovascular Cavity
            h_surf = font_h2.render("Gastrovascular System: Digestion & Circulation Without Blood or Organs", True, (245, 225, 120))
            modal.blit(h_surf, (cx, cy))
            cy += 28

            paragraphs = [
                "• COMBINED ORGAN: Jellyfish possess no separate heart, lungs, kidneys, or circulatory vessels. "
                "The entire interior of the body is a single continuous GASTROVASCULAR CAVITY that performs digestion, "
                "gas exchange, and nutrient transport all at once.",

                "• FEEDING MANUBRIUM: Zooplankton and copepods caught by oral arms are drawn into the central manubrium. "
                "Digestive enzymes dissolve the prey into glowing nutrient boluses inside the gastric pouches.",

                "• 8 RADIAL CANALS: Tiny beating microscopic cilia line the 8 radial canals, pumping digested nutrients "
                "directly outward to the margin ring canal, nourishing swimming muscles and sensory rhopalia directly.",

                "• TRY IT: Press [F] or click the open ocean to place a plankton swarm and watch the feeding sequence!"
            ]
            for p in paragraphs:
                words = p.split(' ')
                line = ""
                for w in words:
                    if font_p.size(line + w + " ")[0] > mw - 100:
                        modal.blit(font_p.render(line, True, (200, 230, 255)), (cx, cy))
                        cy += 20
                        line = w + " "
                    else:
                        line += w + " "
                if line:
                    modal.blit(font_p.render(line, True, (200, 230, 255)), (cx, cy))
                    cy += 24

        screen.blit(modal, (mx, my))
