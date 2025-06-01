import pytest
import json
from unittest.mock import patch

# Add the project root to the Python path to allow direct import of app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import data_manager # Will be used for mocking its methods

# In-memory store for our mock data manager
MOCK_USER_DATA = {}

def mock_load_user_data():
    """Mock version of load_user_data that returns a deep copy of our in-memory store."""
    return json.loads(json.dumps(MOCK_USER_DATA)) # Deep copy to simulate real load

def mock_save_user_data(data):
    """Mock version of save_user_data that updates our in-memory store."""
    global MOCK_USER_DATA
    MOCK_USER_DATA = json.loads(json.dumps(data)) # Deep copy to simulate real save

@pytest.fixture(autouse=True)
def mock_data_storage(monkeypatch):
    """Fixture to automatically mock data_manager.load_user_data and data_manager.save_user_data."""
    global MOCK_USER_DATA
    MOCK_USER_DATA = {} # Reset for each test

    monkeypatch.setattr(data_manager, 'load_user_data', mock_load_user_data)
    monkeypatch.setattr(data_manager, 'save_user_data', mock_save_user_data)
    # Also need to ensure that any direct imports of these functions in app.py are patched.
    # If app.py does `from data_manager import load_user_data`, that needs patching too.
    # For simplicity, we assume app.py calls data_manager.load_user_data() etc.
    # If app.py has `from data_manager import get_user, update_user` and these internally call
    # load_user_data/save_user_data using the module prefix (e.g. data_manager.load_data()),
    # then patching data_manager.load_user_data and data_manager.save_user_data is sufficient.
    # Let's verify data_manager.py structure for get_user and update_user.
    # get_user calls load_user_data() - this will be the module global one if not prefixed.
    # update_user calls load_user_data() and save_user_data().

    # To ensure app.py's imported versions are patched if it uses `from data_manager import ...`:
    # This can get tricky. A common way is to patch where the function *is looked up*, not where it's defined.
    # So, if app.py uses `from data_manager import load_user_data`, we'd patch `app.load_user_data`.
    # However, app.py uses `from data_manager import get_user, update_user`.
    # get_user and update_user in data_manager.py itself call load_user_data and save_user_data.
    # So, patching them in the data_manager module (as done above) should be effective.

