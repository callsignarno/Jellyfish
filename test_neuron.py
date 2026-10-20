from neuron import Neuron

# Create three neurons
neuron_a = Neuron()
neuron_b = Neuron()
neuron_c = Neuron()

# Create a chain: A -> B -> C
neuron_a.connect(neuron_b)
neuron_b.connect(neuron_c)

print("Testing neural chain: A -> B -> C\n")

# Simulate 20 time steps
for i in range(35):

    # Apply continuous external input to neuron A
    neuron_a.add_input(2.0)

    # Update and propagate neuron A
    neuron_a.update(0.1)
    neuron_a.propagate()

    # Update and propagate neuron B
    neuron_b.update(0.1)
    neuron_b.propagate()

    # Update and propagate neuron C
    neuron_c.update(0.1)
    neuron_c.propagate()

    # Display neuron states
    print(
        f"Step {i + 1:2}: "
        f"A={neuron_a.membrane_potential:.2f} "
        f"({'FIRE' if neuron_a.fired else '----'}), "
        f"B={neuron_b.membrane_potential:.2f} "
        f"({'FIRE' if neuron_b.fired else '----'}), "
        f"C={neuron_c.membrane_potential:.2f} "
        f"({'FIRE' if neuron_c.fired else '----'})"
    )