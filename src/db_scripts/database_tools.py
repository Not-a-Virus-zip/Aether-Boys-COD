# Purpose: Generic methods that all database logic will need
import sqlite3 as sql
from pathlib import Path
# from src.db_scripts.database_logic import TagQuery as tq
# from src.db_scripts.database_logic import MeasureTypeQuery as mtq

# (typing imports)
from typing import ClassVar

# This code gets the home directory based on the current file path: "BASE_DIR/src/db_scripts/database_tools.py"
#          database_tools.py   db_scripts  src  base directory
#                 vvvv              vvv    vvv    vvv
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# This gets the path to the meal planner
DB_PATH = BASE_DIR / 'data' / 'mymealplanner.db'

# Returns a new connection object to the db
def get_connection() -> sql.Connection:
    try:
        con = sql.connect(DB_PATH)
        con.execute('PRAGMA foreign_keys = ON;')  # Makes sure foreign keys are turned on
        return con
    except sql.Error as e:
        print(f'Database connection error: {e}')
        raise

type Name = str
type Tag = str


# The foundation for querying the database
class SelectDB:
    select_query: ClassVar[str]
    accepted_filters: ClassVar[dict[str, str]]
    accepted_sorts: ClassVar[dict[str, str]]
    
    delete_table_name = ClassVar[str]
    delete_id_name = ClassVar[str]

    @classmethod
    def run_select(
            cls,
            order: str | None = None,
            filter_column: str | None = None,
            filter_value: str | None = None,
            asc: bool = True,
            exact: bool = False
    ) -> list[tuple]:
        editable_query = cls.select_query
        if filter_column is not None and filter_value is not None:  # Only activates if a filter column/value is added
            editable_query += 'WHERE '
            try:
                editable_query += f'{cls.accepted_filters[filter_column.lower()]} '  # Checks if filter is good
            except(KeyError):
                raise ValueError(f'filter_column:{filter_column!r} is not in {list(cls.accepted_filters.keys())}')
            # Determines if the user wants an exact or more of a rough match
            if exact:
                editable_query += '= ? '
                filter_tuple = (filter_value,)
            else:
                editable_query += 'LIKE ? '
                filter_tuple = (f'%{filter_value}%',)
        elif filter_column is None and filter_value is None:
            filter_tuple = ()
        else:
            raise ValueError(f'Only one filter was given. Please make sure both are present')
        # Start query not filtered
        editable_query += cls._get_order(order, asc)
        with get_connection() as con:
            cur = con.cursor()
            rows = cur.execute(editable_query, filter_tuple)
        return rows.fetchall()

    @classmethod
    def run_delete(cls, given_id: str):
        try:
            with get_connection() as con:
                cur = con.cursor()
                cur.execute(f'DELETE FROM {cls.delete_table_name} WHERE {cls.delete_id_name} = ?', (given_id))
        # TODO: This type of error will happen often. We need a error message showing what constraints are keeping it from being deleted
        except sql.IntegrityError as e:
            raise QueryDeleteError


    @classmethod
    def _get_order(cls, order: str | None, asc: bool) -> str:
        if order is None:
            order = list(cls.accepted_sorts.keys())[0]
        try:
            order_sql = f'ORDER BY {cls.accepted_sorts[order.lower()]} '
        except(KeyError):
            raise ValueError(f'order:{order!r} is not in {list(cls.accepted_sorts.keys())}')

        if asc:
            order_sql += 'ASC '
        else:
            order_sql += 'DESC '
        return order_sql


# Errors for logic
class MealIngredientQuery(SelectDB):
    pass

# Errors for data validation
class DatabaseErrors(Exception): 
    """Base class for this library"""

class QueryInvalidFK(DatabaseErrors):
    def __init__(self, value_type, value):
        self.value_type = value_type
        self.value = value

    def __str__(self):
        return f'Invalid {self.value_type} given!'

class QueryUpdateError(DatabaseErrors):
    def __init__(self, identifier):
        self.identifier = identifier

    def __str__(self):
        return f'Unable to update: {self.identifier!r}'

class QueryDeleteError(DatabaseErrors):
    def __str__(self):
        return f'Unable to delete selected item. Probably constrained to another item'