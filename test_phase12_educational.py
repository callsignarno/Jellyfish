import os
import unittest
import math

os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame

from jellyfish import Jellyfish
from nervous_system import NervousSystem
from sensory_system import SensorySystem
from environment import Environment
from educational_guide import EducationalGuide


class TestPhase12EducationalMasterpiece(unittest.TestCase):
    """
    Test suite for Phase 12: Educational Masterpiece & Biological Guide.
    
    Verifies:
      1. Educational Field Guide modal state, tabs, and content integrity.
      2. Anatomical callout pins and coordinate transformation anchoring.
      3. Time dilation simulation speeds (1.0x, 0.5x, 0.25x).
      4. Guided educational lessons (1-5) triggering biological demonstrations.
      5. Biomechanical metrics (Reynolds number, elastic strain, thrust impulse).
      6. Living benthic ecosystem entities (sea-pens, ctenophores, vent ash).
    """

    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1200, 700))

    def setUp(self):
        self.jellyfish = Jellyfish(600, 350)
        self.nervous_system = NervousSystem(rows=4, cols=5)
        self.sensory_system = SensorySystem()
        self.environment = Environment(1200, 700)
        self.guide = EducationalGuide(1200, 700)

    def test_01_educational_guide_tabs_and_content(self):
        print("Test 1: Verifying Educational Field Guide tabs and scientific content...")
        self.assertEqual(len(self.guide.TABS), 5)
        self.assertFalse(self.guide.show_guide)

        # Toggle modal
        self.guide.toggle_guide()
        self.assertTrue(self.guide.show_guide)

        # Tab cycling
        for tab_idx in range(5):
            self.guide.active_tab = tab_idx
            self.assertEqual(self.guide.active_tab, tab_idx)

        # Ensure modal draws cleanly
        self.guide.draw_modal(self.screen)
        print("PASS: Educational Field Guide tabs and dialog verified.")

    def test_02_anatomical_pins_and_hit_testing(self):
        print("Test 2: Verifying anatomical callout pins and biological metadata...")
        self.assertEqual(len(self.guide.pins_meta), 7)
        pin_ids = [p['id'] for p in self.guide.pins_meta]
        self.assertIn('rhopalia', pin_ids)
        self.assertIn('coronal_muscles', pin_ids)
        self.assertIn('mesoglea', pin_ids)
        self.assertIn('radial_canals', pin_ids)
        self.assertIn('manubrium', pin_ids)
        self.assertIn('oral_arms', pin_ids)
        self.assertIn('tentacles', pin_ids)

        self.guide.show_anatomy = True
        # Calculate screen position of first pin
        p0 = self.guide.pins_meta[0]
        ox, oy = p0['offset'](self.jellyfish.size, self.jellyfish.contraction)
        px = self.jellyfish.position.x + ox
        py = self.jellyfish.position.y + oy

        # Test hover detection
        self.guide.update_hover(px, py, self.jellyfish)
        self.assertIsNotNone(self.guide.hovered_pin)
        self.assertEqual(self.guide.hovered_pin['id'], 'rhopalia')

        # Test click selection
        handled = self.guide.handle_click(px, py, self.jellyfish)
        self.assertTrue(handled)
        self.assertEqual(self.guide.selected_pin, 'rhopalia')

        # Ensure pins draw cleanly
        self.guide.draw_anatomy_pins(self.screen, self.jellyfish)
        print("PASS: Anatomical callout pins and hit testing verified.")

    def test_03_time_dilation_speed_scaling(self):
        print("Test 3: Verifying time dilation simulation speeds...")
        self.assertEqual(self.guide.time_scale, 1.0)
        s1 = self.guide.cycle_speed()
        self.assertEqual(s1, 0.5)
        s2 = self.guide.cycle_speed()
        self.assertEqual(s2, 0.25)
        s3 = self.guide.cycle_speed()
        self.assertEqual(s3, 1.0)
        print("PASS: Time dilation speed controls verified.")

    def test_04_guided_educational_lessons(self):
        print("Test 4: Verifying guided interactive educational lessons 1 to 5...")
        # Lesson 1: Rhopalial Pacemaker
        self.guide.start_lesson(1, self.jellyfish, self.nervous_system, self.sensory_system, self.environment)
        self.assertEqual(self.guide.active_lesson, 1)
        self.assertIn("PACEMAKER", self.guide.lesson_banner)
        self.assertGreater(self.nervous_system.neurons[0].input_current, 0.0)

        # Lesson 2: Statolith Gravity Righting
        self.guide.start_lesson(2, self.jellyfish, self.nervous_system, self.sensory_system, self.environment)
        self.assertEqual(self.guide.active_lesson, 2)
        self.assertAlmostEqual(self.jellyfish.orientation, 0.95)
        self.assertIn("STATOLITH", self.guide.lesson_banner)

        # Lesson 3: Tactile Escape Burst
        self.guide.start_lesson(3, self.jellyfish, self.nervous_system, self.sensory_system, self.environment)
        self.assertEqual(self.guide.active_lesson, 3)
        self.assertTrue(self.sensory_system.manual_touch_trigger)

        # Lesson 4: Chemotaxis & Digestion
        self.guide.start_lesson(4, self.jellyfish, self.nervous_system, self.sensory_system, self.environment)
        self.assertEqual(self.guide.active_lesson, 4)
        self.assertTrue(self.sensory_system.food_active)

        # Lesson 5: Electrophysiology
        self.guide.start_lesson(5, self.jellyfish, self.nervous_system, self.sensory_system, self.environment)
        self.assertEqual(self.guide.active_lesson, 5)
        self.assertIn("ELECTROPHYSIOLOGY", self.guide.lesson_banner)

        # Timer update & auto-conclusion
        self.guide.update(7.5, self.jellyfish, self.nervous_system, self.sensory_system, self.environment)
        self.assertIsNone(self.guide.active_lesson)
        self.assertEqual(self.guide.time_scale, 1.0)
        print("PASS: Guided educational lessons verified.")

    def test_05_biomechanical_and_fluid_metrics(self):
        print("Test 5: Verifying biomechanical metrics (Reynolds number, elastic strain, thrust impulse)...")
        # Apply contraction
        motor_activations = [1.0] * 8
        self.jellyfish.update(0.05, motor_activations)
        self.assertGreater(self.jellyfish.contraction, 0.1)
        self.assertGreater(self.jellyfish.elastic_strain_pct, 10.0)
        self.assertGreater(self.jellyfish.instant_thrust_mn, 0.0)
        self.assertGreater(self.jellyfish.reynolds_number, 30.0)

        # Test telemetry rendering in nervous_system
        telemetry_data = {
            're': self.jellyfish.reynolds_number,
            'thrust_mn': self.jellyfish.instant_thrust_mn,
            'strain_pct': self.jellyfish.elastic_strain_pct,
            'energy': self.jellyfish.energy
        }
        self.nervous_system.draw(self.screen, telemetry_data=telemetry_data)
        print(f"  Contraction: {self.jellyfish.contraction:.2f}, Mesoglea Strain: {self.jellyfish.elastic_strain_pct:.1f}%, Re: {self.jellyfish.reynolds_number:.0f}")
        print("PASS: Biomechanical metrics and telemetry verified.")

    def test_06_living_benthic_ecosystem_entities(self):
        print("Test 6: Verifying living benthic ecosystem entities...")
        self.assertGreater(len(self.environment.sea_pens), 0)
        self.assertGreater(len(self.environment.ctenophores), 0)

        # Step environment to generate hydrothermal vent particles
        for _ in range(10):
            self.environment.update(0.1)

        self.assertGreater(len(self.environment.vent_particles), 0)
        self.environment.draw_terrain(self.screen)
        self.environment.draw_particles(self.screen)
        self.environment.draw_atmosphere(self.screen, 0.5)
        print(f"  Active Sea-Pens: {len(self.environment.sea_pens)}, Active Vent Ash Particles: {len(self.environment.vent_particles)}")
        print("PASS: Living benthic ecosystem verified.")


if __name__ == '__main__':
    unittest.main()
