# Jellyfish Deep-Sea Neural Simulation — Phase Handbook

A beginner-friendly, modular handbook documenting each development phase of the Jellyfish Deep-Sea Neural Simulation. This handbook details the biological architecture, how each component works, what was present before each phase, what changes were made, and the empirical test results.

---

## Global System Architecture & Data Flow

The simulation faithfully implements the neuromuscular hierarchy of real cnidarians (*Jellyfish*):

```
┌──────────────────────────────────────────────────────────┐
│                   Environmental Stimuli                  │
│       (Touch/Obstacle, Ambient Light, Food Particles)    │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│             Phase 9: Sensory System Detection            │
│   (Touch -> Neuron 0 | Light -> Neuron 2 | Food -> N4)   │
└────────────────────────────┬─────────────────────────────┘
                             │  nervous_system.stimulate()
                             ▼
┌──────────────────────────────────────────────────────────┐
│             4×5 Distributed Nerve Net Grid               │
│          (Traveling waves, refractory gating)            │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│        Motor Neurons: Indices 12–19 (Coronal Margin)     │
│             (Normalized activity signal 0.0–1.0)         │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│           Phase 8: Eight Bell Muscle Regions             │
│        (Muscle contraction and natural relaxation)       │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│         Muscle-Driven Bell Contraction (Geometry)        │
│          (Dome narrowing and tentacle wave stroke)       │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│             Hydrodynamic Propulsion & Physics            │
│       (Finite upward impulse, water drag, buoyancy)      │
└──────────────────────────────────────────────────────────┘
```

> **Fundamental Rule**: Environmental stimuli and sensory inputs **never** directly alter position, velocity, muscle activation, or bell contraction. All physical actions emerge solely through neural processing across the distributed nerve net.

---

## Phase 8 — Connect the Nerve Net to the Muscles

### 1. What Was Already Present
- **Game Engine**: Pygame display (1200×700), particle marine snow, clock (60 FPS), and status HUD.
- **Parametric Jellyfish**: Dome geometry and 7 wavy tentacles driven by an autonomous cosine animation `math.cos(time * speed)`.
- **Integrate-and-Fire Neuron**: `Neuron` class in `neuron.py` with `threshold=1.0` and `refractory_period=0.1s`.
- **Nerve Net Grid**: 4×5 grid of 20 neurons with bidirectional 4-way connections in `nervous_system.py`.
- **Muscle Model**: `Muscle` class in `muscle.py` with contraction rate (`5.0/s`) and relaxation rate (`3.0/s`).

### 2. The Problems Identified
- **Subthreshold Signal Die-Off**: `Neuron.propagate()` passed `signal=0.3`, which was too weak to reach the firing threshold of 1.0. A single stimulus died at distance 1.
- **Refractory Echo Loops**: When signal strength was raised to 1.0, backward transmission into neurons that just fired caused potentials to accumulate during refractory periods, causing an infinite back-and-forth ping-pong firing loop.
- **Imperceptible Twitches vs. Permanent Contraction**: `neuron.fired` lasted only 1 frame (16.7 ms), producing a negligible twitch. Conversely, raw membrane potential never decayed, keeping muscles permanently contracted.
- **Continuous Runaway Acceleration**: Upward acceleration was applied continuously every frame the bell was contracted, sending the jellyfish off-screen.

### 3. What Was Implemented
- **Refractory Gating in Propagation**: `Neuron.propagate()` now ignores target neurons whose `refractory_timer > 0`, and clears accumulated charge during refractory periods.
- **Forward Traveling Waves**: `NervousSystem` uses `signal_strength=1.0` and `refractory_period=0.15s`, allowing a single stimulus to sweep across all 20 neurons as a clean, unidirectional wave.
- **Motor Activity Envelope**: Introduced `Neuron.activity` (jumps to 1.0 upon firing and decays to 0.0 over ~0.25s), providing muscles with an excitation transient that permits natural subsequent relaxation.
- **Motor Neuron Mapping**: Mapped neurons 12–19 (rows 2 and 3 along the coronal margin) directly to the 8 bell muscles.
- **Impulse-Based Propulsion**: Replaced constant acceleration with an upward impulse proportional to active contraction transition ($\Delta \text{contraction} > 0$). Added hydrodynamic damping (`1.8`) and gentle negative buoyancy sinking (`+15.0 * dt`).

### 4. Verification & Results
- Verified with `test_phase8_pipeline.py`:
  - Quiescent resting state: 0.0 contraction without stimulus.
  - Single stimulus on neuron 0 reached all 8 motor neurons (12–19).
  - Peak contraction reached ~0.66, yielding an upward swimming velocity of ~-103 px/s.
  - Muscles fully relaxed back to 0.0 contraction after neural activity stopped.
  - Movement remained bounded within screen limits without runaway acceleration.

---

## Phase 9 — Sensory System Integration

### 1. What Was Already Present
- Verified working Phase 8 neural-to-muscle-to-movement pipeline.
- Working 4×5 diffuse nerve net with forward wave propagation.
- 8 muscle units driven by motor neurons 12–19.
- Functional keyboard controls (`SPACE` to pause, `R` to reset, `S` for manual stimulation).

### 2. Sensory Modalities & Assigned Sensory Neurons

Three dedicated sensory modalities were introduced via `sensory_system.py`, each mapped to a specific sensory neuron in Row 0 (the sensory pole of the jellyfish):

| Sensory Modality | Sensory Receptor | Grid Neuron | Grid Position | Biological Analogy |
| :--- | :--- | :---: | :---: | :--- |
| **Touch / Obstacle** | Mechanoreceptor | **Neuron 0** | Row 0, Col 0 | Anterior rhopalia / marginal mechanoreceptors detecting reef or floor contact. |
| **Light Detection** | Photoreceptor | **Neuron 2** | Row 0, Col 2 | Central apical ocelli detecting downwelling sunlight or shadow reflexes. |
| **Food Detection** | Chemoreceptor | **Neuron 4** | Row 0, Col 4 | Marginal chemoreceptors detecting organic chemical plumes and nearby plankton. |

