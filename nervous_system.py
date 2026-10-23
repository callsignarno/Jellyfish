import collections
import pygame
from neuron import Neuron


class NervousSystem:
    """
    Biological 4x5 Diffuse Nerve Net (DNN) & Patch-Clamp Electrophysiology.
    
    Structure:
      - Row 0: Sensory Receptors (0=Touch Mechanoreceptor, 2=Apical Ocellus, 4=Chemoreceptor)
      - Row 1: Interneuron Processing Network
      - Rows 2 & 3: Coronal Motor Neurons / Rhopalia Pacemakers (12-19)
    
    Features:
      - Bidirectional electrical & chemical synapses
      - 0.15s refractory hyperpolarization enforcing forward traveling wave propagation
      - Dual-channel real-time patch clamp electrophysiology oscilloscope (-80 mV to +30 mV)
      - Interactive micro-electrode stimulation hit-testing
    """

    def __init__(self, rows=4, cols=5, signal_strength=1.0):
        self.rows = rows
        self.cols = cols
        self.signal_strength = signal_strength

        # Use 0.15s refractory period to gate clean forward traveling waves
        self.neurons = [
            Neuron(refractory_period=0.15)
            for _ in range(rows * cols)
        ]

        self.build_connections()

        # Grid geometry for HUD display & micro-electrode clicks
        self.grid_x = 980
        self.grid_y = 75
        self.spacing = 38
        self.node_radius = 8

        # Electrophysiology Patch-Clamp Oscilloscope Traces
        # CH1: Sensory Receptor (Neuron 0), CH2: Coronal Motor (Neuron 12)
        self.osc_maxlen = 120
        self.trace_ch1 = collections.deque([0.0] * self.osc_maxlen, maxlen=self.osc_maxlen)
        self.trace_ch2 = collections.deque([0.0] * self.osc_maxlen, maxlen=self.osc_maxlen)
        self.sample_timer = 0.0

    def get_index(self, row, col):
        return row * self.cols + col

    def build_connections(self):
        for row in range(self.rows):
            for col in range(self.cols):
                neuron = self.neurons[self.get_index(row, col)]

                if row > 0:
                    neuron.connect(self.neurons[self.get_index(row - 1, col)])
                if row < self.rows - 1:
                    neuron.connect(self.neurons[self.get_index(row + 1, col)])
                if col > 0:
                    neuron.connect(self.neurons[self.get_index(row, col - 1)])
                if col < self.cols - 1:
                    neuron.connect(self.neurons[self.get_index(row, col + 1)])

    def stimulate(self, index, strength=80.0):
        """Apply a brief external stimulus to one neuron."""
        if 0 <= index < len(self.neurons):
            self.neurons[index].add_input(strength)

    def get_neuron_at(self, mx, my):
        """Hit test for micro-electrode stimulation: returns neuron index or None."""
        for index in range(len(self.neurons)):
            row = index // self.cols
            col = index % self.cols
            nx = self.grid_x + col * self.spacing
            ny = self.grid_y + row * self.spacing
            if (mx - nx) ** 2 + (my - ny) ** 2 <= (self.node_radius + 7) ** 2:
                return index
        return None

    def update(self, dt):
        for neuron in self.neurons:
            neuron.update(dt)

        for neuron in self.neurons:
            neuron.propagate(signal=self.signal_strength)

        # Record continuous membrane potential for the patch-clamp oscilloscope
        # Display spike peak (1.25V) when action potential fires
        v1 = self.neurons[0].membrane_potential
        if self.neurons[0].fired:
            v1 = 1.25
        elif self.neurons[0].refractory_timer > 0:
            v1 = -0.15

        v2 = self.neurons[12].membrane_potential
        if self.neurons[12].fired:
            v2 = 1.25
        elif self.neurons[12].refractory_timer > 0:
            v2 = -0.15

        self.trace_ch1.append(v1)
        self.trace_ch2.append(v2)

    def draw(self, surface, telemetry_data=None):
        spacing = self.spacing
        start_x = self.grid_x
        start_y = self.grid_y
        radius = self.node_radius

        mx, my = pygame.mouse.get_pos()
        hovered_idx = self.get_neuron_at(mx, my)

        # -------------------------
        # Glass Panel Backdrop for Nerve Net
        # -------------------------
        panel_w, panel_h = 216, 175
        net_panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        net_panel.fill((10, 20, 32, 225))
        pygame.draw.rect(net_panel, (45, 95, 135, 230), (0, 0, panel_w, panel_h), 1, border_radius=8)
        surface.blit(net_panel, (start_x - 18, start_y - 28))

        label_font = pygame.font.Font(None, 18)
        hdr_font = pygame.font.Font(None, 19)

        # Header Title
        title_surf = hdr_font.render("DIFFUSE NERVE NET (DNN)", True, (135, 215, 255))
        surface.blit(title_surf, (start_x - 10, start_y - 22))

        # Sensory row annotation
        sens_annot = label_font.render("Sensory Row (0)", True, (180, 195, 210))
        surface.blit(sens_annot, (start_x + 85, start_y - 6))

        # Motor row annotation
        mot_annot = label_font.render("Motor Neurons (12-19)", True, (100, 190, 220))
        surface.blit(mot_annot, (start_x + 45, start_y + 3 * spacing + 12))

        # -------------------------
        # Synaptic Connections & Traveling Action Potential Waves
        # -------------------------
        for index, neuron in enumerate(self.neurons):
            row = index // self.cols
            col = index % self.cols
            x = start_x + col * spacing
            y = start_y + row * spacing

            for connected_neuron in neuron.connections:
                other_index = self.neurons.index(connected_neuron)
                other_row = other_index // self.cols
                other_col = other_index % self.cols

                other_x = start_x + other_col * spacing
                other_y = start_y + other_row * spacing

                syn_active = neuron.activity > 0.08 or connected_neuron.activity > 0.08
                syn_col = (90, 195, 255) if syn_active else (32, 50, 72)
                pygame.draw.line(
                    surface,
                    syn_col,
                    (x, y),
                    (other_x, other_y),
                    2 if syn_active else 1
                )

                # Traveling wave spark along active synapse
                if neuron.fired:
                    spark_x = int(x + (other_x - x) * 0.45)
                    spark_y = int(y + (other_y - y) * 0.45)
                    pygame.draw.circle(surface, (255, 255, 200), (spark_x, spark_y), 3)

        # -------------------------
        # Neurons Rendering
        # -------------------------
        for index, neuron in enumerate(self.neurons):
            row = index // self.cols
            col = index % self.cols
            x = start_x + col * spacing
            y = start_y + row * spacing

            # Sensory Nodes Accent Badges
            if index == 0:
                pygame.draw.circle(surface, (245, 160, 60), (x, y), radius + 3, 1)
                surface.blit(label_font.render("T", True, (255, 175, 75)), (x - 4, y - 18))
            elif index == 2:
                pygame.draw.circle(surface, (250, 225, 80), (x, y), radius + 3, 1)
                surface.blit(label_font.render("L", True, (255, 230, 90)), (x - 3, y - 18))
            elif index == 4:
                pygame.draw.circle(surface, (80, 235, 160), (x, y), radius + 3, 1)
                surface.blit(label_font.render("F", True, (90, 240, 170)), (x - 3, y - 18))
            elif index >= 12:
                # Motor Neurons
                pygame.draw.circle(surface, (60, 180, 220), (x, y), radius + 3, 1)

            # Micro-electrode hover indicator
            if hovered_idx == index:
                pygame.draw.circle(surface, (255, 245, 130), (x, y), radius + 5, 2)

            # Membrane Potential Color Dynamics
            if neuron.fired:
                color = (55, 255, 160)
            elif neuron.activity > 0:
                glow = neuron.activity
                color = (
                    int(45 + 30 * glow),
                    int(80 + 170 * glow),
                    int(120 + 135 * glow)
                )
            elif neuron.membrane_potential > 0:
                color = (65, 165, 255)
            else:
                color = (48, 65, 85)

            pygame.draw.circle(surface, color, (x, y), radius)

        # -------------------------
        # Dual-Channel Patch-Clamp Oscilloscope
        # -------------------------
        self.draw_oscilloscope(surface, ox=start_x - 18, oy=start_y + panel_h - 18, ow=216, oh=148)

        # -------------------------
        # Biomechanical & Telemetry Card
        # -------------------------
        if telemetry_data:
            self.draw_telemetry_card(surface, ox=start_x - 18, oy=start_y + panel_h + 138, ow=216, oh=112, data=telemetry_data)

    def draw_oscilloscope(self, surface, ox, oy, ow, oh):
        """Draw dual-channel real-time membrane potential voltage waveforms in millivolts."""
        panel = pygame.Surface((ow, oh), pygame.SRCALPHA)
        panel.fill((10, 20, 32, 225))
        pygame.draw.rect(panel, (45, 95, 135, 230), (0, 0, ow, oh), 1, border_radius=8)

        # Biological Reticle Lines (mV)
        # 0.0 -> y_rest (-70 mV), 1.0 -> y_thresh (-55 mV), 1.25 -> y_spike (+30 mV)
        y_zero = int(oy + oh * 0.72)
        y_thresh = int(oy + oh * 0.32)
        y_spike = int(oy + oh * 0.16)

        # Baseline V_rest (-70 mV)
        pygame.draw.line(surface, (35, 65, 95), (ox + 10, y_zero), (ox + ow - 10, y_zero), 1)
        # Firing Threshold V_thresh (-55 mV / 1.0V) dashed red
        for dx in range(ox + 10, ox + ow - 10, 8):
            pygame.draw.line(surface, (200, 70, 70), (dx, y_thresh), (dx + 4, y_thresh), 1)

        surface.blit(panel, (ox, oy))

        osc_font = pygame.font.Font(None, 16)
        hdr_font = pygame.font.Font(None, 18)

        title_txt = hdr_font.render("PATCH-CLAMP OSCILLOSCOPE", True, (135, 215, 255))
        # Real-time digital readouts in millivolts
        latest_v1 = self.trace_ch1[-1] if self.trace_ch1 else 0.0
        latest_v2 = self.trace_ch2[-1] if self.trace_ch2 else 0.0
        mv1 = -70.0 + latest_v1 * 80.0
        mv2 = -70.0 + latest_v2 * 80.0

        ch1_txt = osc_font.render(f"CH1 N0: {mv1:+.0f} mV", True, (250, 185, 75))
        ch2_txt = osc_font.render(f"CH2 N12: {mv2:+.0f} mV", True, (50, 245, 205))
        thresh_txt = osc_font.render("Threshold", True, (220, 85, 85))

        surface.blit(title_txt, (ox + 10, oy + 8))
        surface.blit(ch1_txt, (ox + 10, oy + 24))
        surface.blit(ch2_txt, (ox + 115, oy + 24))
        surface.blit(thresh_txt, (ox + ow - 65, y_thresh - 10))

        # Plot waveforms
        def v_to_y(v):
            return int(y_zero - (v / 1.0) * (y_zero - y_thresh))

        pts_ch1 = []
        pts_ch2 = []
        step_x = (ow - 20) / (self.osc_maxlen - 1)
        for i, (v1, v2) in enumerate(zip(self.trace_ch1, self.trace_ch2)):
            px = int(ox + 10 + i * step_x)
            pts_ch1.append((px, v_to_y(v1)))
            pts_ch2.append((px, v_to_y(v2)))

        if len(pts_ch1) > 1:
            pygame.draw.lines(surface, (250, 185, 75), False, pts_ch1, 2)
            pygame.draw.lines(surface, (50, 245, 205), False, pts_ch2, 2)

    def draw_telemetry_card(self, surface, ox, oy, ow, oh, data):
        """Draw real-time biomechanical and hydrodynamics metrics."""
        panel = pygame.Surface((ow, oh), pygame.SRCALPHA)
        panel.fill((10, 20, 32, 225))
        pygame.draw.rect(panel, (45, 95, 135, 230), (0, 0, ow, oh), 1, border_radius=8)
        surface.blit(panel, (ox, oy))

        f_hdr = pygame.font.Font(None, 18)
        f_lbl = pygame.font.Font(None, 16)

        title = f_hdr.render("BIOMECHANICS & FLUID METRICS", True, (135, 215, 255))
        surface.blit(title, (ox + 10, oy + 8))

        re_txt = f_lbl.render(f"Reynolds No (Re):  {data.get('re', 210):.0f} (Transitional)", True, (200, 230, 255))
        thrust_txt = f_lbl.render(f"Jet Thrust Force:    {data.get('thrust_mn', 0.0):.1f} mN", True, (100, 240, 210))
        strain_txt = f_lbl.render(f"Mesoglea Strain:   {data.get('strain_pct', 0.0):.1f} %", True, (245, 215, 95))
        atp_txt = f_lbl.render(f"Metabolic ATP:       {data.get('energy', 85.0):.0f} %", True, (255, 180, 110))

        surface.blit(re_txt, (ox + 10, oy + 28))
        surface.blit(thrust_txt, (ox + 10, oy + 48))
        surface.blit(strain_txt, (ox + 10, oy + 68))
        surface.blit(atp_txt, (ox + 10, oy + 88))