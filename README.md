# telehabit

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