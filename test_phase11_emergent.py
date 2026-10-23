"""
Test Suite for Phase 11: Emergent Behavior
Validates emergent chemotaxis (food steering), predator evasion, obstacle avoidance,
statocyst depth equilibrium, differential muscle steering, and strict absence of movement shortcuts.
"""

import math
import os
import pygame

# Set dummy video driver for headless test execution
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from environment import Environment
from jellyfish import Jellyfish
from nervous_system import NervousSystem
from sensory_system import SensorySystem


def test_differential_muscle_steering():
    """Test 1: Verify differential muscle contraction produces emergent lateral steering."""
    print("Test 1: Verifying differential muscle contraction and emergent lateral steering...")
    dt = 0.016

    # 1. Rightward steering from Neuron 4 (right rhopalium)
    jf_right = Jellyfish(600, 350)
    ns_right = NervousSystem(4, 5)
    ns_right.stimulate(4, 80.0)

    for _ in range(60):
        ns_right.update(dt)
        acts = [ns_right.neurons[i].activity for i in range(12, 20)]
        jf_right.update(dt, acts)

    assert jf_right.position.x > 605.0, f"Stimulating Neuron 4 must steer jellyfish to the right, got x={jf_right.position.x}"
    assert jf_right.position.y < 310.0, f"Power stroke must also propel jellyfish upward, got y={jf_right.position.y}"
    print(f"  Rightward steering: dx={jf_right.position.x - 600:.2f} px, dy={jf_right.position.y - 350:.2f} px")

    # 2. Leftward steering from Neuron 0 (left rhopalium)
    jf_left = Jellyfish(600, 350)
    ns_left = NervousSystem(4, 5)
    ns_left.stimulate(0, 80.0)

    for _ in range(60):
        ns_left.update(dt)
        acts = [ns_left.neurons[i].activity for i in range(12, 20)]
        jf_left.update(dt, acts)

    assert jf_left.position.x < 595.0, f"Stimulating Neuron 0 must steer jellyfish to the left, got x={jf_left.position.x}"
    assert jf_left.position.y < 310.0, f"Power stroke must also propel jellyfish upward, got y={jf_left.position.y}"
    print(f"  Leftward steering: dx={jf_left.position.x - 600:.2f} px, dy={jf_left.position.y - 350:.2f} px")

    # 3. Bilateral vertical swimming from Neuron 2 (center apical organ)
    jf_center = Jellyfish(600, 350)
    ns_center = NervousSystem(4, 5)
    ns_center.stimulate(2, 80.0)

    for _ in range(60):
        ns_center.update(dt)
        acts = [ns_center.neurons[i].activity for i in range(12, 20)]
        jf_center.update(dt, acts)

    assert abs(jf_center.position.x - 600.0) < 2.0, f"Neuron 2 must produce balanced vertical swimming, got dx={jf_center.position.x - 600.0}"
    assert jf_center.position.y < 310.0, f"Upward impulse must be generated, got y={jf_center.position.y}"
    print(f"  Bilateral vertical stroke: dx={jf_center.position.x - 600:.2f} px, dy={jf_center.position.y - 350:.2f} px")

    print("PASS: Differential muscle contractions successfully generate directional steering.\n")