---

### 3. How Each Sensory System Works

#### A. Touch / Obstacle Detection
- **Environmental Detection**: Continuously checks if the jellyfish bell collides with the physical reef obstacle (`Rect(500, 520, 180, 40)`) or the seafloor boundary ($y \ge 570$).
- **Manual Test Cue**: Pressing **`T`** triggers a tactile contact cue.
- **Anti-Flooding Cooldown**: Employs a `1.0s` cooldown timer. While the jellyfish remains in contact with an obstacle or the seafloor, it does not spam the nervous system on every frame; it excites the network at paced physiological intervals.
- **Neural Route**: Stimulates `Neuron 0`, launching a diagonal traveling wave that propagates down to motor neurons 12–19, producing an escape swimming impulse.

#### B. Light Detection
- **Environmental Detection**: Models ambient deep-sea lighting through 4 distinct depth tiers (*Abyss*, *Twilight*, *Shallows*, *Surface*).
- **Controls**:
  - **`L`**: Cycles through ambient light tiers.
  - **`UP` / `DOWN` Arrows**: Smoothly brightens or dims the ambient illumination.
- **Visual Atmosphere**: The ocean background and surface lighting gradient dynamically shift from pitch midnight deep sea (`Abyss`) up to luminous sunlit water with downwelling sunlight rays (`Surface`).
- **Change Detection & Anti-Flooding**: Photoreceptors detect changes in ambient light ($\Delta \text{light} \ne 0$) with a `0.7s` debounce timer.
- **Neural Route**: Stimulates `Neuron 2`, launching a bilateral concentric wave through the nerve net down to motor neurons 12–19.

#### C. Food Detection & Placement
- **Interactive Mouse Placement**:
  - **Left Click in Ocean**: Drops food particles exactly at the mouse cursor position!
  - **`F` Key**: Places food at the current mouse cursor location.
- **Proximity Detection**: Computes Euclidean distance to food. If distance $\le 160$ pixels, food is flagged as `IN RANGE`.
- **Ingestion**: When the jellyfish reaches the food (distance $< 42\text{px}$), the food is consumed with a burst of sparkling golden particles!
- **Anti-Flooding Adaptation**: While food remains within sensing range, a `1.3s` adaptation cooldown prevents network flooding while maintaining rhythmic feeding pulses.
- **Natural Decay on Removal**: Eating or removing food stops sensory stimulation; existing neural activity decays cleanly to 0.0.
- **Neural Route**: Stimulates `Neuron 4`, launching a traveling wave down to motor neurons 12–19.

---

### 4. Visual Feedback & HUD Interface

1. **Neural Grid Indicators**:
   - Sensory neurons in Row 0 feature distinct accent rings and letter markers:
     - `T` (Neuron 0 — Orange ring): Touch
     - `L` (Neuron 2 — Yellow ring): Light
     - `F` (Neuron 4 — Green ring): Food
   - Motor neurons (12–19) feature blue accent rings.
2. **Telemetry Status Bar**:
   - `Touch: CONTACT` or `Clear`
   - `Light: Twilight (0.3)` (displays active tier)
   - `Food: IN RANGE`, `Active (Far)`, or `None`
   - `Last Stimulus`: Displays the most recently triggered sensory event.
3. **Environmental Visuals**:
   - A rocky reef obstacle drawn on the seafloor.
   - Bioluminescent golden nutrient particles with a soft attraction halo drawn when food is active.

---

### 5. Interactive Keybindings & Controls Reference

| Input | Action | Target / Sensory Neuron |
| :---: | :--- | :--- |
| **`Left Click` (in water)** | **Place Food at Click Location** | Spawns food at cursor; stimulates **Neuron 4** when within sensing range |
| **`Left Click` (on jellyfish)** | **Tactile Poke / Touch** | Stimulates **Neuron 0** directly |
| **`F`** | Place Food at Mouse Cursor | Spawns food at cursor position |
| **`L`** | Cycle Ambient Light Tier | Stimulates **Neuron 2** on change (*Abyss* $\to$ *Twilight* $\to$ *Shallows* $\to$ *Surface*) |
| **`UP` / `DOWN`** | Fine Adjust Light Brightness | Smoothly adjusts ambient ocean light intensity |
| **`T`** | Test Touch / Obstacle Contact | Stimulates **Neuron 0** |
| **`S`** | Direct Neural Stimulus (Manual) | Directly stimulates **Neuron 0** |
| **`SPACE`** | Pause / Resume Simulation | Freezes / unfreezes update loop |
| **`R`** | Reset Simulation | Resets jellyfish, nerve net, and sensory state |

---

### 6. Testing & Verification Results

All tests were automated and verified via `test_phase9_sensory.py`:

| Test Case | Description | Result | Details |
| :---: | :--- | :---: | :--- |
| **1** | Touch Sensory Pathway | **PASS** | `T` / obstacle contact stimulates Neuron 0 $\to$ all 8 motor neurons fire $\to$ peak contraction 0.657 $\to$ upward impulse. |
| **2** | Touch Anti-Flooding | **PASS** | 30 frames of sustained collision generated exactly 1 paced stimulus instead of flooding 30 times. |
| **3** | Light Sensory Pathway | **PASS** | Light change stimulates Neuron 2 $\to$ concentric wave $\to$ all 8 motor neurons fire $\to$ peak contraction 0.660. |
| **4** | Food Sensory Pathway | **PASS** | Food proximity ($\le 160\text{px}$) stimulates Neuron 4 $\to$ all 8 motor neurons fire $\to$ peak contraction 0.653. |
| **5** | Natural Decay | **PASS** | Removing stimulus allows all neural activity and muscle contractions to decay to 0.0000. |
| **6** | No Direct Movement Bypass | **PASS** | With disconnected neural net, triggering touch, light, and food simultaneously resulted in 0.0 contraction and zero upward force. |
| **7** | Phase 8 Pipeline Integrity | **PASS** | Re-verified `test_phase8_pipeline.py` with 100% passing results. |
| **8** | Component Unit Tests | **PASS** | `test_neuron.py`, `test_muscle.py`, and `test_nervous_system.py` pass without regression. |

