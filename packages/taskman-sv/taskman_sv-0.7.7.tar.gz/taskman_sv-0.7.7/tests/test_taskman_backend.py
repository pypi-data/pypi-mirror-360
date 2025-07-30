import unittest
import os
import json
import tempfile
import shutil
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock
from src.taskman_sv.taskman_backend import TaskmanBackend

class TestTaskmanBackend(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Initialize backend with test directory
        self.backend = TaskmanBackend()
        self.backend.data_dir = self.test_dir
        self.backend.users_dir = os.path.join(self.test_dir, "users")
        
        # Create test directories
        os.makedirs(self.backend.users_dir, exist_ok=True)
        
        # Test user credentials
        self.test_username = "testuser"
        self.test_password = "testpass123"

    def tearDown(self):
        """Clean up after each test"""
        try:
            if os.path.exists(self.test_dir):
                shutil.rmtree(self.test_dir)
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def test_setup_data_directory(self):
        """Test if data directories are created correctly"""
        # Test directory existence
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertTrue(os.path.exists(self.backend.users_dir))

    def test_user_registration(self):
        """Test user registration functionality"""
        # Test successful registration
        result = self.backend.register_user(self.test_username, self.test_password)
        self.assertTrue(result)
        
        # Test duplicate registration
        result = self.backend.register_user(self.test_username, self.test_password)
        self.assertFalse(result)
        
        # Verify user file exists
        user_file = os.path.join(self.test_dir, "users", f"{self.test_username}.json")
        self.assertTrue(os.path.exists(user_file))

    def test_authentication(self):
        """Test user authentication"""
        # Register user first
        self.backend.register_user(self.test_username, self.test_password)
        
        # Test successful authentication
        result = self.backend.authenticate(self.test_username, self.test_password)
        self.assertTrue(result)
        
        # Test failed authentication
        result = self.backend.authenticate(self.test_username, "wrongpass")
        self.assertFalse(result)
        result = self.backend.authenticate("wronguser", self.test_password)
        self.assertFalse(result)

    def test_save_and_load_tasks(self):
        """Test saving and loading tasks"""
        # Setup authenticated user
        self.backend.register_user(self.test_username, self.test_password)
        self.backend.authenticate(self.test_username, self.test_password)
        
        # Test data
        test_tasks = [{
            "name": "Test Task",
            "description": "Test Description",
            "duration": 3600,
            "status": "Pending",
            "mode": "custom"
        }]
        
        # Test saving
        result = self.backend.save_tasks(test_tasks)
        self.assertTrue(result)
        
        # Test loading
        loaded_data = self.backend.load_tasks()
        self.assertIsNotNone(loaded_data)
        self.assertIn("tasks", loaded_data)
        self.assertEqual(len(loaded_data["tasks"]), 1)
        self.assertEqual(loaded_data["tasks"][0]["name"], "Test Task")

    def test_notes_operations(self):
        """Test notes functionality"""
        # Setup authenticated user
        self.backend.register_user(self.test_username, self.test_password)
        self.backend.authenticate(self.test_username, self.test_password)
        
        # Test data
        test_notes = {
            "modules": {
                "Work": ["Note 1", "Note 2"],
                "Personal": ["Note 3"]
            }
        }
        
        # Test saving notes
        result = self.backend.save_notes(test_notes)
        self.assertTrue(result)
        
        # Test loading notes
        loaded_notes = self.backend.load_notes()
        self.assertIsNotNone(loaded_notes)
        self.assertIn("modules", loaded_notes)
        self.assertIn("Work", loaded_notes["modules"])
        self.assertIn("Personal", loaded_notes["modules"])
        self.assertEqual(len(loaded_notes["modules"]["Work"]), 2)
        self.assertEqual(len(loaded_notes["modules"]["Personal"]), 1)

    def test_fastnotes_operations(self):
        """Test fast notes functionality"""
        # Setup authenticated user
        self.backend.register_user(self.test_username, self.test_password)
        self.backend.authenticate(self.test_username, self.test_password)
        
        # Test data
        test_fastnotes = ["Quick note 1", "Quick note 2"]
        
        # Test saving
        result = self.backend.save_fastnotes(test_fastnotes)
        self.assertTrue(result)
        
        # Test loading
        loaded_fastnotes = self.backend.load_fastnotes()
        self.assertIsNotNone(loaded_fastnotes)
        self.assertEqual(len(loaded_fastnotes), 2)
        self.assertEqual(loaded_fastnotes[0], "Quick note 1")

    def test_report_operations(self):
        """Test report functionality"""
        # Setup authenticated user
        self.backend.register_user(self.test_username, self.test_password)
        self.backend.authenticate(self.test_username, self.test_password)
        
        # Test data
        test_report = ["Report line 1", "Report line 2"]
        test_date = date.today().isoformat()
        
        # Test saving report
        result = self.backend.save_report(test_report, test_date)
        self.assertTrue(result)
        
        # Test loading report
        loaded_report = self.backend.load_report(test_date)
        self.assertIsNotNone(loaded_report)
        self.assertEqual(loaded_report["content"], test_report)

if __name__ == '__main__':
    unittest.main()
