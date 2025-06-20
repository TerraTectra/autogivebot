# Telegram Giveaway Bot

This is a Telegram bot designed for creating and managing giveaways, allowing users to easily participate and automatically selecting winners.

## Features

- **Create Giveaways:** Easily set up new giveaways with a title, description, and end date/time.
- **Button Participation:** Users can participate in giveaways by simply clicking a button on the giveaway message.
- **Automatic Winner Selection:** The bot automatically draws a winner randomly from the participants once the giveaway end time is reached.
- **Winner Announcements:** Winners are publicly announced in the chat where the giveaway was created.
- **Database Persistence:** Uses SQLAlchemy to store user, giveaway, and participant data in a SQLite database.
- **Database Migrations:** Employs Alembic for managing database schema changes.
- **Scheduled Tasks:** Uses APScheduler for timely checking and concluding giveaways.
- **Easy Setup Scripts:** Comes with `.bat` (Windows) and `.sh` (Linux/macOS) scripts to simplify setup and execution.

## Setup

There are two ways to set up the bot: using the provided setup scripts (recommended) or manually.

### Using Setup Scripts (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/telegram-giveaway-bot.git # Replace with actual repo URL if known
    cd telegram_giveaway_bot
    ```

2.  **Run the setup script for your operating system:**
    *   **Windows:** Open Command Prompt or PowerShell, navigate to the `telegram_giveaway_bot` directory and run:
        ```batch
        setup_and_run.bat
        ```
        Then choose option `1. Full Setup`. This will guide you through Python checks, virtual environment creation, dependency installation, and token configuration reminders.
    *   **Linux/macOS:** Open your terminal, navigate to the `telegram_giveaway_bot` directory and run:
        ```bash
        chmod +x setup_and_run.sh
        ./setup_and_run.sh
        ```
        Then choose option `1. Full Setup`. This will perform similar setup steps.

3.  **Configure the Bot Token:**
    The setup script will remind you to set the `TELEGRAM_BOT_TOKEN`. This is a **crucial step**.
    - Obtain your bot token from BotFather on Telegram.
    - Set it as an environment variable named `TELEGRAM_BOT_TOKEN`.
        - **Windows (in Command Prompt for current session):** `set TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE`
        - **Windows (PowerShell for current session):** `$env:TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"`
        - **Linux/macOS (for current session):** `export TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"`
    - For permanent setup, add it to your system's environment variables or your shell's profile file (e.g., `.bashrc`, `.zshrc`).
    The bot will not start if the token is not configured. You can see how the token is loaded in `config/settings.py`.

4.  **Initialize/Upgrade the Database:**
    The setup scripts (Option 1) should guide you if database setup is needed. If you need to do this manually after setup, or if you are updating:
    - Ensure your virtual environment is active if you set it up manually.
    - Run the following command from the `telegram_giveaway_bot` directory:
        ```bash
        alembic upgrade head
        ```
    This will create or update the database schema in the `data/giveaway.db` SQLite file. The `data/` directory will be created if it doesn't exist.

### Manual Setup

1.  **Clone the repository (see above).**

2.  **Ensure Python is installed:** Python 3.8 or higher is recommended.

3.  **Create a virtual environment and activate it:**
    ```bash
    python3 -m venv venv  # Or just "python" on some systems
    # Windows:
    # venv\Scripts\activate.bat
    # Linux/macOS:
    # source venv/bin/activate
    ```

4.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure the Bot Token (see step 3 in "Using Setup Scripts").**

6.  **Initialize/Upgrade the Database (see step 4 in "Using Setup Scripts").**

## Running the Bot

-   **Using Setup Scripts:**
    -   Run `setup_and_run.bat` (Windows) or `./setup_and_run.sh` (Linux/macOS).
    -   Choose the "Run Bot" option from the menu.
-   **Manually (after manual setup):**
    1.  Activate the virtual environment (`source venv/bin/activate` or `venv\Scripts\activate.bat`).
    2.  Ensure `TELEGRAM_BOT_TOKEN` environment variable is set.
    3.  Run the bot from the `telegram_giveaway_bot` directory:
        ```bash
        python bot/bot.py
        ```

Press `Ctrl+C` to stop the bot.

## Available Commands

-   `/start`
    -   Welcomes the user and registers/updates their information in the bot's database.
-   `/help`
    -   Shows a help message with available commands and usage instructions.
-   `/create_giveaway <Title> | <Description> | <YYYY-MM-DD HH:MM>`
    -   Creates a new giveaway.
    -   `<Title>`: The title of the giveaway (e.g., "Steam Key for Awesome Game").
    -   `<Description>`: A short description of the prize.
    -   `<YYYY-MM-DD HH:MM>`: The end date and time for the giveaway in UTC. For example, `2024-12-31 20:00`.
    -   **Example:** `/create_giveaway My Prize | A cool item | 2024-07-01 15:30`
-   **Participating:**
    -   When a giveaway is created, a message is posted with a "Participate!" button. Click this button to enter the giveaway. You'll receive a confirmation or a message if you're already participating or if the giveaway has ended.

## Technologies Used

-   Python 3
-   [python-telegram-bot](https://python-telegram-bot.org/) - For interacting with the Telegram Bot API.
-   [SQLAlchemy](https://www.sqlalchemy.org/) - For database interaction (ORM).
-   [Alembic](https://alembic.sqlalchemy.org/) - For database schema migrations.
-   [APScheduler](https://apscheduler.readthedocs.io/) - For scheduling tasks (e.g., checking for ended giveaways).
-   SQLite - As the default database.

---
*Note: Replace `your-username/telegram-giveaway-bot.git` with the actual repository URL when known.*