---

### 7. File Manifest

- `sensory_system.py`: Dedicated sensory detection class managing touch/obstacle, light tiers, food proximity, anti-flooding cooldowns, and sensory rendering.
- `nervous_system.py`: Extended with visual sensory markers (`T`, `L`, `F`) and header telemetry on the neural grid.
- `main.py`: Updated game loop integrating sensory detection, keyboard handlers (`T`, `L`, `F`), environmental lighting, and HUD telemetry.
- `test_phase9_sensory.py`: Integration test suite validating the complete sensory pipeline and strict architectural constraints.
- `PHASE_HANDBOOK.md`: Living documentation and architectural reference.

---

## Phase 10 — Deep-Sea Environment

### 1. What Was Already Present
- **Sensory-to-Motor Neural Architecture**: Phase 8 and Phase 9 verified pipelines connecting mechanoreceptors, photoreceptors, and chemoreceptors to the 4×5 nerve net and 8 coronal bell muscles.
- **Visual Scene**: Basic Pygame window (1200×700), static random particles, static reef obstacle drawn in sensory system, and ambient lighting backdrop.
- **Controls**: Pause (`SPACE`), Reset (`R`), Stimulate (`S`), Touch (`T`), Light (`L`, `UP`, `DOWN`), Food (`F` or `Left Click`).

### 2. Environmental Properties Model
Phase 10 introduces a lightweight, biologically inspired physical environment in `environment.py`:
1. **Depth Profile ($y \in [120, 580]$)**:
   - Evaluated as normalized depth: $\text{norm\_depth} = \frac{y - 120}{460}$.
   - Depth scales from **200 m** (Epipelagic/sunlit boundary) down to **3,000 m** (Bathypelagic abyss at the seafloor).
2. **Hydrostatic Pressure**:
   - Follows oceanographic hydrostatic gradient: $P \approx 1 + \frac{\text{depth}}{10}$ atmospheres.
   - Ranges from **21 atm** near surface to **301 atm** in the abyss.
3. **Thermocline Temperature Gradient**:
   - Temperature follows a non-linear oceanic thermocline: $T = 20.0 - 16.0 \times \sqrt{\text{norm\_depth}}$ °C.
   - Ranges from a warm **20.0 °C** at shallow depths to a chilly **4.0 °C** at the bathyal seabed.
4. **Ambient Darkness**:
   - Monotonically increases with depth from **0.15** (surface twilight) to **1.0** (abyssal darkness).
5. **Dynamic Water Currents**:
   - 4 selectable current modes:
     - `Calm (0 px/s)`: Quiescent water.
     - `Eastward (+22 px/s)`: Steady laminar eastward current.
     - `Westward (-22 px/s)`: Steady laminar westward current.
     - `Tidal Swell`: Dynamic undulating current with horizontal oscillation ($26 \sin(0.75t + 0.004y)$) and subtle vertical surge ($5 \cos(0.5t)$).

### 3. Separation of Environmental Forces vs. Neural Swimming
A critical architectural constraint of Phase 10 is that environmental fluid forces must **never bypass or contaminate** the neural-to-muscle swimming pipeline:
- **Environmental Fluid Drag**: Applied as passive fluid advection in `jellyfish.py`:
  $$\Delta v_x = (v_{\text{current}, x} - v_x) \times 1.2 \times \Delta t$$
  $$\Delta v_y = (v_{\text{current}, y} - v_y) \times 0.6 \times \Delta t$$
- **Muscle-Driven Swimming Stroke**: Continues to be strictly generated by muscle contraction transitions:
  $$\text{impulse}_y = -220.0 \times \max(0.0, \text{contraction} - \text{prev\_contraction})$$
- Even when drifting at high speeds in strong currents, muscle contraction remains 0.0 unless neural signals fire from motor neurons 12–19.

### 4. Environmental Objects & Sensory Interactions
1. **Apex Deep-Sea Predator (`DeepSeaPredator`)**:
   - Sinuous, bioluminescent deep-sea cruising predator equipped with glowing eyes, lateral photophores, and an angler-like photophore lure.
   - Spawns and cruises across the ocean depths (spawned manually via `P`).
   - **Sensory Detection**: As the predator passes within mechanoreceptive wake range ($\le 175$ px), the jellyfish senses the fluid disturbance wave.
   - **Escape Reflex**: Directly stimulates `TOUCH_NEURON` (Neuron 0). The nerve net integrates the stimulus, propagates a wave to motor neurons 12–19, producing an emergency escape swimming contraction upward.
2. **Marine Snow & Food Advection**:
   - Suspended particulate marine snow in `environment.py` is dynamically advected by the local water current vectors while slowly settling down the water column, wrapping seamlessly across boundaries.
   - Planktonic food clusters placed by the user (`Left Click` or `F`) drift naturally with current velocities, creating a dynamic, living fluid environment.
3. **Bathymetric Seafloor & Hydrothermal Vent**:
   - Multi-point bathymetric seabed polygon and an active hydrothermal vent chimney with thermal shimmer, alongside the rocky reef shelf obstacle.

### 5. Interactive Keybindings & Controls Reference

