echo "Creating .venv"
py -m venv .venv --upgrade-deps --clear
echo "Installing packages from requirements.txt"
.\.venv\Scripts\pip install --require-venv -r requirements.txt
echo "Building test database"
.\.venv\Scripts\python scripts\rebuild_database.py
echo "Activating .venv"
.\.venv\Scripts\activate.bat