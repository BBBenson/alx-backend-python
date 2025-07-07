import sqlite3
import functools

def with_db_connection(func):
    """Decorator that automatically handles opening and closing database connections."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        try:
            # Call the original function with connection as first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection
            conn.close()
    
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    """Get a user by their ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

@with_db_connection
def get_users_by_age_range(conn, min_age, max_age):
    """Get users within a specific age range."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE age BETWEEN ? AND ?", (min_age, max_age))
    return cursor.fetchall()

if __name__ == "__main__":
    print("=== Task 1: Handle Database Connections with a Decorator ===")
    
    # Fetch user by ID with automatic connection handling
    user = get_user_by_id(user_id=1)
    if user:
        print(f"User found: ID={user[0]}, Name={user[1]}, Email={user[2]}, Age={user[3]}")
    else:
        print("User not found")
    
    # Fetch users by age range
    users_in_range = get_users_by_age_range(min_age=30, max_age=40)
    print(f"\nUsers aged 30-40 ({len(users_in_range)} found):")
    for user in users_in_range:
        print(f"  {user[1]} (Age: {user[3]})")