| Input | Action | Effect |
| :---: | :--- | :--- |
| **`C`** | **Cycle Water Current Mode** | Toggles between *Calm* $\to$ *Eastward* $\to$ *Westward* $\to$ *Tidal Swell* |
| **`P`** | **Spawn Apex Predator Pass** | Predator cruises near the jellyfish's depth; triggers mechanoreceptor escape when in range |
| **`Left Click` (in water)** | Place Food | Spawns nutrient plankton at cursor; drifts with ambient currents |
| **`Left Click` (on jellyfish)** | Tactile Poke / Touch | Directly stimulates mechanoreceptor (Neuron 0) |
| **`F`** | Food at Mouse Cursor | Spawns food at cursor position |
| **`L`** | Cycle Ambient Light Tier | Stimulates Neuron 2 (*Abyss* $\to$ *Twilight* $\to$ *Shallows* $\to$ *Surface*) |
| **`UP` / `DOWN`** | Fine Adjust Light Brightness | Smoothly changes ambient illumination |
| **`T`** | Test Touch / Obstacle Contact | Stimulates Neuron 0 |
| **`S`** | Direct Neural Stimulus | Stimulates Neuron 0 |
| **`SPACE`** | Pause / Resume | Pauses physics and environment simulation |
| **`R`** | Reset Simulation | Resets jellyfish, nerve net, sensory state, and returns environment to calm state |

### 6. Testing & Verification Results

All tests were automated and verified via `test_phase10_environment.py`:

| Test Case | Description | Result | Details |
| :---: | :--- | :---: | :--- |
| **1** | Environmental Properties | **PASS** | Surface: 200m depth, 21 atm pressure, 20°C temp, 0.15 darkness. Seabed: 3000m depth, 301 atm pressure, 4°C temp, 1.0 darkness. Monotonic gradients confirmed. |
| **2** | Current Modes & Force Separation | **PASS** | Mode cycling verified. Eastward current induced horizontal drift ($v_x > 5$ px/s) with exactly 0.0 muscle contraction. Active motor firing independently generated strong vertical propulsion ($<-30$ px/s impulse). |
| **3** | Particle & Food Advection | **PASS** | Food cluster drifted $>10$ px with the eastward current over 1s. Marine snow advection and wrapping verified. |
| **4** | Predator Detection & Escape | **PASS** | Predator $>175$ px away did not stimulate; predator approaching within 100 px triggered mechanoreceptor (Neuron 0) $\to$ wave propagated to motor neurons 12–19 $\to$ peak contraction $>0.4$ $\to$ upward escape impulse. |
| **5** | Phase 8 & Phase 9 Regression Integrity | **PASS** | Stimulus propagation, bell contraction, light cycling, and reset mechanics validated with 100% pass rate. |
| **6** | Existing Unit Tests | **PASS** | `test_neuron.py`, `test_muscle.py`, `test_nervous_system.py`, `test_phase8_pipeline.py`, and `test_phase9_sensory.py` all pass cleanly. |

### 7. File Manifest

- `environment.py`: Environmental simulation module managing depth, pressure, temperature, dynamic current modes, marine snow advection, seafloor bathymetry, hydrothermal vents, and the `DeepSeaPredator` entity.
- `jellyfish.py`: Updated `update(dt, motor_activations, current_velocity=None)` to incorporate fluid drag while strictly preserving the muscle-driven swimming impulse mechanics.
- `sensory_system.py`: Integrated with `environment` for food advection with currents and mechanoreceptive predator wake detection.
- `main.py`: Integrated environment initialization, current cycling (`C`), predator passes (`P`), environment rendering, and comprehensive HUD telemetry.
- `test_phase10_environment.py`: Comprehensive test suite verifying environmental models, fluid drag separation, food/particle advection, predator detection, and regressions.
- `HANDBOOK.md` & `PHASE_HANDBOOK.md`: Updated comprehensive documentation.

---

## Phase 11 — Emergent Behavior

### 1. What Was Already Present
- **Sensory Systems (Phase 9)**: Multimodal sensory inputs (Touch -> N0, Light -> N2, Food -> N4).
- **Deep-Sea Environment (Phase 10)**: Depth profile (200m–3000m), hydrostatic pressure, thermocline temperature, darkness, dynamic water currents, seafloor bathymetry, and apex predator.
- **Neuromuscular Swimming Pipeline (Phase 8)**: 4×5 diffuse nerve net driving motor neurons 12–19, which contract 8 coronal muscles to produce upward propulsion.
- **Physical Drag vs. Swimming Force Separation**: Fluid drag operates independently from muscle power strokes.

### 2. The Problems Addressed in Phase 11
- Previously, the jellyfish could only pulse straight upwards vertically. Even when sensing food to its left or right, it could not steer or approach it.
- Obstacle contact and predator wake triggered generic upward strokes without directional evasion or spatial awareness.
- When left without stimuli, passive negative buoyancy caused the jellyfish to sink indefinitely to the seafloor boundary.

### 3. Biological Mechanisms & Behavioral Rules Added

#### A. Asymmetrical Lateral Muscle Propulsion (Biological Steering)
In real cnidarians (*Scyphozoa* and *Hydrozoa*), steering is an emergent consequence of asymmetrical wave arrival times and contraction across the circular coronal muscle margin:
- Each of the 8 muscle sectors around the bell is assigned a lateral impulse weight $w_i \in [-0.75, +0.375]$ corresponding to its lateral position along the margin.
- **Zero Lateral Force on Symmetrical Strokes**:
  $$\sum_{i=0}^7 w_i = (-0.75) + (-0.75) + 0 + 0 + 0.375 \times 4 = \mathbf{0.0000}$$
  When stimulated centrally or uniformly (e.g. Center Light N2, or manual S), all muscles contract symmetrically, generating **0.0 lateral thrust** and swimming straight up.
- **Emergent Lateral Thrust on Unilateral Waves**:
  When a wave sweeps from the right (Neuron 4), right-side motor neurons (13, 14, 18, 19) fire several frames before the left side, causing the right margin to contract earlier and more strongly:
  $$\Delta v_x = 800.0 \times \sum_{i=0}^7 w_i \cdot \max(0, c_i - c_{i, \text{prev}})$$
  This produces a positive horizontal impulse ($\Delta v_x > 0$), steering the jellyfish gracefully to the **right**. Conversely, waves from the left (Neuron 0) steer the jellyfish to the **left** ($\Delta v_x < 0$).
