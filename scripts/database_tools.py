import sqlite3 as sql
from pathlib import Path

# This code gets the home directory
BASE_DIR = Path(__file__).resolve().parent.parent
# This gets the path to the meal planner
DB_PATH = BASE_DIR / 'data' / 'mymealplanner.db'

# Returns a new connection object to the db
def get_connection():
    try:
        con = sql.connect(DB_PATH)
        return con
    except sql.Error as e:
        print(f'Database connection error: {e}')
        raise