def test_emergent_chemotaxis_food_approach():
    """Test 2: Verify autonomous approach, steering, and ingestion of food cues."""
    print("Test 2: Verifying emergent chemotaxis (food steering and capture)...")
    dt = 0.016

    # 1. Food on the right
    jf = Jellyfish(600, 380)
    ns = NervousSystem(4, 5)
    ss = SensorySystem()
    ss.spawn_food(650, 310)  # Right and above within sensing range (dist ~86 px)

    eaten_right = False
    for step in range(150):
        ss.update(dt, jf, ns)
        ns.update(dt)
        acts = [ns.neurons[i].activity for i in range(12, 20)]
        jf.update(dt, acts)

        if not ss.food_active:
            eaten_right = True
            print(f"  Food on right captured and ingested at step {step} (final pos: {jf.position.x:.1f}, {jf.position.y:.1f})")
            break

    assert eaten_right, "Jellyfish must steer toward and ingest food placed to its right"
    assert len(ss.ingestion_particles) > 0, "Ingestion particles must spawn upon eating food"

    # 2. Food on the left
    jf = Jellyfish(600, 380)
    ns = NervousSystem(4, 5)
    ss = SensorySystem()
    ss.spawn_food(550, 310)  # Left and above within sensing range (dist ~86 px)

    eaten_left = False
    for step in range(150):
        ss.update(dt, jf, ns)
        ns.update(dt)
        acts = [ns.neurons[i].activity for i in range(12, 20)]
        jf.update(dt, acts)

        if not ss.food_active:
            eaten_left = True
            print(f"  Food on left captured and ingested at step {step} (final pos: {jf.position.x:.1f}, {jf.position.y:.1f})")
            break

    assert eaten_left, "Jellyfish must steer toward and ingest food placed to its left"

    print("PASS: Emergent chemotaxis successfully guides jellyfish to food without movement shortcuts.\n")


def test_obstacle_avoidance_and_predator_evasion():
    """Test 3: Verify obstacle avoidance and predator evasion behaviors."""
    print("Test 3: Verifying obstacle avoidance and predator evasion...")
    dt = 0.016
    env = Environment(1200, 700)
    ss = SensorySystem()
    jf = Jellyfish(600, 350)
    ns = NervousSystem(4, 5)

    # 1. Obstacle collision triggers avoidance
    jf.position.x = ss.obstacle_rect.centerx
    jf.position.y = ss.obstacle_rect.centery
    ss.update(dt, jf, ns, environment=env)

    assert ss.touch_detected, "Obstacle collision must be detected"
    assert "Obstacle" in ss.active_behavior, f"Active behavior must reflect obstacle avoidance: {ss.active_behavior}"
    assert ns.neurons[SensorySystem.TOUCH_NEURON].input_current > 0.0, "Neuron 0 must be stimulated"

    # 2. Predator disturbance triggers evasion burst
    ss.reset()
    jf.position.y = 350.0
    env.predator.spawn(target_y=350.0, direction=1)
    env.predator.position.x = jf.position.x - 90.0  # Approaching within 175px

    ss.update(dt, jf, ns, environment=env)
    assert ss.touch_detected, "Predator pressure wake must trigger mechanoreception"
    assert "Predator Evasion" in ss.active_behavior, f"Behavior must be Predator Evasion, got: {ss.active_behavior}"

    # Verify escape stroke propulsion
    peak_escape_vel = 0.0
    for _ in range(30):
        ns.update(dt)
        acts = [ns.neurons[i].activity for i in range(12, 20)]
        jf.update(dt, acts)
        if jf.velocity.y < peak_escape_vel:
            peak_escape_vel = jf.velocity.y

    assert peak_escape_vel < -50.0, f"Predator evasion must propel jellyfish upward out of cruise zone, peak_vel.y={peak_escape_vel}"
    print(f"  Predator evasion vertical escape velocity: {peak_escape_vel:.1f} px/s")

    print("PASS: Obstacle avoidance and predator evasion behaviors verified.\n")