- **Visual Orientation Tilt**: The bell dome and tentacles organically bank into turns based on horizontal velocity:
  $$\theta_{\text{target}} = \text{clamp}(v_x \times 0.005, -0.25, +0.25) \text{ rad}$$

#### B. Omnidirectional 360° Swimming & Heading Physics
- **Heading Vector Representation**:
  In Pygame, the screen coordinate system has $y$ increasing downwards. The jellyfish maintains its physical orientation $\theta$ (in radians), where:
  - $\theta = 0$: pointing straight UP (default stance) $\to \vec{h} = (0, -1)$
  - $\theta = \pi/2$: pointing RIGHT $\to \vec{h} = (1, 0)$
  - $\theta = -\pi/2$: pointing LEFT $\to \vec{h} = (-1, 0)$
  - $\theta = \pm\pi$: pointing straight DOWN $\to \vec{h} = (0, 1)$
  - General heading unit vector: $\vec{h} = (\sin\theta, -\cos\theta)$
- **Biological Power Stroke Along Heading**:
  When bell muscles contract ($\Delta c = \max(0, c - c_{\text{prev}}) > 0$), the water jet expelled from the subumbrella margin produces equal-and-opposite thrust along the bell's current heading:
  $$\Delta v_x = 220.0 \times \Delta c \times \sin(\theta)$$
  $$\Delta v_y = 220.0 \times \Delta c \times (-\cos(\theta))$$
  *(When $\theta = 0$, $\Delta v_x = 0$ and $\Delta v_y = -220.0 \times \Delta c$, maintaining 100% backward compatibility with Phase 8).*
- **Smooth Biological Reorientation**:
  Sensory systems and righting statoliths steer `target_orientation`. The body smoothly rotates into alignment:
  $$\text{diff} = (\theta_{\text{target}} - \theta + \pi) \pmod{2\pi} - \pi$$
  $$\Delta \theta = \text{clamp}(\text{diff} \times 4.8 \times \Delta t, -4.8 \times \Delta t, 4.8 \times \Delta t)$$
- **Full 360° Visual Rotation**:
  The bell dome polygon, margin rim, and all 7 trailing tentacles dynamically rotate around the bell center $(x, y)$ by $\theta$.

#### C. Emergent Chemotaxis (Autonomous Food Approach & Capture in Any Direction)
- In real jellyfish, chemical receptors across marginal rhopalia detect chemical scent gradients from any direction in the water column ($r \le 300$ px).
- The jellyfish calculates target heading to the food $\theta_{\text{food}} = \text{atan2}(dx, -dy)$ and sets `target_orientation`:
  - **Food to the Right of Heading** ($\text{diff} > 0.2$ rad): Stimulates right rhopalium (Neuron 4) $\to$ sweeps wave through right muscles $\to$ banks and steers right.
  - **Food to the Left of Heading** ($\text{diff} < -0.2$ rad): Stimulates left rhopalium (Neuron 0) $\to$ sweeps wave through left muscles $\to$ banks and steers left.
  - **Food Dead Ahead** ($|\text{diff}| \le 0.2$ rad): Stimulates center apical organ (Neuron 2) $\to$ bilateral power stroke propels the jellyfish directly into the food.
- The jellyfish rhythmically pulses, turns, closes the distance in any 2D direction (Above, Below, Left, Right, Diagonals), and ingests the food upon reaching within $42$ px with a shower of golden sparkling particles.
- **Zero Movement Shortcuts**: No artificial pathfinding or velocity overrides exist. Movement toward food is 100% driven by neural wave propagation and muscle contraction transitions.

#### D. Obstacle Avoidance
- When the bell collides with the rocky reef shelf obstacle or boundaries, tactile mechanoreceptors fire, producing an immediate escape swimming stroke that lifts the jellyfish above and away from the substrate.
- Paced anti-flooding cooldown prevents perpetual excitation loops while touching objects.

#### E. Predator Evasion Burst
- When an apex predator approaches within the $175$ px sensory wake horizon, mechanoreceptors detect the high-amplitude pressure disturbance.
- Triggers an urgent high-intensity escape reflex (`TOUCH_NEURON` at strength 85.0) directed toward the surface (`target_orientation = 0.0`), initiating a rapid vertical escape burst that propels the jellyfish upward and out of the predator's horizontal cruise corridor ($v_y < -100$ px/s).

#### F. Statocyst Depth Equilibrium (Baroreception)
- In the deep bathyal zone ($y > 480$ px / depth $> 2400$ m, pressure $> 240$ atm), deep-sea medusae use statocysts (gravity/balance sensory organs) to avoid sinking into the abyssal benthos.
- If negative buoyancy causes the resting jellyfish to sink below $480$ px, the statocyst triggers a paced compensatory recovery stroke (Neuron 2, cooldown $2.4$s).
- This produces emergent **mesopelagic depth maintenance**, keeping the jellyfish suspended in its preferred midwater zone ($y \sim 300 - 380$ px) without human intervention.
- In comfortable midwater with no active stimuli, the simulation enters **Quiescent Drift**.

---

### 4. Visual Feedback & HUD Interface

The HUD displays the active emergent behavioral state in real time:
- `Behavior: Chemotaxis (Steering Right)` / `Chemotaxis (Steering Left)` / `Chemotaxis (Approaching Food)`
- `Behavior: Predator Evasion (Escape Burst)`
- `Behavior: Obstacle Avoidance (Escape Stroke)`
- `Behavior: Depth Equilibrium (Statocyst Pulse)`
- `Behavior: Quiescent Drift`
- `Behavior: Food Ingested!`

---

### 5. Testing & Verification Results

All emergent behaviors and architectural constraints were verified via `test_phase11_emergent.py`:

