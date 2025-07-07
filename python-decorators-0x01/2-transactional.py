import sqlite3
import functools
import logging

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

def transactional(func):
    """Decorator that manages database transactions by automatically committing or rolling back changes."""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Begin transaction (SQLite uses autocommit by default, so we need to explicitly begin)
            conn.execute('BEGIN')
            logger.info(f"Transaction started for {func.__name__}")
            
            # Execute the function
            result = func(conn, *args, **kwargs)
            
            # Commit the transaction
            conn.commit()
            logger.info(f"Transaction committed successfully for {func.__name__}")
            
            return result
            
        except Exception as e:
            # Rollback the transaction on error
            conn.rollback()
            logger.error(f"Transaction rolled back for {func.__name__}: {str(e)}")
            raise e
    
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """Update a user's email address."""
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    
    if cursor.rowcount == 0:
        raise ValueError(f"No user found with ID {user_id}")
    
    logger.info(f"Updated email for user ID {user_id} to {new_email}")

@with_db_connection
@transactional
def transfer_user_data(conn, from_user_id, to_user_id):
    """Simulate a complex transaction that might fail."""
    cursor = conn.cursor()
    
    # Get source user
    cursor.execute("SELECT * FROM users WHERE id = ?", (from_user_id,))
    source_user = cursor.fetchone()
    if not source_user:
        raise ValueError(f"Source user {from_user_id} not found")
    
    # Update target user with source user's age
    cursor.execute("UPDATE users SET age = ? WHERE id = ?", (source_user[3], to_user_id))
    if cursor.rowcount == 0:
        raise ValueError(f"Target user {to_user_id} not found")
    
    logger.info(f"Transferred age from user {from_user_id} to user {to_user_id}")

if __name__ == "__main__":
    print("=== Task 2: Transaction Management Decorator ===")
    
    try:
        # Update user's email with automatic transaction handling
        print("Updating user email...")
        update_user_email(user_id=1, new_email='alice.updated@email.com')
        print("Email updated successfully!")
        
        # Demonstrate successful transaction
        print("\nPerforming data transfer...")
        transfer_user_data(from_user_id=2, to_user_id=3)
        print("Data transfer completed successfully!")
        
        # Demonstrate failed transaction (rollback)
        print("\nAttempting invalid operation (should fail and rollback)...")
        try:
            update_user_email(user_id=999, new_email='nonexistent@email.com')
        except ValueError as e:
            print(f"Operation failed as expected: {e}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")
