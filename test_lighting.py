import unittest
from unittest.mock import MagicMock
from datetime import time
from roadmesh.monitoring.lighting import LightingController

class TestLightingController(unittest.TestCase):
    def setUp(self):
        self.battery = MagicMock()
        self.lighting = LightingController(self.battery)

    def test_state_transitions(self):
        self.battery.calculate_percentage.return_value = 60
        self.lighting.update(now=time(20,0))
        self.assertEqual(self.lighting.state, 'ON')
        self.battery.calculate_percentage.return_value = 30
        self.lighting.update(now=time(20,0))
        self.assertEqual(self.lighting.state, 'DIM')
        self.battery.calculate_percentage.return_value = 10
        self.lighting.update(now=time(20,0))
        self.assertEqual(self.lighting.state, 'OFF')

    def test_health_check_night(self):
        self.lighting.state = 'OFF'
        self.assertFalse(self.lighting.health_check(now=time(20,0)))
        self.lighting.state = 'ON'
        self.assertTrue(self.lighting.health_check(now=time(20,0)))

    def test_health_check_day(self):
        self.lighting.state = 'OFF'
        self.assertTrue(self.lighting.health_check(now=time(12,0)))

if __name__ == '__main__':
    unittest.main() 