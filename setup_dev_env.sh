#!/bin/bash
echo "Creating .venv"
python3 -m venv .venv --upgrade-deps
echo "Activating .venv"
source .venv/bin/activate
echo "Installing packages from requirements.txt"
pip install --require-venv -r requirements.txt