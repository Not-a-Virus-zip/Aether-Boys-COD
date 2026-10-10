Write-Output "Creating .venv"
python3 -m venv .venv
Write-Output "Activating .venv"
.\.venv\Scripts\Activate.ps1
Write-Output "Installing packages"
pip install --require-venv -r requirements.txt