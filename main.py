import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from roadmesh.config import TIMEZONE
from roadmesh.monitoring.battery import BatteryChargeMonitoring
from roadmesh.monitoring.energy import EnergyHarvestMonitor
from roadmesh.monitoring.load import LoadController
from roadmesh.monitoring.lighting import LightingController
from roadmesh.monitoring.power_management import PowerManagement
from roadmesh.networking.mesh_manager import MeshNetworkManager
from roadmesh.networking.user_service import UserServiceManager
from roadmesh.persistence import append_mesh_status, append_event_log

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def simulate_system(days=1):
    # Initialize modules
    battery = BatteryChargeMonitoring(capacity_Ah=5.0, consumption_rate=0.2)
    energy = EnergyHarvestMonitor()
    load_ctrl = LoadController(battery)
    lighting = LightingController(battery)
    mesh = MeshNetworkManager()
    user_service = UserServiceManager()
    power_mgmt = PowerManagement(battery, lighting, mesh, load_ctrl)

    # Example mesh setup
    mesh.add_node('A')
    mesh.add_node('B')
    mesh.add_link('A', 'B', quality=90)
    mesh.add_node('C')
    mesh.add_link('B', 'C', quality=80)
    mesh.print_topology()

    # Simulate time
    start = datetime.now(ZoneInfo(TIMEZONE))
    end = start + timedelta(days=days)
    curr = start
    last_mesh_mode = None
    last_lighting_mode = None
    while curr < end:
        logger.info(f"Simulating hour: {curr}")
        energy.read_solar()
        energy.read_teg()
        battery.simulate_charge()
        battery.simulate_discharge()
        battery.read_voltage()
        power_mgmt.update()
        # Track mesh node statuses for uptime analytics
        append_mesh_status(mesh.get_node_statuses())
        # Log mode changes
        if power_mgmt.mode != last_mesh_mode:
            append_event_log(f"Mesh mode changed to {power_mgmt.mode} at {curr}")
            last_mesh_mode = power_mgmt.mode
        if power_mgmt.lighting_mode != last_lighting_mode:
            append_event_log(f"Lighting mode changed to {power_mgmt.lighting_mode} at {curr}")
            last_lighting_mode = power_mgmt.lighting_mode
        curr += timedelta(hours=1)

    logger.info('Simulation complete')
    mesh.print_topology()

if __name__ == '__main__':
    simulate_system(days=1) 