class Muscle:
    def __init__(
        self,
        contraction_strength=1.0,
        contraction_rate=5.0,
        relaxation_rate=3.0
    ):
        self.activation = 0.0

        self.contraction_strength = contraction_strength
        self.contraction_rate = contraction_rate
        self.relaxation_rate = relaxation_rate

        self.contraction = 0.0

    def update(self, dt):
        # Muscle contracts when activated
        if self.activation > 0:
            self.contraction += (
                self.activation
                * self.contraction_rate
                * dt
            )

        # Muscle relaxes when activation is removed
        else:
            self.contraction -= self.relaxation_rate * dt

        # Keep contraction between 0 and maximum strength
        self.contraction = max(
            0.0,
            min(self.contraction, self.contraction_strength)
        )

    def activate(self, level=1.0):
        self.activation = max(0.0, min(level, 1.0))

    def relax(self):
        self.activation = 0.0