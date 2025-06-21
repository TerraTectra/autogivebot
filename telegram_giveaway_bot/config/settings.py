import os

# Telegram Bot Token (obtain from BotFather)
# Set this as an environment variable for production.
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN_FALLBACK')

# Database connection string (e.g., "sqlite:///giveaway.db")
DATABASE_URL = "sqlite:///data/giveaway.db"

# Logging configuration (optional)
LOG_LEVEL = "INFO"  # Options: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
LOG_FILE = "bot.log"  # Set to None to disable file logging, or provide a file path
