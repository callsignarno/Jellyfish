from nervous_system import NervousSystem

network = NervousSystem(rows=4, cols=5)

# Stimulate neuron 0
source = network.neurons[0]
source.add_input(2.0)

print("Testing neural activity across the grid\n")

for step in range(40):
    # Keep stimulating neuron 0
    source.add_input(2.0)

    network.update(0.1)

    active = [
        i for i, neuron in enumerate(network.neurons)
        if neuron.fired
    ]

    potentials = [
        f"{i}:{neuron.membrane_potential:.1f}"
        for i, neuron in enumerate(network.neurons)
        if neuron.membrane_potential > 0
    ]

    print(
        f"Step {step + 1:2}: "
        f"Fired = {active}, "
        f"Potentials = {potentials}"
    )