@pytest.fixture
def client():
    """A test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# --- Test User Data Endpoint ---
def test_get_new_user(client):
    """Test GET /api/user/<user_id> for a new user."""
    response = client.get('/api/user/testuser1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['health'] == 100
    assert data['experience'] == 0
    assert data['gold'] == 10
    assert data['tasks'] == {}
    assert data['habits'] == {}
    # Check that this new user is now in our mock data store
    assert 'testuser1' in MOCK_USER_DATA

def test_get_existing_user(client):
    """Test GET /api/user/<user_id> for an existing user."""
    # Setup: Create a user directly in the mock store
    MOCK_USER_DATA['testuser2'] = {"health": 50, "experience": 10, "gold": 5, "tasks": {"task1": "desc"}, "habits": {}}

    response = client.get('/api/user/testuser2')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['health'] == 50
    assert data['experience'] == 10
    assert data['tasks'] == {"task1": "desc"}

# --- Test Task Endpoints ---
def test_add_task(client):
    """Test POST /api/user/<user_id>/tasks (add task)."""
    user_id = 'testuser_add_task'
    # Ensure user is created (though add_task_api should handle it via get_user)
    client.get(f'/api/user/{user_id}')

    response = client.post(f'/api/user/{user_id}/tasks',
                           data=json.dumps({"name": "New Task 1", "description": "Test Desc"}),
                           content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == "Task added successfully"
    assert "New Task 1" in data['task']
    assert data['task']["New Task 1"]["description"] == "Test Desc"
    assert data['task']["New Task 1"]["completed"] == False

    # Verify data in mock store
    assert "New Task 1" in MOCK_USER_DATA[user_id]['tasks']
    assert MOCK_USER_DATA[user_id]['tasks']["New Task 1"]["description"] == "Test Desc"

def test_add_task_missing_name(client):
    """Test POST /api/user/<user_id>/tasks with missing task name."""
    user_id = 'testuser_add_task_fail'
    client.get(f'/api/user/{user_id}')

    response = client.post(f'/api/user/{user_id}/tasks',
                           data=json.dumps({"description": "Test Desc"}),
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Task name is required"

def test_edit_task_description(client):
    """Test PUT /api/user/<user_id>/tasks/<task_id> (edit task description)."""
    user_id = 'testuser_edit_task'
    task_id = 'task_to_edit'
    MOCK_USER_DATA[user_id] = {
        "health": 100, "experience": 0, "gold": 0,
        "tasks": {task_id: {"description": "Original Desc", "completed": False}},
        "habits": {}
    }

    response = client.put(f'/api/user/{user_id}/tasks/{task_id}',
                          data=json.dumps({"description": "Updated Desc"}),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['task'][task_id]['description'] == "Updated Desc"
    assert MOCK_USER_DATA[user_id]['tasks'][task_id]['description'] == "Updated Desc"

def test_edit_task_complete(client):
    """Test PUT /api/user/<user_id>/tasks/<task_id> (complete task and check stats)."""
    user_id = 'testuser_complete_task'
    task_id = 'task_to_complete'
    MOCK_USER_DATA[user_id] = {
        "health": 100, "experience": 0, "gold": 0,
        "tasks": {task_id: {"description": "Test", "completed": False}},
        "habits": {}
    }

    response = client.put(f'/api/user/{user_id}/tasks/{task_id}',
                          data=json.dumps({"completed": True}),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['task'][task_id]['completed'] is True
    assert MOCK_USER_DATA[user_id]['tasks'][task_id]['completed'] is True
    assert MOCK_USER_DATA[user_id]['experience'] == 10  # Default XP gain
    assert MOCK_USER_DATA[user_id]['gold'] == 5      # Default gold gain

def test_edit_task_undo_complete(client):
    """Test PUT /api/user/<user_id>/tasks/<task_id> (undo completion and check stats)."""
    user_id = 'testuser_undo_complete_task'
    task_id = 'task_to_undo_complete'
    MOCK_USER_DATA[user_id] = {
        "health": 100, "experience": 10, "gold": 5,
        "tasks": {task_id: {"description": "Test", "completed": True}}, # Initially completed
        "habits": {}
    }

    response = client.put(f'/api/user/{user_id}/tasks/{task_id}',
                          data=json.dumps({"completed": False}),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['task'][task_id]['completed'] is False
    assert MOCK_USER_DATA[user_id]['tasks'][task_id]['completed'] is False
    assert MOCK_USER_DATA[user_id]['experience'] == 0 # XP reverted
    assert MOCK_USER_DATA[user_id]['gold'] == 0     # Gold reverted

def test_fail_task(client):
    """Test POST /api/user/<user_id>/tasks/<task_id>/fail (fail task and check health)."""
    user_id = 'testuser_fail_task'
    task_id = 'task_to_fail'
    MOCK_USER_DATA[user_id] = {
        "health": 100, "experience": 0, "gold": 0,
        "tasks": {task_id: {"description": "Test", "completed": False}},
        "habits": {}
    }

    response = client.post(f'/api/user/{user_id}/tasks/{task_id}/fail')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['task'][task_id]['completed'] is False # Should ensure it's marked not completed
    assert MOCK_USER_DATA[user_id]['tasks'][task_id]['completed'] is False
    assert MOCK_USER_DATA[user_id]['health'] == 90  # Default health deduction
    assert data['user_stats']['health'] == 90

def test_fail_completed_task(client):
    """Test POST /api/user/<user_id>/tasks/<task_id>/fail on an already completed task."""
    user_id = 'testuser_fail_completed_task'
    task_id = 'completed_task_to_fail'
    MOCK_USER_DATA[user_id] = {
        "health": 100, "experience": 10, "gold": 5, # User got rewards
        "tasks": {task_id: {"description": "Test", "completed": True}}, # Task was completed
        "habits": {}
    }

    response = client.post(f'/api/user/{user_id}/tasks/{task_id}/fail')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['task'][task_id]['completed'] is False # Marking as failed should un-complete it
    assert MOCK_USER_DATA[user_id]['tasks'][task_id]['completed'] is False
    assert MOCK_USER_DATA[user_id]['health'] == 90  # Health deduction
    # Experience and gold from prior completion are NOT reverted by fail endpoint by current design
    assert MOCK_USER_DATA[user_id]['experience'] == 10
    assert MOCK_USER_DATA[user_id]['gold'] == 5

def test_delete_task(client):
    """Test DELETE /api/user/<user_id>/tasks/<task_id> (delete task)."""
    user_id = 'testuser_delete_task'
    task_id = 'task_to_delete'
    MOCK_USER_DATA[user_id] = {
        "health": 100, "experience": 0, "gold": 0,
        "tasks": {task_id: {"description": "Test", "completed": False}},
        "habits": {}
    }

    response = client.delete(f'/api/user/{user_id}/tasks/{task_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == "Task deleted successfully"
    assert task_id not in MOCK_USER_DATA[user_id]['tasks']

def test_delete_missing_task(client):
    """Test DELETE /api/user/<user_id>/tasks/<task_id> for a non-existent task."""
    user_id = 'testuser_delete_missing_task'
    # User exists, but task does not
    MOCK_USER_DATA[user_id] = {"health": 100, "experience": 0, "gold": 0, "tasks": {}, "habits": {}}

    response = client.delete(f'/api/user/{user_id}/tasks/non_existent_task')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == "Task not found"

# --- Test Habit Endpoints ---
def test_add_habit(client):
    """Test POST /api/user/<user_id>/habits (add habit)."""
    user_id = 'testuser_add_habit'
    client.get(f'/api/user/{user_id}') # Initialize user

    response = client.post(f'/api/user/{user_id}/habits',
                           data=json.dumps({"name": "New Habit 1", "description": "Read daily", "frequency": "daily"}),
                           content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == "Habit added successfully"
    assert "New Habit 1" in data['habit']
    habit_data = data['habit']["New Habit 1"]
    assert habit_data["description"] == "Read daily"
    assert habit_data["frequency"] == "daily"
    assert habit_data["streak"] == 0
    assert habit_data["last_completed_date"] is None

    # Verify data in mock store
    assert "New Habit 1" in MOCK_USER_DATA[user_id]['habits']
    stored_habit = MOCK_USER_DATA[user_id]['habits']["New Habit 1"]
    assert stored_habit["description"] == "Read daily"
    assert stored_habit["streak"] == 0

def test_edit_habit(client):
    """Test PUT /api/user/<user_id>/habits/<habit_id> (edit habit)."""
    user_id = 'testuser_edit_habit'
    habit_id = 'habit_to_edit'
    MOCK_USER_DATA[user_id] = {
        "tasks": {},
        "habits": {habit_id: {"description": "Original Desc", "frequency": "daily", "streak": 0, "last_completed_date": None}}
    }

    response = client.put(f'/api/user/{user_id}/habits/{habit_id}',
                          data=json.dumps({"description": "Updated Desc", "frequency": "weekly"}),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    updated_habit = data['habit'][habit_id]
    assert updated_habit['description'] == "Updated Desc"
    assert updated_habit['frequency'] == "weekly"

    # Verify data in mock store
    stored_habit = MOCK_USER_DATA[user_id]['habits'][habit_id]
    assert stored_habit['description'] == "Updated Desc"
    assert stored_habit['frequency'] == "weekly"

def test_complete_habit(client):
    """Test POST /api/user/<user_id>/habits/<habit_id>/complete."""
    user_id = 'testuser_complete_habit'
    habit_id = 'habit_to_complete'
    MOCK_USER_DATA[user_id] = {
        "health": 100, "experience": 0, "gold": 0,
        "tasks": {},
        "habits": {habit_id: {"description": "Test", "frequency": "daily", "streak": 0, "last_completed_date": None}}
    }

    response = client.post(f'/api/user/{user_id}/habits/{habit_id}/complete')
    assert response.status_code == 200
    data = json.loads(response.data)

    completed_habit = data['habit'][habit_id]
    assert completed_habit['streak'] == 1
    assert completed_habit['last_completed_date'] is not None

    user_stats = data['user_stats']
    assert user_stats['experience'] == 5 # Default XP for habit
    assert user_stats['gold'] == 2       # Default gold for habit

    # Verify data in mock store
    stored_user = MOCK_USER_DATA[user_id]
    assert stored_user['habits'][habit_id]['streak'] == 1
    assert stored_user['habits'][habit_id]['last_completed_date'] is not None
    assert stored_user['experience'] == 5
    assert stored_user['gold'] == 2

def test_fail_habit(client):
    """Test POST /api/user/<user_id>/habits/<habit_id>/fail."""
    user_id = 'testuser_fail_habit'
    habit_id = 'habit_to_fail'
    MOCK_USER_DATA[user_id] = {
        "health": 100, "experience": 0, "gold": 0,
        "tasks": {},
        "habits": {habit_id: {"description": "Test", "frequency": "daily", "streak": 5, "last_completed_date": "some_date"}}
    }

    response = client.post(f'/api/user/{user_id}/habits/{habit_id}/fail')
    assert response.status_code == 200
    data = json.loads(response.data)

    failed_habit = data['habit'][habit_id]
    assert failed_habit['streak'] == 0 # Streak resets

    user_stats = data['user_stats']
    assert user_stats['health'] == 95 # Default health deduction for habit fail

    # Verify data in mock store
    stored_user = MOCK_USER_DATA[user_id]
    assert stored_user['habits'][habit_id]['streak'] == 0
    assert stored_user['health'] == 95

def test_delete_habit(client):
    """Test DELETE /api/user/<user_id>/habits/<habit_id>."""
    user_id = 'testuser_delete_habit'
    habit_id = 'habit_to_delete'
    MOCK_USER_DATA[user_id] = {
        "tasks": {},
        "habits": {habit_id: {"description": "Test", "frequency": "daily", "streak": 0}}
    }

    response = client.delete(f'/api/user/{user_id}/habits/{habit_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == "Habit deleted successfully"
    assert habit_id not in MOCK_USER_DATA[user_id]['habits']

def test_delete_missing_habit(client):
    """Test DELETE /api/user/<user_id>/habits/<habit_id> for a non-existent habit."""
    user_id = 'testuser_delete_missing_habit'
    MOCK_USER_DATA[user_id] = {"tasks": {}, "habits": {}}

    response = client.delete(f'/api/user/{user_id}/habits/non_existent_habit')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == "Habit not found or user data incomplete" # Message from app.py
```
