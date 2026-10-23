"""
Test Suite for Phase 10: Deep-Sea Environment
Tests environmental physical properties, water currents, fluid drag separation,
marine snow & food advection, predator detection, and regression of sensory/motor pipelines.
"""

import math
import os
import pygame

# Set dummy video driver for headless execution
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from environment import Environment, DeepSeaPredator
from jellyfish import Jellyfish
from nervous_system import NervousSystem
from sensory_system import SensorySystem


def test_environmental_properties():
    """Test 1: Verify depth, pressure, temperature, and darkness models."""
    print("Test 1: Verifying environmental physical property calculations...")
    env = Environment(1200, 700)

    # Test surface conditions (y = 120)
    cond_surface = env.get_conditions_at(pygame.Vector2(600, 120))
    assert math.isclose(cond_surface['depth_m'], 200.0, abs_tol=1e-3), f"Surface depth expected 200m, got {cond_surface['depth_m']}"
    assert math.isclose(cond_surface['pressure_atm'], 21.0, abs_tol=1e-3), f"Surface pressure expected 21 atm, got {cond_surface['pressure_atm']}"
    assert math.isclose(cond_surface['temp_c'], 20.0, abs_tol=1e-3), f"Surface temp expected 20°C, got {cond_surface['temp_c']}"
    assert math.isclose(cond_surface['darkness'], 0.15, abs_tol=1e-3), f"Surface darkness expected 0.15, got {cond_surface['darkness']}"

    # Test seabed conditions (y = 580)
    cond_seabed = env.get_conditions_at(pygame.Vector2(600, 580))
    assert math.isclose(cond_seabed['depth_m'], 3000.0, abs_tol=1e-3), f"Seabed depth expected 3000m, got {cond_seabed['depth_m']}"
    assert math.isclose(cond_seabed['pressure_atm'], 301.0, abs_tol=1e-3), f"Seabed pressure expected 301 atm, got {cond_seabed['pressure_atm']}"
    assert math.isclose(cond_seabed['temp_c'], 4.0, abs_tol=1e-3), f"Seabed temp expected 4°C, got {cond_seabed['temp_c']}"
    assert math.isclose(cond_seabed['darkness'], 1.0, abs_tol=1e-3), f"Seabed darkness expected 1.0, got {cond_seabed['darkness']}"

    # Test midwater gradient (y = 350)
    cond_mid = env.get_conditions_at(pygame.Vector2(600, 350))
    assert 200.0 < cond_mid['depth_m'] < 3000.0, "Midwater depth should be intermediate"
    assert 21.0 < cond_mid['pressure_atm'] < 301.0, "Midwater pressure should be intermediate"
    assert 4.0 < cond_mid['temp_c'] < 20.0, "Midwater temp should be intermediate"
    assert 0.15 < cond_mid['darkness'] < 1.0, "Midwater darkness should be intermediate"

    print("PASS: Environmental physical models correctly compute depth, pressure, temperature, and darkness.")


def test_water_current_and_drag_separation():
    """Test 2: Verify current modes and separation of environmental drag from muscle swimming."""
    print("Test 2: Verifying water current modes and physical force separation...")
    env = Environment(1200, 700)
    jelly = Jellyfish(600, 350)

    # 1. Mode cycling
    assert env.current_mode_index == 0, "Default mode should be Calm (0)"
    env.cycle_current()
    assert env.current_mode_index == 1, "Mode 1 should be Eastward"
    curr_east = env.get_current_at(jelly.position)
    assert curr_east.x == 22.0 and curr_east.y == 0.0, f"Expected Eastward (22, 0), got {curr_east}"

    env.cycle_current()
    assert env.current_mode_index == 2, "Mode 2 should be Westward"
    curr_west = env.get_current_at(jelly.position)
    assert curr_west.x == -22.0 and curr_west.y == 0.0, f"Expected Westward (-22, 0), got {curr_west}"

    # 2. Fluid drag on jellyfish: Eastward current should move jellyfish east without neural contraction
    env.current_mode_index = 1
    current_vel = env.get_current_at(jelly.position)
    initial_x = jelly.position.x

    # Update with 0 motor activation
    zero_activations = [0.0] * 8
    for _ in range(80):
        jelly.update(0.016, zero_activations, current_velocity=current_vel)

    assert jelly.position.x > initial_x + 5.0, f"Jellyfish should have drifted eastward, pos.x: {jelly.position.x}"
    assert jelly.velocity.x > 5.0, f"Jellyfish velocity.x should be positive due to current drag, got {jelly.velocity.x}"
    assert jelly.contraction == 0.0, f"Muscle contraction must remain 0 during passive current drag, got {jelly.contraction}"

    # 3. Separation of forces: An active motor stroke should produce vertical swimming regardless of current
    full_activations = [1.0] * 8
    vel_before = jelly.velocity.y
    for _ in range(5):
        jelly.update(0.016, full_activations, current_velocity=current_vel)
    assert jelly.velocity.y < vel_before - 30.0, f"Muscle contraction must generate upward swimming impulse independently of current: {jelly.velocity.y} vs {vel_before}"

    print("PASS: Water currents apply fluid drag without contaminating muscle contraction or neural pipelines.")


