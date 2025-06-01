# telehabit

Telehack is a gamified task and habit tracker integrated with Telegram, featuring a command-line bot interface and a richer Web App interface.

## Features

### Telegram Bot Interface
- `/start`: Initialize or welcome the user.
- `/status`: Display current user statistics (Health, XP, Gold).
- `/webapp`: Provides a link to open the Telegram Web App.
- Basic task/habit interactions (completion/failure) are available, but the Web App offers a more comprehensive experience.

### Telegram Web App
Accessed via the `/webapp` command in the bot, offering a richer user experience:
- **User Stats Display**: Clearly shows current Health, Experience Points (XP), and Gold.
- **Task Management**:
    - Add new tasks with names and descriptions.
    - View all existing tasks.
    - Edit task descriptions.
    - Mark tasks as complete to earn rewards.
    - Mark tasks as failed, which may impact stats.
    - Delete tasks.
- **Habit Management**:
    - Add new habits with names, descriptions, and frequency (e.g., daily, weekly).
    - View all existing habits, including their current streak.
    - Edit habit descriptions and frequencies.
    - Mark habits as "Done Today" to maintain streaks and earn rewards.
    - Mark habits as "Missed", which can break streaks and impact stats.
    - Delete habits.
- **Gamification**:
    - Earn XP and Gold for completing tasks and maintaining habit streaks.
    - Lose Health for failing tasks or missing habits.

## Setup and Running

### Telegram Bot Token

To run the Telegram bot, you need to provide its API token via an environment variable named `TELEGRAM_TOKEN`.

1.  **Get a token:** Talk to the [BotFather](https://t.me/botfather) on Telegram to create a new bot or get the token for an existing one.
2.  **Set the environment variable:**

    **Linux/macOS (bash/zsh):**
    ```bash
    export TELEGRAM_TOKEN="YOUR_ACTUAL_TOKEN_HERE"
    ```

    **Windows (Command Prompt):**
    ```bash
    set TELEGRAM_TOKEN="YOUR_ACTUAL_TOKEN_HERE"
    ```

    **Windows (PowerShell):**
    ```bash
    $env:TELEGRAM_TOKEN="YOUR_ACTUAL_TOKEN_HERE"
    ```

### Running the Bot
Once the token is set, you can run the main bot script:
```bash
python main.py
```
And the Flask app for the web UI (in a separate terminal):
```bash
python app.py
```
Make sure to install dependencies from `requirements.txt` first:
```bash
pip install -r requirements.txt
```

Once both `main.py` (the bot) and `app.py` (the web server) are running, you can access the Web App by sending the `/webapp` command to your bot in Telegram.
