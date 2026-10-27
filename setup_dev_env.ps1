$ErrorActionPreference = "Stop"
Write-Output "Creating .venv"
python3 -m venv .venv --upgrade-deps --clear
Write-Output "Activating .venv"
.\.venv\Scripts\Activate.ps1
Write-Output "Installing packages"
pip install --require-venv -r requirements.txt
Write-Output "Building test database"
python3 scripts\rebuild_database.py