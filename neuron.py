class Neuron:
    def __init__(self, threshold=1.0, refractory_period=0.1):
        self.membrane_potential = 0.0
        self.threshold = threshold

        self.input_current = 0.0

        self.refractory_period = refractory_period
        self.refractory_timer = 0.0

        self.fired = False
        self.connections = []

    def update(self, dt):
        # Reset firing state
        self.fired = False

        # Handle refractory period
        if self.refractory_timer > 0:
            self.refractory_timer = max(
                0.0, self.refractory_timer - dt
            )
            self.input_current = 0.0
            return

        # Integrate incoming current
        self.membrane_potential += self.input_current * dt

        # Clear input after processing
        self.input_current = 0.0

        # Check firing threshold
        if self.membrane_potential >= self.threshold:
            self.fired = True

            # Reset membrane potential
            self.membrane_potential = 0.0

            # Begin refractory period
            self.refractory_timer = self.refractory_period

    def add_input(self, current):
        # Accumulate incoming current
        self.input_current += current

    def connect(self, neuron):
        # Establish a connection to another neuron
        if neuron not in self.connections:
            self.connections.append(neuron)

    def propagate(self, signal=0.3):
        # A firing neuron sends a signal to connected neurons
        if self.fired:
            for neuron in self.connections:
                neuron.membrane_potential += signal