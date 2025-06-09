import unittest
from roadmesh.networking.mesh_manager import MeshNetworkManager

class TestMeshNetworkManager(unittest.TestCase):
    def setUp(self):
        self.mesh = MeshNetworkManager()

    def test_add_remove_node(self):
        self.mesh.add_node('A')
        self.assertIn('A', self.mesh.nodes)
        self.mesh.remove_node('A')
        self.assertNotIn('A', self.mesh.nodes)

    def test_add_remove_link(self):
        self.mesh.add_link('A', 'B', quality=80)
        self.assertIn('B', self.mesh.nodes['A'].neighbors)
        self.mesh.remove_link('A', 'B')
        self.assertNotIn('B', self.mesh.nodes['A'].neighbors)

    def test_topology(self):
        self.mesh.add_link('A', 'B')
        self.mesh.add_link('B', 'C')
        topo = self.mesh.get_topology()
        self.assertIn('A', topo)
        self.assertIn('B', topo['A'])

    def test_health_check(self):
        self.mesh.add_link('A', 'B')
        self.assertTrue(self.mesh.health_check())
        self.mesh.set_node_status('A', 'DOWN')
        self.assertFalse(self.mesh.health_check())

if __name__ == '__main__':
    unittest.main() 