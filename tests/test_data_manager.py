import unittest
import os
import json
import data_manager # To modify DATA_FILE
from data_manager import load_user_data, save_user_data, get_user, update_user

class TestDataManager(unittest.TestCase):
    original_data_file = None
    test_data_file = 'test_user_data.json'

    @classmethod
    def setUpClass(cls):
        cls.original_data_file = data_manager.DATA_FILE
        data_manager.DATA_FILE = cls.test_data_file

    @classmethod
    def tearDownClass(cls):
        data_manager.DATA_FILE = cls.original_data_file

    def setUp(self):
        # Ensure the test file is clean before each test
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

    def tearDown(self):
        # Clean up the test file after each test
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

    def test_load_save_user_data(self):
        sample_data = {"1": {"health": 50, "experience": 5, "gold": 2, "tasks": {}}}
        save_user_data(sample_data)
        loaded_data = load_user_data()
        self.assertEqual(loaded_data, sample_data)

    def test_get_new_user(self):
        user_id = "new_user_123"
        user_data = get_user(user_id)
        expected_data = {"health": 100, "experience": 0, "gold": 10, "tasks": {}}
        self.assertEqual(user_data, expected_data)
        # Check if the user was saved by get_user (it should be, due to the initialization logic)
        all_users_data = load_user_data()
        self.assertIn(user_id, all_users_data)
        self.assertEqual(all_users_data[user_id], expected_data)

    def test_get_existing_user(self):
        user_id = "existing_user_456"
        expected_data = {"health": 70, "experience": 7, "gold": 70, "tasks": {"task1": "done"}}
        # Save initial state directly for this test
        save_user_data({user_id: expected_data})
        user_data = get_user(user_id)
        self.assertEqual(user_data, expected_data)

    def test_update_user(self):
        user_id = "user_to_update_789"
        # Initialize user first using get_user to ensure it's in the "database"
        initial_user_state = get_user(user_id) # This will save the initial state

        # Now, create the data for update.
        # We want to update only specific fields, not necessarily all.
        # So, we base the update on the initial state or a subset of fields.
        updated_specific_data = {
            'experience': 50,
            'gold': 25
        }
        # update_user merges this with existing data
        update_user(user_id, updated_specific_data)

        user_data_after_update = get_user(user_id)

        self.assertEqual(user_data_after_update['experience'], 50)
        self.assertEqual(user_data_after_update['gold'], 25)
        # Health and tasks should remain as per initial_user_state
        self.assertEqual(user_data_after_update['health'], initial_user_state['health'])
        self.assertEqual(user_data_after_update['tasks'], initial_user_state['tasks'])


    def test_load_user_data_file_not_found(self):
        # setUp ensures the file is deleted
        loaded_data = load_user_data()
        self.assertEqual(loaded_data, {})

    def test_load_user_data_invalid_json(self):
        with open(self.test_data_file, 'w') as f:
            f.write("this is not valid json")
        loaded_data = load_user_data()
        self.assertEqual(loaded_data, {})

if __name__ == '__main__':
    unittest.main()
