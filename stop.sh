#!/bin/bash

PORT=8000
PID_FILE="server.pid"

echo "Stopping AI Interview Assistant on port $PORT..."

# 1. Try to stop using PID file
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "Process $PID stopped via PID file."
    else
        echo "Process $PID from PID file is not running."
    fi
    rm "$PID_FILE"
else
    echo "No PID file found."
fi

# 2. Try to stop by checking the port (more robust)
LSOF_PID=$(lsof -t -i:$PORT)
if [ ! -z "$LSOF_PID" ]; then
    echo "Found process $LSOF_PID running on port $PORT. Killing it..."
    kill -9 $LSOF_PID
    echo "Server on port $PORT stopped."
else
    echo "No process found running on port $PORT."
fi
