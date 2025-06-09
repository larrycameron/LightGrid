import unittest
from unittest.mock import patch
from roadmesh.networking.user_service import UserServiceManager
import bcrypt

class TestUserServiceManager(unittest.TestCase):
    @patch('roadmesh.networking.user_service.save_users')
    @patch('roadmesh.networking.user_service.load_users', return_value={})
    @patch('roadmesh.networking.user_service.save_sessions')
    @patch('roadmesh.networking.user_service.load_sessions', return_value={})
    def test_register_and_authenticate(self, mock_load_sessions, mock_save_sessions, mock_load_users, mock_save_users):
        us = UserServiceManager()
        self.assertTrue(us.register_user('testuser', 'password123'))
        self.assertFalse(us.register_user('testuser', 'password123'))  # duplicate
        self.assertTrue(us.authenticate('testuser', 'password123'))
        self.assertFalse(us.authenticate('testuser', 'wrongpass'))

    @patch('roadmesh.networking.user_service.save_users')
    @patch('roadmesh.networking.user_service.load_users', return_value={'testuser': bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode()})
    @patch('roadmesh.networking.user_service.save_sessions')
    @patch('roadmesh.networking.user_service.load_sessions', return_value={})
    def test_session_and_health(self, mock_load_sessions, mock_save_sessions, mock_load_users, mock_save_users):
        us = UserServiceManager()
        sid = us.create_session('testuser')
        self.assertEqual(us.get_user_by_session(sid), 'testuser')
        us.end_session(sid)
        self.assertIsNone(us.get_user_by_session(sid))
        # Health check: no users or sessions
        us.users = {}
        self.assertFalse(us.health_check())
        us.users = {'testuser': 'hash'}
        us.sessions = {}
        self.assertFalse(us.health_check())
        us.sessions = {'sid': 'testuser'}
        self.assertTrue(us.health_check())

if __name__ == '__main__':
    unittest.main() 