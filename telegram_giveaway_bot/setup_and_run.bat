@echo off
setlocal

REM === Configuration ===
set VENV_DIR=venv
set PYTHON_EXE=python
set REQUIREMENTS_FILE=requirements.txt
set BOT_SCRIPT=bot/bot.py
REM === End Configuration ===

REM Function to check if Python is installed
:check_python
echo Checking for Python...
%PYTHON_EXE% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found or not added to PATH.
    echo Please install Python (version 3.8 or higher recommended) and ensure it's added to your PATH.
    echo You can download Python from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Python found.

REM Function to create virtual environment
:create_venv
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Creating virtual environment in %VENV_DIR%...
    %PYTHON_EXE% -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment. Please check your Python installation.
        pause
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

REM Function to install requirements
:install_requirements
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
echo Installing dependencies from %REQUIREMENTS_FILE%...
pip install -r %REQUIREMENTS_FILE%
if %errorlevel% neq 0 (
    echo Failed to install dependencies. Please check your internet connection and %REQUIREMENTS_FILE%.
    pause
    exit /b 1
)
echo Dependencies installed successfully.

REM Function to remind about TELEGRAM_BOT_TOKEN
:remind_token
echo.
echo === IMPORTANT: Configure Bot Token ===
echo You need to set the TELEGRAM_BOT_TOKEN environment variable.
echo 1. Get your token from BotFather on Telegram.
echo 2. Set the environment variable:
echo    - You can set it temporarily for this session by typing:
echo      set TELEGRAM_BOT_TOKEN=YOUR_ACTUAL_TOKEN_HERE
echo      (replace YOUR_ACTUAL_TOKEN_HERE with your real token)
echo    - Or set it permanently in your system's environment variables.
echo.
echo The bot will not run correctly without this token.
echo The config file at config/settings.py shows where the token is loaded.
echo.
choice /C YN /M "Do you want to open config/settings.py to see the token configuration example?"
if %errorlevel% == 1 start "" "config\settings.py"
echo.


REM Function to run the bot
:run_bot
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
echo Starting the Telegram bot...
echo Press Ctrl+C to stop the bot.
%PYTHON_EXE% %BOT_SCRIPT%
if %errorlevel% neq 0 (
    echo The bot exited with an error.
)
echo Bot has been stopped.
pause

REM --- Main Menu ---
:menu
cls
echo Telegram Giveaway Bot Setup and Runner
echo ------------------------------------
echo 1. Full Setup (Python check, Venv, Install Dependencies, Token Reminder)
echo 2. Install/Update Dependencies (Venv activation + pip install)
echo 3. Configure Bot Token (Reminder)
echo 4. Run Bot
echo 5. Exit
echo ------------------------------------

choice /C 12345 /N /M "Enter your choice: "

if errorlevel 5 goto :eof
if errorlevel 4 goto :run_bot_menu_wrapper
if errorlevel 3 goto :remind_token_menu_wrapper
if errorlevel 2 goto :install_req_menu_wrapper
if errorlevel 1 goto :full_setup_menu_wrapper

goto :menu

:full_setup_menu_wrapper
call :check_python || goto :menu
call :create_venv || goto :menu
call :install_requirements || goto :menu
call :remind_token || goto :menu
echo Full setup steps completed.
pause
goto :menu

:install_req_menu_wrapper
call :create_venv || goto :menu
call :install_requirements || goto :menu
echo Dependencies check/update completed.
pause
goto :menu

:remind_token_menu_wrapper
call :remind_token || goto :menu
pause
goto :menu

:run_bot_menu_wrapper
call :remind_token_if_not_set_for_run
call :run_bot || goto :menu
goto :menu

REM Helper for run_bot_menu_wrapper to ensure token reminder if not done via full setup
:remind_token_if_not_set_for_run
REM This is a simple check. A more robust way would be to check env var directly,
REM but that's more complex in pure batch. This relies on user having seen it.
echo Before running, make sure your TELEGRAM_BOT_TOKEN is set.
choice /C YN /M "Have you set your TELEGRAM_BOT_TOKEN environment variable for this session or permanently? (Y/N)"
if /I "%ERRORLEVEL%" == "2" (
    echo Token not set. Please use option 1 (Full Setup) or 3 (Configure Bot Token) first.
    pause
    goto :menu
)
goto :eof


endlocal
