import sqlite3
import os

class ExecuteQuery:
    """Reusable context manager that takes a query as input and executes it"""
    
    def __init__(self, db_name="example.db", query=None, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params or []
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """Enter the context - open connection and execute query"""
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
                ("Eve", 28),
                ("Frank", 50),
                ("Grace", 22),
                ("Henry", 60)
            ]
            self.cursor.executemany("INSERT INTO users (name, age) VALUES (?, ?)", sample_users)
            self.connection.commit()
            print("Sample data inserted into users table")
        
        # Execute the provided query
        if self.query:
            print(f"Executing query: {self.query}")
            if self.params:
                print(f"With parameters: {self.params}")
                self.cursor.execute(self.query, self.params)
            else:
                self.cursor.execute(self.query)
            self.results = self.cursor.fetchall()
        
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
    
    def get_results(self):
        """Return the query results"""
        return self.results

def main():
    print("=== Reusable Query Context Manager ===\n")
    
    # Use the context manager with a specific query and parameter
    query = "SELECT * FROM users WHERE age > ?"
    parameter = 25
    
    with ExecuteQuery(query=query, params=[parameter]) as executor:
        results = executor.get_results()
        
        print(f"\nResults for users older than {parameter}:")
        print("ID | Name    | Age")
        print("-" * 20)
        for row in results:
            print(f"{row[0]:2} | {row[1]:7} | {row[2]}")
    
    print(f"\nFound {len(results) if results else 0} users older than {parameter}")
    
    # Another example with different query
    print("\n" + "="*50)
    query2 = "SELECT name, age FROM users WHERE age BETWEEN ? AND ?"
    params2 = [30, 50]
    
    with ExecuteQuery(query=query2, params=params2) as executor:
        results2 = executor.get_results()
        
        print(f"\nResults for users aged between {params2[0]} and {params2[1]}:")
        print("Name    | Age")
        print("-" * 15)
        for row in results2:
            print(f"{row[0]:7} | {row[1]}")

if __name__ == "__main__":
    main()
