
from neuron import Neuron


class NervousSystem:
    def __init__(self, rows=4, cols=5):
        self.rows = rows
        self.cols = cols

        # Create the neurons
        self.neurons = [
            Neuron()
            for _ in range(rows * cols)
        ]

        # Connect neighboring neurons
        self.build_connections()

    def get_index(self, row, col):
        return row * self.cols + col

    def build_connections(self):
        for row in range(self.rows):
            for col in range(self.cols):
                neuron = self.neurons[
                    self.get_index(row, col)
                ]

                # Connect to the neuron above
                if row > 0:
                    neuron.connect(
                        self.neurons[
                            self.get_index(row - 1, col)
                        ]
                    )

                # Connect to the neuron below
                if row < self.rows - 1:
                    neuron.connect(
                        self.neurons[
                            self.get_index(row + 1, col)
                        ]
                    )

                # Connect to the neuron on the left
                if col > 0:
                    neuron.connect(
                        self.neurons[
                            self.get_index(row, col - 1)
                        ]
                    )

                # Connect to the neuron on the right
                if col < self.cols - 1:
                    neuron.connect(
                        self.neurons[
                            self.get_index(row, col + 1)
                        ]
                    )
    def update(self, dt):
        # Update every neuron
        for neuron in self.neurons:
            neuron.update(dt)

        # Propagate signals from neurons that fired
        for neuron in self.neurons:
            neuron.propagate()