def test_particle_and_food_advection():
    """Test 3: Verify marine snow and food particles are advected by currents."""
    print("Test 3: Verifying marine snow and food advection...")
    env = Environment(1200, 700)
    sensory = SensorySystem()
    jelly = Jellyfish(600, 350)
    net = NervousSystem(4, 5)

    # Place food
    sensory.spawn_food(600, 300)
    initial_food_x = sensory.food_position.x

    # Set eastward current
    env.current_mode_index = 1
    dt = 0.05
    for _ in range(20):
        env.update(dt)
        sensory.update(dt, jelly, net, environment=env)

    assert sensory.food_position.x > initial_food_x + 10.0, f"Food should drift eastward with current: {sensory.food_position.x} vs {initial_food_x}"

    print("PASS: Suspended particles and food are properly advected by environmental currents.")


def test_predator_detection_and_escape():
    """Test 4: Verify predator disturbance is sensed through mechanoreceptors and triggers escape swimming."""
    print("Test 4: Verifying predator sensory detection and neural escape response...")
    env = Environment(1200, 700)
    sensory = SensorySystem()
    jelly = Jellyfish(600, 350)
    net = NervousSystem(4, 5)

    # Spawn predator approaching jellyfish
    env.predator.spawn(target_y=350.0, direction=1)
    env.predator.position.x = jelly.position.x - 300.0  # Far away (> sensing radius 175)

    # Update: predator far away -> no detection
    sensory.update(0.016, jelly, net, environment=env)
    assert not sensory.touch_detected, "Predator out of range should not trigger mechanoreceptor"
    assert net.neurons[0].activity == 0.0, "Neuron 0 should remain inactive when predator is out of range"

    # Move predator within sensing radius (e.g. 100px away)
    env.predator.position.x = jelly.position.x - 100.0
    sensory.update(0.016, jelly, net, environment=env)

    assert sensory.touch_detected, "Predator within 175px must trigger mechanoreceptor"
    assert net.neurons[0].input_current > 0.0 or net.neurons[0].activity > 0.0, "Predator wake must stimulate Neuron 0"

    # Propagate through neural network to motor neurons and muscles
    motor_fired = False
    peak_contraction = 0.0
    for _ in range(12):
        net.update(0.05)
        motor_acts = [net.neurons[i].activity for i in range(12, 20)]
        jelly.update(0.05, motor_acts)
        if any(act > 0.2 for act in motor_acts):
            motor_fired = True
        if jelly.contraction > peak_contraction:
            peak_contraction = jelly.contraction

    assert motor_fired, "Predator stimulus at Neuron 0 must propagate to motor neurons 12-19"
    assert peak_contraction > 0.4, f"Escape response must contract bell muscles (peak: {peak_contraction})"
    assert jelly.velocity.y < -30.0, f"Escape response must propel jellyfish upward (velocity: {jelly.velocity.y})"

    print("PASS: Predator wake triggers Neuron 0, motor contraction, and upward escape swimming via neural net.")


def test_regressions_phase8_and_9():
    """Test 5: Verify Phase 8 and Phase 9 functionality without regressions."""
    print("Test 5: Verifying Phase 8 and Phase 9 regression integrity...")
    jelly = Jellyfish(600, 350)
    net = NervousSystem(4, 5)
    sensory = SensorySystem()
    env = Environment(1200, 700)

    # 1. Reset check
    sensory.reset()
    env.reset()
    assert env.current_mode_index == 0
    assert not env.predator.active
    assert not sensory.touch_detected

    # 2. Manual stimulus 'S' (Neuron 0)
    net.stimulate(0)
    for _ in range(10):
        net.update(0.05)
        acts = [net.neurons[i].activity for i in range(12, 20)]
        jelly.update(0.05, acts, current_velocity=env.get_current_at(jelly.position))

    assert jelly.contraction > 0.3, "Direct neural stimulation must contract muscles"
    assert jelly.velocity.y < -20.0, "Direct neural stimulation must generate upward swimming"

    # 3. Light cycling
    sensory.cycle_light()
    sensory.update(0.05, jelly, net, environment=env)
    assert net.neurons[2].input_current > 0.0 or net.neurons[2].activity > 0.0, "Light change must stimulate Neuron 2"

    print("PASS: All Phase 8 and Phase 9 pipelines operate with 100% integrity.")


if __name__ == "__main__":
    test_environmental_properties()
    test_water_current_and_drag_separation()
    test_particle_and_food_advection()
    test_predator_detection_and_escape()
    test_regressions_phase8_and_9()
    print("\nALL PHASE 10 ENVIRONMENT TESTS PASSED SUCCESSFULLY!")
