import json

DATA_FILE = 'user_data.json' # Module-level variable

def load_user_data():
    """Loads user data from the JSON file."""
    try:
        with open(DATA_FILE, 'r') as f: # Uses module-level DATA_FILE
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data

def save_user_data(data):
    """Saves user data to the JSON file."""
    with open(DATA_FILE, 'w') as f: # Uses module-level DATA_FILE
        json.dump(data, f, indent=4)

def get_user(user_id):
    """Gets a specific user's data, initializing if not found."""
    users = load_user_data()
    user_id_str = str(user_id)
    if user_id_str not in users:
        users[user_id_str] = {"health": 100, "experience": 0, "gold": 10, "tasks": {}}
        # No need to save here, as get_user is for retrieval.
        # The caller can decide to save if modifications are made.
    return users.get(user_id_str)


def update_user(user_id, user_specific_data):
    """Updates a specific user's data."""
    users = load_user_data()
    user_id_str = str(user_id)
    # Ensure the user exists before updating, or initialize if that's the desired behavior.
    # For now, assuming get_user or some other mechanism ensures user creation.
    if user_id_str not in users:
        users[user_id_str] = {"health": 100, "experience": 0, "gold": 10, "tasks": {}} # Initialize if not exist
    users[user_id_str].update(user_specific_data)
    save_user_data(users)
