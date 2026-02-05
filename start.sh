#!/bin/bash

# Configuration
PORT=8000
APP_FILE="app.py"
PYTHON_CMD="./venv/bin/python3"

echo "Checking for Virtual Environment..."
if [ ! -f "$PYTHON_CMD" ]; then
    echo "ERROR: Virtual environment not found at ./venv. Please create it first."
    exit 1
fi

echo "Starting AI Interview Assistant (FastAPI Server)..."
echo "URL: http://localhost:$PORT"

# Run the application in the background and save the PID
# We use nohup so it keeps running even if the terminal is closed
# Log output to server.log
nohup "$PYTHON_CMD" "$APP_FILE" > server.log 2>&1 &
echo $! > server.pid

echo "Server started with PID $(cat server.pid). Log is being written to server.log"