| Test Case | Description | Result | Details |
| :---: | :--- | :---: | :--- |
| **1** | Differential Muscle Steering | **PASS** | Neuron 4 steered right ($dx = +10.18$ px, $dy = -55.46$ px). Neuron 0 steered left ($dx = -7.28$ px, $dy = -55.41$ px). Neuron 2 swam vertically ($dx = 1.42$ px, $dy = -56.28$ px). |
| **2** | Emergent Chemotaxis (Right & Left) | **PASS** | Food placed at right was captured at step 29 (pos: 635.4, 347.4); food placed at left was captured at step 31 (pos: 573.4, 342.2). Ingestion particles confirmed. |
| **3** | Obstacle Avoidance & Predator Evasion | **PASS** | Obstacle collision triggered avoidance; predator wake triggered emergency burst reaching peak escape velocity of $-106.5$ px/s. |
| **4** | Statocyst Depth Equilibrium | **PASS** | Sinking to $y=510$ px triggered statocyst recovery pulse reaching $-72.6$ px/s; midwater resting state returned to Quiescent Drift. |
| **5** | Zero Movement Shortcuts | **PASS** | Disconnecting motor activations produced $0.00000$ movement change toward food, confirming strict neural transmission dependence. |
| **6** | Omnidirectional 360° Swimming (All Directions) | **PASS** | Successfully navigated to and captured food in all 6 test vectors: **Above** (step 99), **Right** (step 42), **Left** (step 56), **Below** (step 191), **Down-Right** (step 138), **Down-Left** (step 130). |

---

### 6. File Manifest

- `jellyfish.py`: Added `target_orientation`, heading vector $\vec{h} = (\sin\theta, -\cos\theta)$ omnidirectional power stroke, differential muscle lateral impulse calculation, smooth angular turning, and 360° rotated polygon rendering.
- `sensory_system.py`: Implemented omnidirectional chemotaxis targeting in all 360° directions, statocyst depth regulation, obstacle avoidance responses, and active behavioral state tracking.
- `nervous_system.py`: Standardized default stimulus strength to 80.0 for reliable first-frame firing across all framerates.
- `main.py`: Updated HUD status bar to display real-time active emergent behavior and directional food placement.
- `test_phase11_emergent.py`: Dedicated automated test suite verifying differential steering, chemotaxis, predator evasion, depth equilibrium, shortcut absence, and full 360° omnidirectional swimming.
- `HANDBOOK.md` & `PHASE_HANDBOOK.md`: Comprehensive documentation updated.

---

## Deep-Sea Masterpiece Upgrade — Bioluminescent Anatomy, Ecosystem & Electrophysiology

### 1. What Was Already Present
- Verified Phase 8–11 neuromuscular pipeline: 4×5 diffuse nerve net driving 8 coronal muscles.
- Omnidirectional 360° heading physics and rotational rendering.
- 3 sensory modalities (mechanoreceptors, photoreceptors, chemoreceptors) and dynamic ocean environment.
- Baseline automated test suites (Tests 1–7) passing with 100% regression integrity.

---

### 2. Architectural Upgrades & Biological Mechanisms Added

#### A. Bioluminescent Internal Anatomy & Translucent Bell (`jellyfish.py`)
- **Layered Bell Dome**: Exumbrella (outer dome) and subumbrella (inner cavity) rendered with alpha transparency and subtle deep-sea shading.
- **Central Manubrium (Gastric Stomach Cavity)**: Suspended inside the subumbrella, featuring an oral cone that houses captured prey.
- **4 Frilly Oral Arms**: Delicate central feeding arms that wave with sinusoidal fluid dynamics to guide plankton into the mouth.
- **8 Radial Canals & Coronal Photophores**: Connecting the central gastric pouch to the 8 marginal rhopalia. When motor neurons (12–19) fire, the active radial canals flash with brilliant GFP cyan/green bioluminescence (`(50, 255, 210)`).
- **8 Marginal Rhopalia**: Glowing pacemaker/sensory bulbs at the bell margin that pulse with bioluminescent light.
- **Hydrodynamic Wake Vortices**: Power stroke contractions shed counter-rotating vortex rings of glowing particles trailing opposite to the heading vector that drift and dissipate in the fluid currents.

#### B. Metabolism, Digestion & Plankton Swarm Ecosystem (`sensory_system.py` & `jellyfish.py`)
- **Metabolic ATP Energy Reserve**: Jellyfish maintains an energy store (initialized at $85\%$, max $100\%$). Bell contraction power strokes consume subtle metabolic ATP ($0.4 \times \Delta c$).
- **Bioluminescent Copepod Plankton Swarms**: Clicking the ocean or pressing `F` spawns a natural cluster of 5 shimmering copepod micro-organisms equipped with twinkling bioluminescent photophores.
- **Gastric Digestion & Energy Recovery**: When the jellyfish reaches within $42$ px, the plankton swarm is ingested into the central manubrium. Food boluses glow warmly inside the translucent stomach cavity and digest over several seconds, replenishing ATP energy to $100\%$.

#### C. Live Patch-Clamp Electrophysiology Oscilloscope & Micro-Electrode Lab (`nervous_system.py` & `main.py`)
- **Dual-Channel Patch-Clamp Oscilloscope**: Rendered directly on-screen in a sleek glass panel with millivolt calibration reticles:
  - **CH1 (Amber/Gold)**: Sensory Input Channel ($V_m(t)$ of Sensory Neuron 0).
  - **CH2 (Neon Cyan)**: Motor Output Channel ($V_m(t)$ of Motor Neuron 12).
  - Displays the continuous biological action potential waveform: resting potential, depolarization ramp, action potential spike peak ($>1.2$V) crossing the $1.0$V threshold line, and hyperpolarizing refractory dip.
- **Interactive Micro-Electrode Current Injection**: Clicking on **any** of the 20 neurons in the 4×5 nerve net grid injects a depolarizing current pulse directly into that neuron, allowing users to initiate custom traveling waves and explore neural net topologies in real time.

