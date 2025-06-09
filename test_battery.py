import unittest
from unittest.mock import patch
from roadmesh.monitoring.battery import BatteryChargeMonitoring

class TestBatteryChargeMonitoring(unittest.TestCase):
    @patch('roadmesh.monitoring.battery.save_battery_state')
    @patch('roadmesh.monitoring.battery.load_battery_state', return_value=2.0)
    @patch('roadmesh.monitoring.battery.append_battery_history')
    def test_charge_discharge(self, mock_hist, mock_load, mock_save):
        b = BatteryChargeMonitoring(5.0, 0.2)
        orig = b.current_charge_Ah
        b.simulate_charge(hours=2)
        self.assertGreater(b.current_charge_Ah, orig)
        b.simulate_discharge(hours=1)
        self.assertLess(b.current_charge_Ah, 5.0)

    @patch('roadmesh.monitoring.battery.save_battery_state')
    @patch('roadmesh.monitoring.battery.load_battery_state', return_value=2.0)
    @patch('roadmesh.monitoring.battery.append_battery_history')
    def test_voltage_and_health(self, mock_hist, mock_load, mock_save):
        b = BatteryChargeMonitoring(5.0, 0.2)
        v = b.read_voltage()
        self.assertTrue(3.0 <= v <= 4.2)
        pct = b.calculate_percentage()
        self.assertTrue(0 <= pct <= 100)
        # Simulate low voltage for health check
        b.voltage_data[-1]['voltage'] = 3.0
        self.assertFalse(b.health_check())

if __name__ == '__main__':
    unittest.main() 