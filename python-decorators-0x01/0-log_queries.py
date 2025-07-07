import sqlite3
import functools
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def log_queries(func):
    """Decorator to log SQL queries executed by any function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract query from arguments
        query = None
        if args:
            for arg in args:
                if isinstance(arg, str) and (
                        'SELECT' in arg.upper() or 'INSERT' in arg.upper() or 'UPDATE' in arg.upper() or 'DELETE' in arg.upper()):
                    query = arg
                    break

        if 'query' in kwargs:
            query = kwargs['query']

        # Log with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if query:
            logger.info(f"[{timestamp}] Executing SQL Query: {query}")
        else:
            logger.info(f"[{timestamp}] Executing function: {func.__name__}")

        # Execute the original function
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        logger.info(
            f"[{timestamp}] Query executed successfully in {execution_time:.3f}s. Returned {len(result) if isinstance(result, (list, tuple)) else 1} row(s)")

        return result

    return wrapper


@log_queries
def fetch_all_users(query):
    """Fetch all users from the database."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    print("=== Task 0: Logging Database Queries ===")

    # Fetch users while logging the query
    users = fetch_all_users(query="SELECT * FROM users")
    print(f"Retrieved {len(users)} users:")
    for user in users:
        print(f"  ID: {user[0]}, Name: {user[1]}, Email: {user[2]}")
