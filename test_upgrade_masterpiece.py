"""
Comprehensive Verification Suite for Deep-Sea Masterpiece Upgrade:
1. Bioluminescent layered bell anatomy & radial canal excitation flash
2. Hydrodynamic vortex wake particle generation
3. Metabolic ATP energy expenditure and gastric digestion
4. Live patch-clamp electrophysiology oscilloscope trace recording
5. Interactive micro-electrode neuron stimulation
6. Bioluminescent copepod plankton swarm chemotaxis & ingestion
"""

import pygame
import math
from jellyfish import Jellyfish
from nervous_system import NervousSystem
from sensory_system import SensorySystem
from environment import Environment


def test_bioluminescent_anatomy_and_radial_canals():
    """Verify radial canals and rhopalia respond to motor neuron activation."""
    print("Test 1: Verifying bioluminescent anatomy and radial canal excitation...")
    jf = Jellyfish(600, 350)
    ns = NervousSystem(4, 5)

    assert jf.energy == 85.0, "Jellyfish must initialize with 85% metabolic energy reserve"
    assert len(jf.wake_particles) == 0, "Wake particles should start empty"

    # Stimulate motor neuron (Neuron 12 -> Muscle 0)
    ns.stimulate(12, 80.0)
    for _ in range(5):
        ns.update(0.016)
        motor_acts = [ns.neurons[i].activity for i in range(12, 20)]
        jf.update(0.016, motor_acts)

    # Verify muscle contraction and bioluminescence flash
    assert jf.contraction > 0.0, "Bell muscles must contract"
    assert jf.bioluminescence_glow > 0.0, "Active swimming must trigger bioluminescent glow"
    print(f"  Peak contraction: {jf.contraction:.3f}, Bioluminescence: {jf.bioluminescence_glow:.2f}")
    print("PASS: Bioluminescent anatomy and excitation confirmed.\n")


def test_wake_vortices():
    """Verify contraction power strokes shed fluid vortex rings."""
    print("Test 2: Verifying hydrodynamic wake vortex generation...")
    jf = Jellyfish(600, 350)
    dt = 0.016

    # Force a rapid contraction stroke
    acts = [1.0] * 8
    for _ in range(4):
        jf.update(dt, acts)

    assert len(jf.wake_particles) > 0, "Power stroke must shed bioluminescent wake vortex particles"
    initial_count = len(jf.wake_particles)

    # Update without contraction: wake particles should dissipate after their 0.7-1.2s lifespan
    for _ in range(80):
        jf.update(dt, [0.0] * 8)

    print(f"  Vortex particles generated: {initial_count}, active after dissipation: {len(jf.wake_particles)}")
    assert len(jf.wake_particles) < initial_count, "Wake particles must dissipate naturally over time"
    print("PASS: Hydrodynamic wake vortices verified.\n")


def test_metabolic_energy_and_digestion():
    """Verify ATP energy expenditure and gastric digestion."""
    print("Test 3: Verifying ATP energy expenditure and gastric digestion...")
    jf = Jellyfish(600, 350)
    dt = 0.016

    initial_energy = jf.energy

    # Continuous pulsing without food expends metabolic energy
    for _ in range(60):
        acts = [1.0 if (_ % 15 < 6) else 0.0] * 8
        jf.update(dt, acts)

    assert jf.energy < initial_energy, f"Swimming must consume metabolic energy: {jf.energy} < {initial_energy}"
    depleted_energy = jf.energy
    print(f"  Energy after swimming: {depleted_energy:.1f}% (down from {initial_energy:.1f}%)")

    # Ingest food into the gastric cavity
    jf.feed(amount=25.0)
    assert len(jf.digesting_particles) > 0, "Feeding must deposit food boluses in the gastric cavity"
    assert jf.energy > depleted_energy, "Feeding must restore metabolic ATP energy"

    print(f"  Energy after feeding: {jf.energy:.1f}%, Active digesting boluses: {len(jf.digesting_particles)}")
    print("PASS: Metabolic energy and gastric digestion verified.\n")


def test_oscilloscope_and_micro_electrode():
    """Verify electrophysiology oscilloscope traces and micro-electrode hit testing."""
    print("Test 4: Verifying patch-clamp oscilloscope and micro-electrode stimulation...")
    ns = NervousSystem(4, 5)
    dt = 0.016

    # Check hit testing
    n0_idx = ns.get_neuron_at(ns.grid_x, ns.grid_y)
    assert n0_idx == 0, f"Neuron 0 position hit test failed, got: {n0_idx}"

    n12_x = ns.grid_x + (12 % 5) * ns.spacing
    n12_y = ns.grid_y + (12 // 5) * ns.spacing
    n12_idx = ns.get_neuron_at(n12_x, n12_y)
    assert n12_idx == 12, f"Neuron 12 position hit test failed, got: {n12_idx}"

    # Verify micro-electrode stimulation injects current
    ns.stimulate(n0_idx, strength=80.0)
    assert ns.neurons[0].input_current > 0.0 or ns.neurons[0].membrane_potential > 0.0

    # Advance simulation and check oscilloscope waveforms
    peak_v1 = 0.0
    for _ in range(30):
        ns.update(dt)
        if ns.trace_ch1[-1] > peak_v1:
            peak_v1 = ns.trace_ch1[-1]

    assert peak_v1 >= 1.0, f"Oscilloscope must record action potential spike (>= 1.0V), got {peak_v1}"
    print(f"  Micro-electrode fired Neuron 0, Oscilloscope recorded spike peak: {peak_v1:.2f}V")
    print("PASS: Electrophysiology oscilloscope and micro-electrode verified.\n")


def test_plankton_swarm_chemotaxis():
    """Verify chemotaxis towards a bioluminescent plankton swarm and ingestion."""
    print("Test 5: Verifying plankton swarm chemotaxis and ingestion...")
    jf = Jellyfish(600, 350)
    ns = NervousSystem(4, 5)
    ss = SensorySystem()
    dt = 0.016

    # Spawn plankton swarm to the right
    ss.spawn_food(690, 350)
    assert ss.food_active, "Plankton swarm must be active"

    captured = False
    for step in range(120):
        ss.update(dt, jf, ns)
        ns.update(dt)
        acts = [ns.neurons[i].activity for i in range(12, 20)]
        jf.update(dt, acts)
        if not ss.food_active:
            captured = True
            print(f"  Plankton swarm captured at step {step} (pos: {jf.position.x:.1f}, {jf.position.y:.1f})")
            break

    assert captured, "Jellyfish must steer towards and capture plankton swarm"
    assert len(jf.digesting_particles) > 0, "Captured plankton must enter gastric digestion"
    print("PASS: Plankton swarm chemotaxis and ingestion verified.\n")


if __name__ == "__main__":
    test_bioluminescent_anatomy_and_radial_canals()
    test_wake_vortices()
    test_metabolic_energy_and_digestion()
    test_oscilloscope_and_micro_electrode()
    test_plankton_swarm_chemotaxis()
    print("ALL UPGRADE MASTERPIECE TESTS PASSED SUCCESSFULLY!")
