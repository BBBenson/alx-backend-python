import time
import sqlite3
import functools
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def with_db_connection(func):
    """Decorator that automatically handles opening and closing database connections."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
    return wrapper

def retry_on_failure(retries=3, delay=2):
    """Decorator that retries database operations if they fail due to transient errors."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retries + 1):  # +1 because we want to include the initial attempt
                try:
                    if attempt > 0:
                        logger.info(f"Retry attempt {attempt}/{retries} for {func.__name__}")
                        time.sleep(delay)
                    
                    result = func(*args, **kwargs)
                    
                    if attempt > 0:
                        logger.info(f"Function {func.__name__} succeeded on attempt {attempt + 1}")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                    
                    # Don't retry on the last attempt
                    if attempt == retries:
                        break
            
            # If we get here, all attempts failed
            logger.error(f"All {retries + 1} attempts failed for {func.__name__}")
            raise last_exception
        
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """Fetch users with automatic retry on failure."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

@with_db_connection
@retry_on_failure(retries=2, delay=0.5)
def unreliable_database_operation(conn):
    """Simulate an unreliable database operation that sometimes fails."""
    # Simulate random failures (30% chance of failure)
    if random.random() < 0.3:
        raise sqlite3.OperationalError("Simulated database connection error")
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    result = cursor.fetchone()
    return result[0]

@with_db_connection
@retry_on_failure(retries=2, delay=1)
def always_failing_operation(conn):
    """Simulate an operation that always fails to test retry exhaustion."""
    raise sqlite3.DatabaseError("This operation always fails")

if __name__ == "__main__":
    print("=== Task 3: Retry Database Queries ===")
    
    # Test successful operation with retry decorator
    print("1. Testing successful operation with retry capability:")
    try:
        users = fetch_users_with_retry()
        print(f"Successfully fetched {len(users)} users")
    except Exception as e:
        print(f"Failed to fetch users: {e}")
    
    # Test unreliable operation that might need retries
    print("\n2. Testing unreliable operation (may require retries):")
    try:
        user_count = unreliable_database_operation()
        print(f"Successfully got user count: {user_count}")
    except Exception as e:
        print(f"Failed to get user count after retries: {e}")
    
    # Test operation that always fails to demonstrate retry exhaustion
    print("\n3. Testing operation that always fails (should exhaust retries):")
    try:
        always_failing_operation()
    except Exception as e:
        print(f"Operation failed after all retries: {e}")
