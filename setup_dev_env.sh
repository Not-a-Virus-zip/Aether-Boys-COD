#!/bin/bash
set -e

echo "Creating .venv"
python3 -m venv .venv --upgrade-deps

echo "Activating .venv"
source .venv/bin/activate

echo "Installing packages from requirements.txt"
pip install --require-venv -r requirements.txt

echo "Building test database"
python3 scripts/rebuild_database.py