def test_statocyst_depth_regulation():
    """Test 4: Verify statocyst baroreceptive depth equilibrium in deep water."""
    print("Test 4: Verifying statocyst depth equilibrium in deep water...")
    dt = 0.016
    ss = SensorySystem()
    jf = Jellyfish(350, 510)  # Sunk into deep bathypelagic open water (y > 480, clear of reef)
    ns = NervousSystem(4, 5)

    assert ss.statocyst_cooldown == 0.0, "Statocyst should be ready to fire"
    ss.update(dt, jf, ns)

    assert "Depth Equilibrium" in ss.active_behavior, f"Expected Depth Equilibrium behavior, got: {ss.active_behavior}"
    assert ns.neurons[SensorySystem.LIGHT_NEURON].input_current > 0.0, "Statocyst should stimulate center apical neuron (Neuron 2)"

    # Execute recovery stroke
    for _ in range(30):
        ns.update(dt)
        acts = [ns.neurons[i].activity for i in range(12, 20)]
        jf.update(dt, acts)

    assert jf.velocity.y < -30.0, f"Statocyst pulse must produce recovery stroke upward, vel.y={jf.velocity.y}"
    print(f"  Statocyst depth recovery pulse: velocity.y = {jf.velocity.y:.1f} px/s")

    # In midwater zone (y = 350) without stimuli, state should be Quiescent Drift
    ss.reset()
    jf.position.y = 350.0
    ss.update(dt, jf, ns)
    assert ss.active_behavior == "Quiescent Drift", f"Midwater resting state must be Quiescent Drift, got: {ss.active_behavior}"

    print("PASS: Statocyst equilibrium successfully maintains depth regulation in deep water.\n")


def test_no_movement_shortcuts():
    """Test 5: Verify strict absence of direct movement shortcuts without neural propagation."""
    print("Test 5: Verifying strict absence of direct movement shortcuts...")
    dt = 0.016
    ss = SensorySystem()
    jf = Jellyfish(600, 350)
    ns = NervousSystem(4, 5)

    # Place food on right
    ss.spawn_food(650, 310)
    ss.update(dt, jf, ns)

    # Intentionally freeze / zero out motor activations (simulating disrupted neural transmission)
    zero_acts = [0.0] * 8
    pos_before = pygame.Vector2(jf.position)
    jf.update(dt, zero_acts)

    # Jellyfish should NOT move toward food without motor signals
    assert math.isclose(jf.position.x, pos_before.x, abs_tol=1e-5), "Position x must not change toward food without motor activations"
    assert jf.contraction == 0.0, "Muscles must not contract without motor activations"

    print("PASS: Confirmed zero movement shortcuts; all behaviors require neural-to-muscle transmission.\n")


def test_omnidirectional_swimming_all_directions():
    """Test 6: Verify jellyfish can reorient and swim in ANY 2D direction (360 degrees)."""
    print("Test 6: Verifying omnidirectional navigation in all directions (Above, Below, Left, Right)...")
    dt = 0.016
    directions = [
        ('Above', pygame.Vector2(600, 230)),
        ('Right', pygame.Vector2(720, 350)),
        ('Left', pygame.Vector2(480, 350)),
        ('Below', pygame.Vector2(600, 470)),
        ('Down-Right', pygame.Vector2(690, 440)),
        ('Down-Left', pygame.Vector2(510, 440)),
    ]

    for name, target in directions:
        jf = Jellyfish(600, 350)
        ns = NervousSystem(4, 5)
        ss = SensorySystem()
        ss.spawn_food(target.x, target.y)

        captured = False
        for step in range(250):
            ss.update(dt, jf, ns)
            ns.update(dt)
            acts = [ns.neurons[i].activity for i in range(12, 20)]
            jf.update(dt, acts)
            if not ss.food_active:
                captured = True
                print(f"  Target {name:10s} captured at step {step:3d} (final pos: {jf.position.x:.1f}, {jf.position.y:.1f})")
                break

        assert captured, f"Jellyfish must be able to swim toward and capture target {name}"

    print("PASS: Omnidirectional 360-degree swimming navigation verified in all cardinal and diagonal directions.\n")


if __name__ == "__main__":
    test_differential_muscle_steering()
    test_emergent_chemotaxis_food_approach()
    test_obstacle_avoidance_and_predator_evasion()
    test_statocyst_depth_regulation()
    test_no_movement_shortcuts()
    test_omnidirectional_swimming_all_directions()
    print("ALL PHASE 11 EMERGENT BEHAVIOR TESTS PASSED SUCCESSFULLY!")
