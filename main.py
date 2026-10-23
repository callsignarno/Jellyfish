import pygame
import random
import math

from jellyfish import Jellyfish
from nervous_system import NervousSystem
from sensory_system import SensorySystem
from environment import Environment
from educational_guide import EducationalGuide

pygame.init()

# -------------------------
# Window configuration
# -------------------------

WIDTH = 1200
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jellyfish Deep-Sea Neurobiology & Biomechanics (Educational Simulation)")

# -------------------------
# Simulation configuration
# -------------------------

clock = pygame.time.Clock()
FPS = 60

running = True
paused = False

font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 20)
btn_font = pygame.font.Font(None, 17)

# -------------------------
# Create simulation objects
# -------------------------

jellyfish = Jellyfish(WIDTH // 2, HEIGHT // 2)
nervous_system = NervousSystem(rows=4, cols=5)
sensory_system = SensorySystem()
environment = Environment(WIDTH, HEIGHT)
educational_guide = EducationalGuide(WIDTH, HEIGHT)

# Default to showing anatomy pins for educational exploration
educational_guide.show_anatomy = True

# -------------------------
# Main simulation loop
# -------------------------

while running:

    # Calculate base elapsed time in seconds
    raw_dt = clock.tick(FPS) / 1000.0
    # Apply educational time-dilation scale (1.0x, 0.5x, 0.25x)
    dt = raw_dt * educational_guide.time_scale

    mx, my = pygame.mouse.get_pos()
    educational_guide.update_hover(mx, my, jellyfish)

    # -------------------------
    # Handle events
    # -------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Mouse interaction: Educational UI, dock buttons, micro-electrode, plankton, poke
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse click
                click_x, click_y = event.pos

                # 1. Check if educational guide modal or anatomy pins consume click
                if educational_guide.handle_click(click_x, click_y, jellyfish):
                    continue

                # 2. Check interactive bottom dock buttons (y = 662..692)
                dock_handled = False
                if 660 <= click_y <= 694:
                    dock_x = 16
                    btn_w = 108
                    btn_spacing = 114
                    dock_actions = ['guide', 'anatomy', 'speed', 'plankton', 'touch', 'stim', 'current', 'predator', 'lesson', 'reset']
                    for idx, action in enumerate(dock_actions):
                        bx = dock_x + idx * btn_spacing
                        if bx <= click_x <= bx + btn_w:
                            if action == 'guide':
                                educational_guide.toggle_guide()
                            elif action == 'anatomy':
                                educational_guide.toggle_anatomy()
                            elif action == 'speed':
                                educational_guide.cycle_speed()
                            elif action == 'plankton':
                                target_x = jellyfish.position.x + random.uniform(60, 110)
                                target_y = max(160, jellyfish.position.y - 110)
                                sensory_system.spawn_food(target_x, target_y)
                            elif action == 'touch':
                                sensory_system.trigger_touch()
                            elif action == 'stim':
                                nervous_system.stimulate(0, strength=85.0)
                            elif action == 'current':
                                environment.cycle_current()
                            elif action == 'predator':
                                environment.trigger_predator(target_y=jellyfish.position.y)
                            elif action == 'lesson':
                                cur = educational_guide.active_lesson or 0
                                next_l = (cur % 5) + 1
                                educational_guide.start_lesson(next_l, jellyfish, nervous_system, sensory_system, environment)
                            elif action == 'reset':
                                jellyfish = Jellyfish(WIDTH // 2, HEIGHT // 2)
                                nervous_system = NervousSystem(rows=4, cols=5)
                                sensory_system.reset()
                                environment.reset()
                                paused = False
                            dock_handled = True
                            break
                    if dock_handled:
                        continue

                # 3. Micro-electrode stimulation on nerve net
                clicked_neuron = nervous_system.get_neuron_at(click_x, click_y)
                if clicked_neuron is not None:
                    nervous_system.stimulate(clicked_neuron, strength=85.0)
                else:
                    dist_to_jelly = (jellyfish.position - pygame.Vector2(click_x, click_y)).length()
                    if dist_to_jelly < 60.0:
                        sensory_system.trigger_touch()
                    else:
                        sensory_system.spawn_food(click_x, click_y)

        elif event.type == pygame.KEYDOWN:

            # Educational Field Guide Modal
            if event.key == pygame.K_e or event.key == pygame.K_TAB:
                educational_guide.toggle_guide()

            # Anatomy Callout Pins
            elif event.key == pygame.K_a:
                educational_guide.toggle_anatomy()

            # Time Dilation Speed (1.0x -> 0.5x -> 0.25x)
            elif event.key == pygame.K_z:
                educational_guide.cycle_speed()

            # Guided Educational Lessons (1 to 5)
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                lesson_num = int(event.unicode)
                educational_guide.start_lesson(lesson_num, jellyfish, nervous_system, sensory_system, environment)

            # Space = pause/unpause
            elif event.key == pygame.K_SPACE:
                paused = not paused

            # R = reset simulation
            elif event.key == pygame.K_r:
                jellyfish = Jellyfish(WIDTH // 2, HEIGHT // 2)
                nervous_system = NervousSystem(rows=4, cols=5)
                sensory_system.reset()
                environment.reset()
                paused = False

            # S = stimulate neuron 0 directly
            elif event.key == pygame.K_s:
                nervous_system.stimulate(0, strength=85.0)

            # T = Touch / contact cue
            elif event.key == pygame.K_t:
                sensory_system.trigger_touch()

            # L = Cycle environmental light intensity tier
            elif event.key == pygame.K_l:
                sensory_system.cycle_light()

            # Up / Down arrows = Brighten or dim ambient ocean light
            elif event.key == pygame.K_UP:
                sensory_system.set_light(sensory_system.current_light + 0.15)
            elif event.key == pygame.K_DOWN:
                sensory_system.set_light(sensory_system.current_light - 0.15)

            # F = Place food cue at current mouse position
            elif event.key == pygame.K_f:
                mouse_pos = pygame.mouse.get_pos()
                sensory_system.spawn_food(mouse_pos[0], mouse_pos[1])

            # C = Cycle water current modes
            elif event.key == pygame.K_c:
                environment.cycle_current()

            # P = Trigger deep-sea viperfish predator
            elif event.key == pygame.K_p:
                environment.trigger_predator(target_y=jellyfish.position.y)

    # -------------------------
    # Update simulation
    # -------------------------

    if not paused:
        # 1. Update deep-sea environment (current dynamics, particles, predator movement)
        environment.update(dt)

        # 2. Update sensory system (detects touch/obstacle/predator, light, food and stimulates sensory neurons)
        sensory_system.update(dt, jellyfish, nervous_system, environment=environment)

        # 3. Update nervous system (integrates inputs, propagates traveling waves)
        nervous_system.update(dt)

        # 4. Select the eight motor neurons (grid indices 12–19 on rows 2 and 3)
        motor_neuron_indices = range(12, 20)

        # Convert neural activity into normalized muscle activation values [0.0, 1.0]
        motor_activations = []
        for index in motor_neuron_indices:
            neuron = nervous_system.neurons[index]
            activation = max(0.0, min(neuron.activity, 1.0))
            motor_activations.append(activation)

        # 5. Get fluid water current vector at jellyfish position
        current_vel = environment.get_current_at(jellyfish.position)

        # 6. Update muscles, bell contraction, and movement with neural signals & fluid drag
        jellyfish.update(dt, motor_activations, current_velocity=current_vel)

        # 7. Update active educational lesson timers & steps
        educational_guide.update(dt, jellyfish, nervous_system, sensory_system, environment)

    # -------------------------
    # Draw scene
    # -------------------------

    # 1. Ambient deep-sea lighting and surface caustic shafts
    environment.draw_atmosphere(screen, sensory_system.current_light)

    # 2. 3-layer parallax marine snow particles
    environment.draw_particles(screen)

    # 3. Seafloor bathymetry, hydrothermal vent ash plume, sea-pens, and reef shelf
    environment.draw_terrain(screen)

    # 4. Draw food cluster, scent halo, and sparkles
    sensory_system.draw(screen, draw_obstacle=False)

    # 5. Draw deep-sea apex predator
    environment.draw_predator(screen)

    # 6. Draw jellyfish with toroidal vortex rings & glowing radial canals
    jellyfish.draw(screen)

    # 7. Draw interactive anatomical callout pins on jellyfish
    educational_guide.draw_anatomy_pins(screen, jellyfish)

    # 8. Draw neural network, oscilloscope & biometrics card
    telemetry_data = {
        're': jellyfish.reynolds_number,
        'thrust_mn': jellyfish.instant_thrust_mn,
        'strain_pct': jellyfish.elastic_strain_pct,
        'energy': jellyfish.energy
    }
    nervous_system.draw(screen, telemetry_data=telemetry_data)

    # -------------------------
    # Top Information HUD Bar
    # -------------------------

    hud_panel = pygame.Surface((WIDTH - 260, 52), pygame.SRCALPHA)
    hud_panel.fill((10, 20, 32, 220))
    pygame.draw.rect(hud_panel, (45, 95, 135, 230), (0, 0, WIDTH - 260, 52), 1, border_radius=8)
    screen.blit(hud_panel, (16, 8))

    status = "PAUSED" if paused else "RUNNING"
    speed_txt = f"{educational_guide.time_scale}x Speed"
    status_text = font.render(
        f"SIMULATION: {status} ({speed_txt})   |   BEHAVIOR: {sensory_system.active_behavior.upper()}",
        True,
        (215, 240, 255)
    )

    env_cond = environment.get_conditions_at(jellyfish.position)
    curr_name = environment.current_modes[environment.current_mode_index]
    pred_status = "HUNTING" if environment.predator.active else "Lurking"

    env_text = small_font.render(
        f"Ocean depth: {env_cond['depth_m']:.0f}m | Press: {env_cond['pressure_atm']:.0f} atm | Temp: {env_cond['temp_c']:.1f}°C | Current: {curr_name} | Predator: {pred_status}",
        True,
        (135, 215, 255)
    )

    screen.blit(status_text, (28, 12))
    screen.blit(env_text, (28, 33))

    # -------------------------
    # Interactive Bottom Dock Buttons (y = 662..692)
    # -------------------------

    dock_panel = pygame.Surface((WIDTH - 32, 38), pygame.SRCALPHA)
    dock_panel.fill((10, 20, 32, 230))
    pygame.draw.rect(dock_panel, (45, 95, 135, 230), (0, 0, WIDTH - 32, 38), 1, border_radius=8)
    screen.blit(dock_panel, (16, 658))

    dock_buttons = [
        ('FIELD GUIDE [E]', (60, 200, 255), educational_guide.show_guide),
        ('ANATOMY [A]', (50, 240, 210), educational_guide.show_anatomy),
        (f'SPEED {educational_guide.time_scale}x [Z]', (250, 215, 80), educational_guide.time_scale != 1.0),
        ('PLANKTON [F]', (90, 240, 160), sensory_system.food_active),
        ('TOUCH [T]', (250, 150, 70), sensory_system.touch_detected),
        ('STIM N0 [S]', (210, 160, 255), False),
        ('CURRENT [C]', (120, 210, 255), environment.current_mode_index != 0),
        ('PREDATOR [P]', (250, 110, 100), environment.predator.active),
        ('LESSONS [1-5]', (255, 235, 120), educational_guide.active_lesson is not None),
        ('RESET [R]', (180, 195, 215), False),
    ]

    dock_x = 22
    btn_w = 108
    btn_spacing = 114
    for idx, (lbl, col, is_highlight) in enumerate(dock_buttons):
        bx = dock_x + idx * btn_spacing
        by = 663
        bh = 28
        b_bg = (24, 48, 72, 230) if is_highlight else (14, 26, 40, 190)
        pygame.draw.rect(screen, b_bg, (bx, by, btn_w, bh), border_radius=5)
        b_border = col if is_highlight else (50, 85, 120)
        pygame.draw.rect(screen, b_border, (bx, by, btn_w, bh), 1, border_radius=5)
        txt = btn_font.render(lbl, True, col)
        screen.blit(txt, (bx + (btn_w - txt.get_width()) // 2, by + 7))

    # -------------------------
    # Active Educational Lesson Banner
    # -------------------------
    educational_guide.draw_active_lesson_banner(screen)

    # -------------------------
    # Educational Field Guide Modal Dialog
    # -------------------------
    educational_guide.draw_modal(screen)

    # Update display
    pygame.display.flip()

# -------------------------
# Shutdown
# -------------------------

pygame.quit()