---

### 3. Interactive Controls Reference

| Input | Action | Effect |
| :---: | :--- | :--- |
| **`Click Ocean`** | **Spawn Plankton Swarm** | Spawns a cluster of 5 bioluminescent copepods; drifts with ambient water currents |
| **`Click Jellyfish`** | **Tactile Poke** | Stimulates mechanoreceptors (Neuron 0); triggers escape contraction |
| **`Click Neuron`** | **Micro-Electrode Pulse** | Injects depolarizing stimulus current directly into any clicked neuron in the grid |
| **`C`** | Cycle Water Currents | Toggles between *Calm* $\to$ *Eastward* $\to$ *Westward* $\to$ *Tidal Swell* |
| **`P`** | Predator Cruise Pass | Apex predator cruises near jellyfish depth; triggers vertical escape reflex |
| **`L` / `UP` / `DOWN`** | Ambient Light Tuning | Cycles photic tiers or smoothly adjusts ambient oceanic illumination |
| **`SPACE`** | Pause / Resume | Freezes/unfreezes physics and neural propagation |
| **`R`** | Reset Simulation | Restores initial state, quiescent drift, and calm waters |

---

### 4. Verification & Testing Results (`test_upgrade_masterpiece.py`)

| Test Case | Description | Result | Details |
| :---: | :--- | :---: | :--- |
| **1** | Bioluminescent Anatomy & Radial Canals | **PASS** | Motor neuron 12 fired $\to$ radial canal 0 flashed bioluminescent glow ($0.98$) $\to$ peak contraction $0.239$. |
| **2** | Hydrodynamic Wake Vortices | **PASS** | Power stroke shed $16$ vortex particles opposite to heading; particles dissipated to $0$ over their lifespan. |
| **3** | ATP Metabolism & Gastric Digestion | **PASS** | Swimming consumed ATP ($85.0\% \to 84.2\%$); feeding deposited $4$ digesting boluses and restored energy to $100.0\%$. |
| **4** | Patch-Clamp Oscilloscope & Micro-Electrode | **PASS** | Micro-electrode hit testing verified on N0 and N12; oscilloscope recorded action potential spike peak of $1.25$V crossing threshold. |
| **5** | Plankton Swarm Chemotaxis | **PASS** | Jellyfish steered towards swarm, captured it at step 21, and ingested plankton into gastric cavity. |
| **6** | Full Regression Suite (All 8 Tests) | **PASS** | `test_neuron`, `test_muscle`, `test_nervous_system`, `test_phase8`, `test_phase9`, `test_phase10`, `test_phase11`, and `test_upgrade_masterpiece` all passed 100%. |

---

### 5. File Manifest

- `jellyfish.py`: Implemented layered translucent bell, glowing radial canals, central manubrium stomach, 4 oral arms, hydrodynamic wake vortices, and ATP energy digestion.
- `sensory_system.py`: Upgraded food cue into a bioluminescent copepod plankton swarm with glowing photophores, and connected feeding to jellyfish digestion.
- `nervous_system.py`: Implemented real-time dual-channel patch-clamp electrophysiology oscilloscope and micro-electrode neuron hit testing.
- `main.py`: Connected micro-electrode neuron clicking, ocean plankton placement, and updated HUD telemetry with ATP energy status.
- `test_upgrade_masterpiece.py`: Automated test suite verifying all 5 core upgrade features.
- `HANDBOOK.md` & `PHASE_HANDBOOK.md`: Comprehensive documentation updated.

---

## Phase 12 — The Educational Passion Project: How a Jellyfish Works Without a Brain

### 1. The Core Scientific Premise
Jellyfish (*Cnidaria: Medusozoa*) have thrived for over **500 million years** without a centralized brain, cerebral cortex, spinal cord, or heart. Phase 12 transforms this simulation into a museum-grade interactive educational experience that explains and demonstrates the true neurobiology and biomechanics of life without a brain:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DECENTRALIZED INTELLIGENCE                           │
│                      (Life Without a Central Brain)                         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
     ┌─────────────────────────────────┼─────────────────────────────────┐
     ▼                                 ▼                                 ▼
┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐
│  8 Marginal Rhopalia   │  │ Diffuse Nerve Net (DNN)│  │ Coronal Muscle Ring &  │
│  • Statolith gravity   │  │ • Bidirectional synapses│ │   Elastic Mesoglea     │
│  • Decentralized       │  │ • 0.15s refractory gate│  │ • Toroidal vortex jet  │
│    pacemaker rhythm    │  │ • Forward wave sweeps  │  │ • 0-ATP spring recoil  │
│  • Rhopalial ocelli    │  │ • Hodgkin-Huxley mV    │  │ • Re ~ 150-4500 flow   │
└────────────────────────┘  └────────────────────────┘  └────────────────────────┘
```

---

### 2. Features Implemented in Phase 12

#### A. Interactive "Neurobiology Academy" Field Guide (`educational_guide.py`)
- **5-Chapter Interactive Modal (Press `E` or `TAB` or Click `[FIELD GUIDE]`):**
  1. **No Brain Paradigm**: Embodied computation, damage resilience, and evolutionary history of decentralized nervous systems.
  2. **Rhopalia & Sensors**: The 8 marginal sensory clubs, calcium-carbonate statolith gravity sensing, and decentralized pacemaker rhythm entrainment.
  3. **Nerve Net Waves & Gating**: Bidirectional unpolarized synapses, action potential depolarization/repolarization, and how refractory gating prevents lethal epileptiform echo loops.
  4. **Vortex Propulsion**: Elastic mesoglea spring recoil (zero-ATP bell re-expansion), and toroidal starting & stopping vortex rings.
  5. **Gastrovascular Cavity**: Central manubrium ingestion and nutrient distribution through 8 radial canals without blood vessels or organs.

#### B. Dynamic Anatomical Callout Pins (`[ANATOMY: A]`)
- Anchors 7 glowing, interactive pins directly to the transformed coordinates of the moving jellyfish:
  - `Exumbrella Mesoglea Dome` (Passive elastic spring matrix)
  - `Subumbrella & Coronal Muscles` (Striated circular power stroke effectors)
  - `Marginal Rhopalia (8x)` (Decentralized pacemakers + statocysts + ocelli)
  - `8 Radial Canals` (Gastrovascular circulatory conduits)
  - `Manubrium & Gastric Cavity` (Central digestive organ)
  - `Frilly Oral Arms (4x)` (Prey capture and transport)
  - `Marginal Tentacles` (Mechanoreceptive fluid sensors)
- Hovering or clicking any pin displays a sleek floating scientific card with leader lines and biological explanations.

#### C. Guided Educational Lessons & Experiments (Keys `1` to `5`)
- **Lesson 1 (Key `1`)**: *Rhopalial Pacemaker Wave* — triggers decentralized pacemaker oscillation, demonstrating action potential wave propagation across the net to coronal muscles.
- **Lesson 2 (Key `2`)**: *Statolith Gravity Righting Reflex* — tilts the bell 55°, showing statolith crystal shift and unilateral corrective steering thrust.
- **Lesson 3 (Key `3`)**: *Tactile Noxious Evasion* — mechanoreceptor contact triggers an explosive escape jet burst.
- **Lesson 4 (Key `4`)**: *Chemotaxis & Gastric Digestion* — spawns plankton, demonstrating chemical gradient navigation, oral arm capture, and glowing gastrovascular distribution.
- **Lesson 5 (Key `5`)**: *Electrophysiology Micro-Probe* — patch-clamp current injection with millivolt Hodgkin-Huxley spike curve analysis.

#### D. Time Dilation Controls (Key `Z` / Dock Button)
- Cycles simulation speed between **1.0x (Realtime)**, **0.5x (Half-Speed)**, and **0.25x (Quarter-Speed)** to observe action potential conduction and fluid vortex rings in slow-motion detail.

#### E. Living Benthic Deep-Sea Ecosystem (`environment.py`)
- **Benthic Sea-Pens / Polyps**: Glowing colonial cnidarians rooted to the seabed that softly sway with water currents and bioluminesce.
- **Hydrothermal Vent Chimney**: Billowing convective smoke plume with buoyant rising mineral ash and cooling particles.
- **Background Ctenophores**: Passive comb jellies (*Beroe*) drifting in the distant ocean with shimmering iridescent rainbow cilia.
- **3-Layer Parallax Marine Snow**: Denser, multi-layered organic particles drifting with fluid velocity vectors.

#### F. Biomechanical & Hydrodynamic Telemetry
- Integrated real-time card displaying:
  - **Reynolds Number ($\mathrm{Re}$)**: Computed from physical fluid properties ($\rho = 1025\text{ kg/m}^3, \mu = 0.0014\text{ Pa}\cdot\text{s}$) in the transitional regime ($\mathrm{Re} \sim 150 - 4500$).
  - **Jet Thrust Force**: Instantaneous momentum impulse ($F_{\text{thrust}}$ in $\mathrm{mN}$).
  - **Mesoglea Strain**: Percentage deformation of the elastic bell.
  - **Patch-Clamp Oscilloscope**: Millivolt-calibrated dual traces ($-70\text{ mV}$ resting, $-55\text{ mV}$ threshold, $+30\text{ mV}$ peak, $-80\text{ mV}$ hyperpolarization).

---

### 3. Verification & Testing (`test_phase12_educational.py`)

| Test | Objective | Status | Result |
| :---: | :--- | :---: | :--- |
| **1** | Educational Guide Tabs & Content | **PASS** | 5 tabs verified; modal toggle and layout verified. |
| **2** | Anatomical Pins & Coordinate Transformation | **PASS** | 7 biological pins verified; hover & hit testing verified. |
| **3** | Time Dilation Speeds | **PASS** | 1.0x $\to$ 0.5x $\to$ 0.25x $\to$ 1.0x verified. |
| **4** | Guided Educational Lessons (1–5) | **PASS** | All 5 lessons trigger designated biological events and auto-conclude. |
| **5** | Biomechanical & Telemetry Metrics | **PASS** | Reynolds number, mesoglea strain, and thrust force confirmed. |
| **6** | Living Benthic Ecosystem | **PASS** | Sea-pens, vent ash particles, and ctenophores verified. |

---

### 4. Interactive Keyboard & Mouse Quick Reference

| Control | Action | Function |
| :---: | :--- | :--- |
| **`E` / `TAB`** | Toggle Field Guide | Opens 5-tab educational modal explaining brainless neurobiology |
| **`A`** | Toggle Anatomy Pins | Displays interactive anatomical callouts anchored to the jellyfish |
| **`Z`** | Time Dilation | Cycles simulation speed: 1.0x $\to$ 0.5x $\to$ 0.25x (slow-motion) |
| **`1` – `5`** | Launch Guided Lesson | Demonstrates Pacemaker, Statolith, Escape, Digestion, or Electrophysiology |
| **`Click Ocean`** | Plankton Swarm | Spawns bioluminescent copepods drifting in ocean currents |
| **`Click Jelly`** | Tactile Poke | Stimulates mechanoreceptor Neuron 0 |
| **`Click Neuron`**| Micro-Electrode | Injects depolarizing current pulse into any clicked neuron in the grid |
| **`C`** | Cycle Water Current | Calm $\to$ Eastward $\to$ Westward $\to$ Tidal Swell |
| **`P`** | Deep-Sea Predator | Viperfish cruises through; triggers escape burst |
| **`L` / `↑` / `↓`**| Ambient Light | Cycles photic depth zones or dims/brightens water column |
| **`SPACE`** | Pause / Resume | Freezes/unfreezes simulation |
| **`R`** | Reset Simulation | Restores initial conditions |


