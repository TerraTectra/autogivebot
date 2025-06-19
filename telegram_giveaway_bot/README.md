# Telegram Giveaway Bot

This is a Telegram bot for managing giveaways.

## Features

- Create and manage giveaways.
- Allow users to participate in giveaways.
- Automatically select winners.
- Announce winners.

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/telegram-giveaway-bot.git
   cd telegram-giveaway-bot
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot:**
   - Rename `config/settings.py.example` to `config/settings.py`.
   - Edit `config/settings.py` and add your `TELEGRAM_BOT_TOKEN` and other settings.

5. **Initialize the database (if using Alembic for migrations):**
   ```bash
   alembic upgrade head
   ```

## Running the Bot

```bash
python bot/bot.py
```

## Technologies Used

- Python
- python-telegram-bot
- SQLAlchemy
- Alembic (for database migrations)
```
