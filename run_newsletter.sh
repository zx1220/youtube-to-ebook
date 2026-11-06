#!/bin/bash
# Runner script for YouTube Newsletter
# This script is called by launchd on a schedule

# Project directory
PROJECT_DIR="/Users/zhangxiang/github/youtube-to-ebook"

# Change to the project directory
cd "$PROJECT_DIR"

# Make sure the log directory exists
mkdir -p "$PROJECT_DIR/logs"

# Wait for network (launchd may start us before morning network is up; 2026-11-06 修 7 点断网)
for i in 1 2 3 4 5 6; do
  if curl -sf --max-time 8 -o /dev/null https://www.youtube.com; then
    break
  fi
  echo "--- network not ready, retry $i/6 at $(date) ---" >> "$PROJECT_DIR/logs/newsletter.log"
  sleep 60
done

# Run the newsletter generator using the project's virtual environment
"$PROJECT_DIR/.venv/bin/python3" "$PROJECT_DIR/main.py" >> "$PROJECT_DIR/logs/newsletter.log" 2>&1

# Add a timestamp to the log
echo "--- Completed at $(date) ---" >> "$PROJECT_DIR/logs/newsletter.log"
