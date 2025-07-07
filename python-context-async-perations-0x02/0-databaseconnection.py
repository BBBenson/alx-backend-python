import sqlite3
import os

class DatabaseConnection:
    """Custom class-based context manager for database connections"""
    
    def __init__(self, db_name="example.db"):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        """Enter the context - open database connection"""
        print(f"Opening database connection to {self.db_name}")
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        
        # Create users table if it doesn't exist and add sample data
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        ''')
        
        # Insert sample data if table is empty
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            sample_users = [
                ("Alice", 25),
                ("Bob", 30),
                ("Charlie", 35),
                ("Diana", 45),
                ("Eve", 28)
            ]
            self.cursor.executemany("INSERT INTO users (name, age) VALUES (?, ?)", sample_users)
            self.connection.commit()
            print("Sample data inserted into users table")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context - close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed")
        
        # Handle exceptions
        if exc_type is not None:
            print(f"An exception occurred: {exc_type.__name__}: {exc_val}")
        return False  # Don't suppress exceptions
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

# Using the context manager
def main():
    print("=== Custom Database Connection Context Manager ===\n")
    
    # Use the context manager with the 'with' statement
    with DatabaseConnection() as db:
        print("Executing query: SELECT * FROM users")
        results = db.execute_query("SELECT * FROM users")
        
        print("\nQuery Results:")
        print("ID | Name    | Age")
        print("-" * 20)
        for row in results:
            print(f"{row[0]:2} | {row[1]:7} | {row[2]}")
    
    print("\nContext manager demonstration completed!")

if __name__ == "__main__":
    main()
