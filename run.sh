#!/bin/bash

# Exit on error
set -e

# we might run this outside the project, so the first thins we should do is to cd to the project root
cd "$(dirname "$0")"

echo "Starting Kanban Board Application..."

# Activate virtual environment
source .venv/bin/activate

# Run the application
python run.py
