from muscle import Muscle


muscle = Muscle()

print("Initial contraction:", muscle.contraction)

muscle.activate(1.0)

for i in range(10):
    muscle.update(0.1)
    print(
        f"Step {i + 1}: "
        f"activation={muscle.activation:.2f}, "
        f"contraction={muscle.contraction:.2f}"
    )

muscle.relax()

for i in range(10):
    muscle.update(0.1)
    print(
        f"Relax {i + 1}: "
        f"activation={muscle.activation:.2f}, "
        f"contraction={muscle.contraction:.2f}"
    )