import unittest
from unittest.mock import MagicMock, patch
from roadmesh.monitoring.health_monitor import HealthMonitor

class TestHealthMonitor(unittest.TestCase):
    def setUp(self):
        self.battery = MagicMock()
        self.lighting = MagicMock()
        self.mesh = MagicMock()
        self.user_service = MagicMock()
        self.monitor = HealthMonitor(self.battery, self.lighting, self.mesh, self.user_service)

    @patch('roadmesh.monitoring.health_monitor.HealthMonitor.send_email_alert')
    def test_all_healthy(self, mock_send_email):
        self.battery.health_check.return_value = True
        self.lighting.health_check.return_value = True
        self.mesh.health_check.return_value = True
        self.user_service.health_check.return_value = True
        self.monitor.check_and_alert()
        mock_send_email.assert_not_called()

    @patch('roadmesh.monitoring.health_monitor.HealthMonitor.send_email_alert')
    def test_battery_unhealthy(self, mock_send_email):
        self.battery.health_check.return_value = False
        self.lighting.health_check.return_value = True
        self.mesh.health_check.return_value = True
        self.user_service.health_check.return_value = True
        self.monitor.check_and_alert()
        mock_send_email.assert_called_once()

    @patch('roadmesh.monitoring.health_monitor.HealthMonitor.send_email_alert')
    def test_multiple_unhealthy(self, mock_send_email):
        self.battery.health_check.return_value = False
        self.lighting.health_check.return_value = False
        self.mesh.health_check.return_value = True
        self.user_service.health_check.return_value = False
        self.monitor.check_and_alert()
        mock_send_email.assert_called_once()

if __name__ == '__main__':
    unittest.main() 