from flask import Flask, jsonify, render_template, request
from data_manager import get_user, update_user

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/webapp')
def index():
    return render_template('index.html')

@app.route('/api/user/<user_id>')
def get_user_api(user_id):
    user_data = get_user(user_id)
    return jsonify(user_data)

@app.route('/api/user/<user_id>/tasks', methods=['POST'])
def add_task_api(user_id):
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Task name is required"}), 400

    task_name = data['name']
    task_description = data.get('description', '') # Optional description

    user_data = get_user(user_id)
    if not user_data:
        return jsonify({"error": "User not found"}), 404

    # For now, task_name is the ID. If it exists, it's overwritten.
    user_data['tasks'][task_name] = {"description": task_description, "completed": False}

    update_user(user_id, user_data)
    return jsonify({"message": "Task added successfully", "task": {task_name: user_data['tasks'][task_name]}}), 201

@app.route('/api/user/<user_id>/tasks/<task_id>', methods=['PUT'])
def edit_task_api(user_id, task_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    user_data = get_user(user_id)
    if not user_data:
        return jsonify({"error": "User not found"}), 404

    if task_id not in user_data['tasks']:
        return jsonify({"error": "Task not found"}), 404

    task = user_data['tasks'][task_id]
    previous_completed_status = task.get('completed', False)

    # Update task fields
    task['description'] = data.get('description', task.get('description', ''))
    task['completed'] = data.get('completed', task.get('completed', False))
    # Potentially other fields like 'name' if we allow renaming,
    # but that's complex if name is ID.

    # Handle stat changes based on completion status change
    if task['completed'] and not previous_completed_status: # Task marked complete
        user_data['experience'] = user_data.get('experience', 0) + 10
        user_data['gold'] = user_data.get('gold', 0) + 5
    elif not task['completed'] and previous_completed_status: # Task marked incomplete from complete (e.g. undo)
        # Optional: Revert stat changes, or handle as a penalty, or do nothing
        # For now, let's assume undoing completion reverts the positive reward
        user_data['experience'] = user_data.get('experience', 0) - 10
        user_data['gold'] = user_data.get('gold', 0) - 5
        # Ensure stats don't go negative if that's a rule
        user_data['experience'] = max(0, user_data['experience'])
        user_data['gold'] = max(0, user_data['gold'])


    user_data['tasks'][task_id] = task # Update the task in user_data
    update_user(user_id, user_data)
    return jsonify({"message": "Task updated successfully", "task": {task_id: task}}), 200

@app.route('/api/user/<user_id>/tasks/<task_id>', methods=['DELETE'])
def delete_task_api(user_id, task_id):
    user_data = get_user(user_id)
    if not user_data:
        return jsonify({"error": "User not found"}), 404

    if task_id not in user_data['tasks']:
        return jsonify({"error": "Task not found"}), 404

    del user_data['tasks'][task_id]
    update_user(user_id, user_data)
    return jsonify({"message": "Task deleted successfully"}), 200

@app.route('/api/user/<user_id>/tasks/<task_id>/fail', methods=['POST'])
def fail_task_api(user_id, task_id):
    user_data = get_user(user_id)
    if not user_data:
        return jsonify({"error": "User not found"}), 404

    if 'tasks' not in user_data or task_id not in user_data['tasks']:
        return jsonify({"error": "Task not found"}), 404

    task = user_data['tasks'][task_id]

    # Mark task as not completed if it was, and apply penalty
    task['completed'] = False
    # Optional: add a 'failed_count' or 'last_failed_date' if needed

    # Deduct health for failing a task
    user_data['health'] = user_data.get('health', 100) - 10 # Standard task failure penalty
    user_data['health'] = max(0, user_data['health']) # Ensure health doesn't go below 0

    user_data['tasks'][task_id] = task # Save changes to the task
    update_user(user_id, user_data)

    response_data = {
        "message": "Task marked as failed",
        "task": {task_id: task},
        "user_stats": {"health": user_data['health']}
    }
    if user_data['health'] == 0:
        response_data["warning"] = "User health has reached 0!"

    return jsonify(response_data), 200

# --- Habit Management Endpoints ---

@app.route('/api/user/<user_id>/habits', methods=['POST'])
def add_habit_api(user_id):
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Habit name is required"}), 400

    habit_name = data['name']
    # Optional fields for a habit
    frequency = data.get('frequency', 'daily')
    description = data.get('description', '')

    user_data = get_user(user_id)
    if not user_data:
        return jsonify({"error": "User not found"}), 404

    if 'habits' not in user_data: # Should be initialized by get_user, but as a safeguard
        user_data['habits'] = {}

    # For now, habit_name is the ID. If it exists, it's overwritten.
    user_data['habits'][habit_name] = {
        "description": description,
        "frequency": frequency,
        "streak": 0,
        "last_completed_date": None # Could be ISO date string
    }

    update_user(user_id, user_data)
    return jsonify({"message": "Habit added successfully", "habit": {habit_name: user_data['habits'][habit_name]}}), 201

@app.route('/api/user/<user_id>/habits/<habit_id>', methods=['PUT'])
def edit_habit_api(user_id, habit_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    user_data = get_user(user_id)
    if not user_data or 'habits' not in user_data or habit_id not in user_data['habits']:
        return jsonify({"error": "Habit not found or user data incomplete"}), 404

    habit = user_data['habits'][habit_id]

    # Update allowed fields
    habit['description'] = data.get('description', habit.get('description', ''))
    habit['frequency'] = data.get('frequency', habit.get('frequency', 'daily'))
    # Other fields like 'streak' or 'last_completed_date' are typically not manually edited,
    # but rather by 'complete'/'fail' actions.

    user_data['habits'][habit_id] = habit
    update_user(user_id, user_data)
    return jsonify({"message": "Habit updated successfully", "habit": {habit_id: habit}}), 200

@app.route('/api/user/<user_id>/habits/<habit_id>', methods=['DELETE'])
def delete_habit_api(user_id, habit_id):
    user_data = get_user(user_id)
    if not user_data or 'habits' not in user_data or habit_id not in user_data['habits']:
        return jsonify({"error": "Habit not found or user data incomplete"}), 404

    del user_data['habits'][habit_id]
    update_user(user_id, user_data)
    return jsonify({"message": "Habit deleted successfully"}), 200

@app.route('/api/user/<user_id>/habits/<habit_id>/complete', methods=['POST'])
def complete_habit_api(user_id, habit_id):
    user_data = get_user(user_id)
    if not user_data or 'habits' not in user_data or habit_id not in user_data['habits']:
        return jsonify({"error": "Habit not found or user data incomplete"}), 404

    habit = user_data['habits'][habit_id]

    # Update habit stats
    habit['streak'] = habit.get('streak', 0) + 1
    # For last_completed_date, ideally use ISO format date string
    from datetime import datetime, timezone
    habit['last_completed_date'] = datetime.now(timezone.utc).isoformat()

    # Update user stats (gamification)
    user_data['experience'] = user_data.get('experience', 0) + 5 # Less XP than tasks, more frequent
    user_data['gold'] = user_data.get('gold', 0) + 2 # Less gold

    user_data['habits'][habit_id] = habit
    update_user(user_id, user_data)
    return jsonify({"message": "Habit marked as complete", "habit": {habit_id: habit}, "user_stats": {"experience": user_data['experience'], "gold": user_data['gold']}}), 200

@app.route('/api/user/<user_id>/habits/<habit_id>/fail', methods=['POST'])
def fail_habit_api(user_id, habit_id):
    user_data = get_user(user_id)
    if not user_data or 'habits' not in user_data or habit_id not in user_data['habits']:
        return jsonify({"error": "Habit not found or user data incomplete"}), 404

    habit = user_data['habits'][habit_id]

    # Update habit stats
    habit['streak'] = 0 # Reset streak on failure

    # Update user stats (gamification)
    user_data['health'] = user_data.get('health', 100) - 5 # Minor health loss for failing a habit
    # Ensure health doesn't go below 0 if that's a rule, or handle "death" state
    user_data['health'] = max(0, user_data['health'])


    user_data['habits'][habit_id] = habit
    update_user(user_id, user_data)

    response_data = {
        "message": "Habit marked as failed/missed",
        "habit": {habit_id: habit},
        "user_stats": {"health": user_data['health']}
    }
    if user_data['health'] == 0:
        response_data["warning"] = "User health has reached 0!"

    return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(debug=True)
