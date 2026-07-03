#!/bin/bash

# Change to the script's own directory (works wherever the repo is checked out).
cd "$(dirname "$0")" || exit 1

# Activate venv
source venv/bin/activate

# Run the bot and log output
python wayfumo_bot.py >> cron_wayfumo.log 2>&1
