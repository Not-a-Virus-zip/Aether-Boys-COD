import sys
import sqlite3
from pathlib import Path

from src.database.database_tools import get_connection

# This code gets the home directory based on the current file path: "BASE_DIR/scripts/rebuild_database.py"
#        rebuild_database.py      scripts  base directory
#                 vvvv              vvv    vvv
BASE_DIR = Path(__file__).resolve().parent.parent
# This gets the path to the meal planner
DB_PATH = BASE_DIR / 'data' / 'mymealplanner.db'
SCRIPT_PATH = BASE_DIR / 'data'
SQL_FILES = (
    'MMP_Create_Tables.sql',
    'MMP_Insert_MeasureType.sql',
    'MMP_Insert_Test_Data.sql',
)

# Rebuilds and deletes all previous data in the database
def _rebuild_database(): 
    with get_connection() as con:
        try:
            cur = con.cursor()
            for file in SQL_FILES:
                print(f'Reading {file}...')
                with open(SCRIPT_PATH/file) as sql_file:
                    script = sql_file.read()
                cur.executescript(script)
        except sqlite3.Error:
            con.rollback()
            raise
    print('Rollback finished!')

if __name__ == '__main__':
    response = ''
    while response != 'y' and response != 'n':
        response = input('Are you sure you want to rebuild? (All data will be deleted) [Y/n] ') or 'y'
        if response.lower().strip() == 'y':
            _rebuild_database()
        elif response.lower().strip() == 'n':
            print('No changes made.')
        else:
            print('Please enter y or n')
    
            