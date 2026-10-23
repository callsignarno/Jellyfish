"""
Phase 9 Sensory System Verification Test Suite:
Validates touch, light, and food sensory pathways through the distributed nerve net.
Confirms no direct stimulus-to-movement bypass exists.
"""
import pygame
from jellyfish import Jellyfish
from nervous_system import NervousSystem
from sensory_system import SensorySystem


def test_sensory_pipeline():
    dt = 1.0 / 60.0

    # -------------------------------------------------------------------------
    # Test 1: Verify Touch / Obstacle Sensory Pathway
    # -------------------------------------------------------------------------
    print("Test 1: Verifying Touch / Obstacle Sensory Pathway...")
    jf = Jellyfish(600, 350)
    ns = NervousSystem(rows=4, cols=5)
    ss = SensorySystem()
    motor_indices = list(range(12, 20))

    # Trigger touch sensory event
    ss.trigger_touch()

    # Step frame: sensory system should stimulate Neuron 0
    ss.update(dt, jf, ns)
    assert ns.neurons[SensorySystem.TOUCH_NEURON].input_current > 0, "Touch should stimulate Neuron 0"

    # Propagate through neural network
    motor_fired = set()
    max_contraction = 0.0
    for _ in range(60):
        ns.update(dt)
        for idx in motor_indices:
            if ns.neurons[idx].fired:
                motor_fired.add(idx)
        acts = [ns.neurons[idx].activity for idx in motor_indices]
        jf.update(dt, acts)
        if jf.contraction > max_contraction:
            max_contraction = jf.contraction

    assert len(motor_fired) == 8, f"Expected all 8 motor neurons to fire from touch, got {sorted(list(motor_fired))}"
    assert max_contraction > 0.5, f"Expected significant bell contraction from touch, got {max_contraction:.3f}"
    print(f"PASS: Touch stimulated Neuron 0 -> all 8 motor neurons fired -> peak contraction {max_contraction:.3f}\n")

    # -------------------------------------------------------------------------
    # Test 2: Touch Anti-Flooding Under Persistent Contact
    # -------------------------------------------------------------------------
    print("Test 2: Verifying Touch Anti-Flooding under persistent contact...")
    jf = Jellyfish(600, 350)
    ns = NervousSystem(rows=4, cols=5)
    ss = SensorySystem()
    # Position jellyfish directly colliding with obstacle
    jf.position.x = ss.obstacle_rect.centerx
    jf.position.y = ss.obstacle_rect.centery
    stim_count = 0

    # Simulate 30 frames of persistent contact (0.5 seconds)
    for _ in range(30):
        prev_input = ns.neurons[SensorySystem.TOUCH_NEURON].input_current
        ss.update(dt, jf, ns)
        if ns.neurons[SensorySystem.TOUCH_NEURON].input_current > prev_input:
            stim_count += 1
        ns.update(dt)

    assert stim_count == 1, f"Persistent contact should not flood network; expected 1 stimulus, got {stim_count}"
    print("PASS: Anti-flooding cooldown prevented repeated network flooding during sustained contact.\n")

    # -------------------------------------------------------------------------
    # Test 3: Verify Light Sensory Pathway
    # -------------------------------------------------------------------------
    print("Test 3: Verifying Light Sensory Pathway...")
    jf = Jellyfish(600, 350)
    ns = NervousSystem(rows=4, cols=5)
    ss = SensorySystem()

    # Change environmental light intensity
    ss.cycle_light()

    # Step frame: sensory system should stimulate Neuron 2
    ss.update(dt, jf, ns)
    assert ns.neurons[SensorySystem.LIGHT_NEURON].input_current > 0, "Light change should stimulate Neuron 2"

    motor_fired = set()
    max_contraction = 0.0
    for _ in range(60):
        ns.update(dt)
        for idx in motor_indices:
            if ns.neurons[idx].fired:
                motor_fired.add(idx)
        acts = [ns.neurons[idx].activity for idx in motor_indices]
        jf.update(dt, acts)
        if jf.contraction > max_contraction:
            max_contraction = jf.contraction

    assert len(motor_fired) == 8, f"Expected all 8 motor neurons to fire from light, got {sorted(list(motor_fired))}"
    assert max_contraction > 0.5, f"Expected significant contraction from light change, got {max_contraction:.3f}"
    print(f"PASS: Light change stimulated Neuron 2 -> all 8 motor neurons fired -> peak contraction {max_contraction:.3f}\n")

    # -------------------------------------------------------------------------
    # Test 4: Verify Food Detection Sensory Pathway
    # -------------------------------------------------------------------------
    print("Test 4: Verifying Food Detection Sensory Pathway...")
    jf = Jellyfish(600, 350)
    ns = NervousSystem(rows=4, cols=5)
    ss = SensorySystem()

    # Toggle food cue placed near jellyfish (within sensing range)
    ss.toggle_food(jf.position)
    assert ss.food_active, "Food should be active"

    # Step frame: sensory system should stimulate Neuron 4
    ss.update(dt, jf, ns)
    assert ss.food_in_range, "Food should be detected in range"
    assert ns.neurons[SensorySystem.FOOD_NEURON].input_current > 0, "Food detection should stimulate Neuron 4"

    motor_fired = set()
    max_contraction = 0.0
    for _ in range(60):
        ns.update(dt)
        for idx in motor_indices:
            if ns.neurons[idx].fired:
                motor_fired.add(idx)
        acts = [ns.neurons[idx].activity for idx in motor_indices]
        jf.update(dt, acts)
        if jf.contraction > max_contraction:
            max_contraction = jf.contraction

    assert len(motor_fired) == 8, f"Expected all 8 motor neurons to fire from food, got {sorted(list(motor_fired))}"
    assert max_contraction > 0.5, f"Expected significant contraction from food cue, got {max_contraction:.3f}"
    print(f"PASS: Food cue stimulated Neuron 4 -> all 8 motor neurons fired -> peak contraction {max_contraction:.3f}\n")

    # -------------------------------------------------------------------------
    # Test 5: Verify Natural Decay When Stimulus Stops
    # -------------------------------------------------------------------------
    print("Test 5: Verifying natural neural and muscle decay when stimulus stops...")
    # Deactivate food
    ss.toggle_food(jf.position)
    assert not ss.food_active, "Food should be deactivated"

    # Run for 2 seconds (120 frames) without sensory inputs
    for _ in range(120):
        ss.update(dt, jf, ns)
        ns.update(dt)
        acts = [ns.neurons[idx].activity for idx in motor_indices]
        jf.update(dt, acts)

    assert jf.contraction == 0.0, f"Expected bell contraction to decay to 0.0, got {jf.contraction}"
    assert all(m.contraction == 0.0 for m in jf.muscles), "Muscles should be fully relaxed"
    assert all(n.activity == 0.0 for n in ns.neurons), "All neuron activities should decay to 0.0"
    print("PASS: Neural activity and muscle contraction completely relaxed to resting state.\n")

    # -------------------------------------------------------------------------
    # Test 6: Strict Architectural Constraint (No Direct Movement Bypass)
    # -------------------------------------------------------------------------
    print("Test 6: Verifying strict absence of direct stimulus-to-movement bypass...")
    class MockDisconnectedNS:
        """A nervous system that ignores sensory inputs."""
        def __init__(self):
            self.neurons = [type('MockN', (), {'activity': 0.0, 'fired': False, 'input_current': 0.0})() for _ in range(20)]
        def stimulate(self, idx, strength=60.0):
            pass # Disconnected / does not excite muscles
        def update(self, dt):
            pass

    mock_ns = MockDisconnectedNS()
    mock_jf = Jellyfish(600, 350)
    mock_ss = SensorySystem()

    # Trigger all three sensory systems simultaneously
    mock_ss.trigger_touch()
    mock_ss.cycle_light()
    mock_ss.toggle_food(mock_jf.position)

    initial_pos = pygame.Vector2(mock_jf.position)
    initial_vel = pygame.Vector2(mock_jf.velocity)

    # Step simulation
    mock_ss.update(dt, mock_jf, mock_ns)
    # With disconnected nervous system, motor activations are all 0.0
    motor_acts = [0.0] * 8
    mock_jf.update(dt, motor_acts)

    # Assert that NO upward thrust was applied directly by sensory events
    assert mock_jf.velocity.y >= initial_vel.y, "Sensory events must not command upward movement directly"
    assert mock_jf.contraction == 0.0, "Sensory events must not command bell contraction directly"
    print("PASS: Strict rule confirmed: sensory events cannot produce movement without neural propagation.\n")

    print("ALL PHASE 9 SENSORY INTEGRATION TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_sensory_pipeline()
