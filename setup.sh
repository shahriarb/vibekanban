#!/bin/bash

# Exit on error
set -e

echo "Setting up Kanban Board Application..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip and install setuptools first
echo "Upgrading pip and installing setuptools..."
pip install --upgrade pip
pip install setuptools wheel

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Initialize the database
echo "Initializing database..."
if [ ! -d "migrations" ]; then
    echo "Setting up initial database migration..."
    flask db init
    flask db migrate -m "Initial migration"
else
    echo "Running existing database migrations..."
fi

flask db upgrade

echo "Setup complete! Run './run.sh' to start the application."
