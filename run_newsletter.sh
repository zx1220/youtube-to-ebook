#!/bin/bash
# Runner script for YouTube Newsletter
# This script is called by launchd on a schedule

# Project directory
PROJECT_DIR="/Users/zhangxiang/github/youtube-to-ebook"

# Change to the project directory
cd "$PROJECT_DIR"

# Make sure the log directory exists
mkdir -p "$PROJECT_DIR/logs"

# Run the newsletter generator using the project's virtual environment
"$PROJECT_DIR/.venv/bin/python3" "$PROJECT_DIR/main.py" >> "$PROJECT_DIR/logs/newsletter.log" 2>&1

# Add a timestamp to the log
echo "--- Completed at $(date) ---" >> "$PROJECT_DIR/logs/newsletter.log"
