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

type Name = str
type Tag = str


# The foundation for querying the database
class SelectDB:
    select_query = None
    accepted_filters = None
    accepted_sorts = None

    @classmethod
    def run_filtered_query(cls, order = None, filter_column = None, filter_value = None, asc = True) -> list[tuple[Name, Tag]]:
        editable_query = cls.select_query
        if filter_column is not None and filter_value is not None:  # Only activates if a filter column/value is added
            filter_value = (f'%{filter_value}%',)
            editable_query += 'WHERE '
            try:
                editable_query += f'{cls.accepted_filters[filter_column.lower()]} LIKE ? '  # Checks if filter is good
            except(KeyError):
                raise ValueError(f'filter_column:{filter_column!r} is not in {list(cls.accepted_filters.keys())}')
        elif filter_column is None and filter_value is None:
            filter_value = ()
        else:
            raise ValueError(f'Only one filter was given. Please make sure both are present')
        # Start query not filtered
        editable_query += cls._get_order(order, asc)
        with get_connection() as con:
            cur = con.cursor()
            rows = cur.execute(editable_query, filter_value)
        return rows.fetchall()

    @classmethod
    def _get_order(cls, order: str, asc: bool) -> str:
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
