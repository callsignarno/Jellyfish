import os
import pygame

os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

from jellyfish import Jellyfish
from nervous_system import NervousSystem
from sensory_system import SensorySystem
from environment import Environment
from educational_guide import EducationalGuide

WIDTH = 1200
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))

jellyfish = Jellyfish(WIDTH // 2, HEIGHT // 2)
nervous_system = NervousSystem(rows=4, cols=5)
sensory_system = SensorySystem()
environment = Environment(WIDTH, HEIGHT)
educational_guide = EducationalGuide(WIDTH, HEIGHT)

# Stimulate neuron 0 and simulate 30 frames
nervous_system.stimulate(0, strength=85.0)
dt = 1.0 / 60.0

for _ in range(35):
    environment.update(dt)
    sensory_system.update(dt, jellyfish, nervous_system, environment=environment)
    nervous_system.update(dt)
    motor_indices = range(12, 20)
    activations = [max(0.0, min(nervous_system.neurons[i].activity, 1.0)) for i in motor_indices]
    cur_vel = environment.get_current_at(jellyfish.position)
    jellyfish.update(dt, activations, current_velocity=cur_vel)
    educational_guide.update(dt, jellyfish, nervous_system, sensory_system, environment)

# Enable anatomy pins and simulate hover on 'rhopalia'
educational_guide.show_anatomy = True
educational_guide.hovered_pin = educational_guide.pins_meta[0]

# --- Render Shot 1: The upgraded living simulation ---
environment.draw_atmosphere(screen, sensory_system.current_light)
environment.draw_particles(screen)
environment.draw_terrain(screen)
sensory_system.draw(screen, draw_obstacle=False)
environment.draw_predator(screen)
jellyfish.draw(screen)
educational_guide.draw_anatomy_pins(screen, jellyfish)

telemetry_data = {
    're': jellyfish.reynolds_number,
    'thrust_mn': jellyfish.instant_thrust_mn,
    'strain_pct': jellyfish.elastic_strain_pct,
    'energy': jellyfish.energy
}
nervous_system.draw(screen, telemetry_data=telemetry_data)

# Top HUD
font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 20)
btn_font = pygame.font.Font(None, 17)

hud_panel = pygame.Surface((WIDTH - 260, 52), pygame.SRCALPHA)
hud_panel.fill((10, 20, 32, 220))
pygame.draw.rect(hud_panel, (45, 95, 135, 230), (0, 0, WIDTH - 260, 52), 1, border_radius=8)
screen.blit(hud_panel, (16, 8))

status_text = font.render(f"SIMULATION: RUNNING (1.0x Speed)   |   BEHAVIOR: {sensory_system.active_behavior.upper()}", True, (215, 240, 255))
env_cond = environment.get_conditions_at(jellyfish.position)
curr_name = environment.current_modes[environment.current_mode_index]
env_text = small_font.render(f"Ocean depth: {env_cond['depth_m']:.0f}m | Press: {env_cond['pressure_atm']:.0f} atm | Temp: {env_cond['temp_c']:.1f}°C | Current: {curr_name} | Predator: Lurking", True, (135, 215, 255))
screen.blit(status_text, (28, 12))
screen.blit(env_text, (28, 33))

# Dock
dock_panel = pygame.Surface((WIDTH - 32, 38), pygame.SRCALPHA)
dock_panel.fill((10, 20, 32, 230))
pygame.draw.rect(dock_panel, (45, 95, 135, 230), (0, 0, WIDTH - 32, 38), 1, border_radius=8)
screen.blit(dock_panel, (16, 658))

dock_buttons = [
    ('FIELD GUIDE [E]', (60, 200, 255), False),
    ('ANATOMY [A]', (50, 240, 210), True),
    ('SPEED 1.0x [Z]', (250, 215, 80), False),
    ('PLANKTON [F]', (90, 240, 160), False),
    ('TOUCH [T]', (250, 150, 70), False),
    ('STIM N0 [S]', (210, 160, 255), True),
    ('CURRENT [C]', (120, 210, 255), False),
    ('PREDATOR [P]', (250, 110, 100), False),
    ('LESSONS [1-5]', (255, 235, 120), False),
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

pygame.image.save(screen, "preview_new_sim.png")
print("Saved preview_new_sim.png")

# --- Render Shot 2: The Educational Field Guide Modal ---
educational_guide.show_guide = True
educational_guide.draw_modal(screen)
pygame.image.save(screen, "preview_educational_modal.png")
print("Saved preview_educational_modal.png")
