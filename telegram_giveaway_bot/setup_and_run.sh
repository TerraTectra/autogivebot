#!/bin/bash

# === Configuration ===
VENV_DIR="venv"
PYTHON_EXE="python3" # Use python3 for Linux/macOS
REQUIREMENTS_FILE="requirements.txt"
BOT_SCRIPT="bot/bot.py"
# === End Configuration ===

# Function to check if Python is installed
check_python() {
    echo "Checking for Python..."
    if ! command -v $PYTHON_EXE &> /dev/null
    then
        echo "Python ($PYTHON_EXE) not found."
        echo "Please install Python (version 3.8 or higher recommended)."
        echo "You can download Python from https://www.python.org/downloads/"
        read -p "Press enter to exit."
        exit 1
    fi
    echo "Python found."
}

# Function to create virtual environment
create_venv() {
    if [ ! -d "$VENV_DIR/bin/activate" ]; then
        echo "Creating virtual environment in $VENV_DIR..."
        $PYTHON_EXE -m venv $VENV_DIR
        if [ $? -ne 0 ]; then
            echo "Failed to create virtual environment. Please check your Python installation."
            read -p "Press enter to exit."
            exit 1
        fi
        echo "Virtual environment created."
    else
        echo "Virtual environment already exists."
    fi
}

# Function to install requirements
install_requirements() {
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install -r $REQUIREMENTS_FILE
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies. Please check your internet connection and $REQUIREMENTS_FILE."
        deactivate
        read -p "Press enter to exit."
        exit 1
    fi
    echo "Dependencies installed successfully."
    deactivate
}

# Function to remind about TELEGRAM_BOT_TOKEN
remind_token() {
    echo ""
    echo "=== IMPORTANT: Configure Bot Token ==="
    echo "You need to set the TELEGRAM_BOT_TOKEN environment variable."
    echo "1. Get your token from BotFather on Telegram."
    echo "2. Set the environment variable:"
    echo "   - For the current session: export TELEGRAM_BOT_TOKEN=\"YOUR_ACTUAL_TOKEN_HERE\""
    echo "   - Or add it to your shell's profile file (e.g., .bashrc, .zshrc)."
    echo ""
    echo "The bot will not run correctly without this token."
    echo "The config file at config/settings.py shows where the token is loaded."
    echo ""
    read -p "Press enter to continue after reviewing token instructions."
}

# Function to run the bot
run_bot() {
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"

    if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" == "YOUR_TELEGRAM_BOT_TOKEN_FALLBACK" ]; then
        echo "ERROR: TELEGRAM_BOT_TOKEN is not set or is using the fallback value."
        echo "Please set it before running the bot. Use option 3 from the menu or set it manually."
        deactivate
        read -p "Press enter to return to menu."
        return
    fi

    echo "Starting the Telegram bot..."
    echo "Press Ctrl+C to stop the bot."
    $PYTHON_EXE $BOT_SCRIPT
    if [ $? -ne 0 ]; then
        echo "The bot exited with an error."
    fi
    echo "Bot has been stopped."
    deactivate
    read -p "Press enter to continue."
}

# --- Main Menu ---
while true; do
    clear
    echo "Telegram Giveaway Bot Setup and Runner (Linux/macOS)"
    echo "------------------------------------"
    echo "1. Full Setup (Python check, Venv, Install Dependencies, Token Reminder)"
    echo "2. Install/Update Dependencies (Venv activation + pip install)"
    echo "3. Configure Bot Token (Reminder)"
    echo "4. Run Bot"
    echo "5. Exit"
    echo "------------------------------------"
    read -p "Enter your choice: " choice

    case $choice in
        1)
            check_python || continue
            create_venv || continue
            install_requirements || continue
            remind_token || continue
            echo "Full setup steps completed."
            read -p "Press enter to return to menu."
            ;;
        2)
            create_venv || continue
            install_requirements || continue
            echo "Dependencies check/update completed."
            read -p "Press enter to return to menu."
            ;;
        3)
            remind_token || continue
            ;;
        4)
            run_bot || continue
            ;;
        5)
            echo "Exiting."
            break
            ;;
        *)
            echo "Invalid choice. Please try again."
            read -p "Press enter to continue."
            ;;
    esac
done
