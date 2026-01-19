#!/bin/bash
# Helper script to run the tennis booking bot
# This automatically activates the virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH to include project root for imports
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run the bot with all arguments passed through
python -m src.main "$@"

