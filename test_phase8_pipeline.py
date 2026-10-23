"""
Phase 8 Verification Script:
Verifies the complete pipeline:
S key -> stimulated neuron -> neural signal propagation -> motor neuron activity ->
muscle activation -> bell contraction -> upward swimming impulse
"""
import pygame
from jellyfish import Jellyfish
from nervous_system import NervousSystem


def test_pipeline():
    dt = 1.0 / 60.0
    jf = Jellyfish(600, 350)
    ns = NervousSystem(rows=4, cols=5)
    motor_indices = list(range(12, 20))

    # --- Test 1: Quiescent state (no autonomous pulsing) ---
    print("Test 1: Testing quiescent state (no autonomous pulsing)...")
    initial_pos_y = jf.position.y
    initial_contraction = jf.contraction
    assert initial_contraction == 0.0, f"Expected initial contraction 0.0, got {initial_contraction}"

    for _ in range(60):  # 1 second of resting frames
        ns.update(dt)
        acts = [ns.neurons[idx].activity for idx in motor_indices]
        jf.update(dt, acts)
        assert jf.contraction == 0.0, f"Bell contracted without stimulus: {jf.contraction}"

    assert all(m.contraction == 0.0 for m in jf.muscles), "Muscles contracted without stimulus"
    print("PASS: Bell does not pulse autonomously.\n")

    # --- Test 2: Stimulate neuron 0 and verify propagation to all motor neurons ---
    print("Test 2: Stimulate neuron 0 and verify propagation to motor neurons...")
    ns.stimulate(0)
    motor_fired = set()
    max_contraction = 0.0
    peak_vel_y = 0.0

    # Track frames over 2 seconds
    for frame in range(120):
        ns.update(dt)
        for idx in motor_indices:
            if ns.neurons[idx].fired:
                motor_fired.add(idx)

        acts = [ns.neurons[idx].activity for idx in motor_indices]
        jf.update(dt, acts)

        if jf.contraction > max_contraction:
            max_contraction = jf.contraction
        if jf.velocity.y < peak_vel_y:
            peak_vel_y = jf.velocity.y

    print(f"Motor neurons fired: {sorted(list(motor_fired))}")
    assert len(motor_fired) == 8, f"Expected all 8 motor neurons (12-19) to fire, but got {sorted(list(motor_fired))}"
    print(f"Peak bell contraction reached: {max_contraction:.3f}")
    assert max_contraction >= 0.5, f"Expected significant bell contraction (>= 0.5), got {max_contraction:.3f}"
    print(f"Peak upward velocity reached: {peak_vel_y:.1f} px/s")
    assert peak_vel_y < -60.0, f"Expected upward velocity (< -60.0), got {peak_vel_y:.1f}"
    print("PASS: Single stimulus propagated to all 8 motor neurons and generated upward swimming.\n")

    # --- Test 3: Natural relaxation and coasting ---
    print("Test 3: Testing natural muscle relaxation and coasting...")
    # Allow 2 more seconds without stimulus
    for _ in range(120):
        ns.update(dt)
        acts = [ns.neurons[idx].activity for idx in motor_indices]
        jf.update(dt, acts)

    final_contraction = jf.contraction
    print(f"Final bell contraction: {final_contraction:.4f}")
    assert final_contraction == 0.0, f"Expected bell to fully relax to 0.0, got {final_contraction}"
    assert all(m.contraction == 0.0 for m in jf.muscles), "All muscles should be fully relaxed"
    print("PASS: Muscles relaxed naturally after neural activity ceased.\n")

    # --- Test 4: Stable physics (no indefinite upward drift) ---
    print("Test 4: Verifying upward acceleration does not accumulate indefinitely...")
    # S stimulated 10 times in quick succession
    for _ in range(10):
        ns.stimulate(0)
        for _ in range(10):
            ns.update(dt)
            acts = [ns.neurons[idx].activity for idx in motor_indices]
            jf.update(dt, acts)

    print(f"Position after rapid stimulations: {jf.position.y:.1f}")
    assert jf.position.y >= 120.0, f"Jellyfish breached upper boundary: {jf.position.y}"
    print("PASS: Screen bounds and physics prevent runaway upward acceleration.\n")

    print("ALL PHASE 8 TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_pipeline()
