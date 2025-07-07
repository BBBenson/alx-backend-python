import sqlite3
import functools
import logging

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
                if isinstance(arg, str) and ('SELECT' in arg.upper() or 'INSERT' in arg.upper() or 'UPDATE' in arg.upper() or 'DELETE' in arg.upper()):
                    query = arg
                    break
        
        if 'query' in kwargs:
            query = kwargs['query']
        
        if query:
            logger.info(f"Executing SQL Query: {query}")
        else:
            logger.info(f"Executing function: {func.__name__}")
        
        # Execute the original function
        result = func(*args, **kwargs)
        logger.info(f"Query executed successfully. Returned {len(result) if isinstance(result, (list, tuple)) else 1} row(s)")
        
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
