#!/bin/bash

# Change to project directory
cd /home/billybs/projects/wayfumo_bot

# Activate venv
source venv/bin/activate

# Run the bot and log output
python wayfumo_bot.py >> cron_wayfumo.log 2>&1
