#!/bin/bash
set -e

# Simple configuration
VENV_PATH=".venv"
LOG_DIR="logs"
IP="0.0.0.0"
# Disable default authentication for demo mode
JUPYTER_ARGS="--NotebookApp.token='' --NotebookApp.password=''"

# Parse command line arguments for additional JupyterLab args
while [[ $# -gt 0 ]]; do
  JUPYTER_ARGS="$JUPYTER_ARGS $1"
  shift
done

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/jupyter-$(date +%Y%m%d-%H%M%S).log"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
  echo "Error: Virtual environment not found at $VENV_PATH"
  exit 1
fi

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
  . "$VENV_PATH/bin/activate"
else
  echo "Error: Could not find activate script in $VENV_PATH/bin"
  exit 1
fi

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
  echo "Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
fi

# Build command (using PORT from .env if available, otherwise default to 8888)
PORT=${PORT:-8888}
CMD="python3 -m jupyter lab --no-browser --ip=$IP --port=$PORT"

# Add debug flag if DEBUG is set in .env
if [ "$DEBUG" = "1" ]; then
  CMD="$CMD --debug"
fi

# Add any additional arguments
if [ -n "$JUPYTER_ARGS" ]; then
  CMD="$CMD $JUPYTER_ARGS"
fi

echo "Starting JupyterLab server on $IP:$PORT"
echo "Logs will be written to $LOG_FILE"
echo "Command: $CMD"

# Run the command and log output
$CMD 2>&1 | tee "$LOG_FILE"
