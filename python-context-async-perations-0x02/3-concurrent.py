import asyncio
import aiosqlite
import os

async def setup_database():
    """Setup the database with sample data"""
    async with aiosqlite.connect("async_example.db") as db:
        # Create users table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        ''')
        
        # Check if data already exists
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            count = await cursor.fetchone()
            
        if count[0] == 0:
            # Insert sample data
            sample_users = [
                ("Alice", 25),
                ("Bob", 30),
                ("Charlie", 35),
                ("Diana", 45),
                ("Eve", 28),
                ("Frank", 50),
                ("Grace", 22),
                ("Henry", 60),
                ("Ivy", 33),
                ("Jack", 41)
            ]
            await db.executemany("INSERT INTO users (name, age) VALUES (?, ?)", sample_users)
            await db.commit()
            print("Sample data inserted into async database")

async def async_fetch_users():
    """Asynchronously fetch all users"""
    print("Starting to fetch all users...")
    
    async with aiosqlite.connect("async_example.db") as db:
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        async with db.execute("SELECT * FROM users") as cursor:
            users = await cursor.fetchall()
        
        print(f"Fetched {len(users)} users")
        return users

async def async_fetch_older_users():
    """Asynchronously fetch users older than 40"""
    print("Starting to fetch users older than 40...")
    
    async with aiosqlite.connect("async_example.db") as db:
        # Simulate some processing time
        await asyncio.sleep(0.15)
        
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            older_users = await cursor.fetchall()
        
        print(f"Fetched {len(older_users)} users older than 40")
        return older_users

async def fetch_concurrently():
    """Execute both queries concurrently using asyncio.gather"""
    print("=== Concurrent Asynchronous Database Queries ===\n")
    
    # Setup database first
    await setup_database()
    
    print("Executing queries concurrently...\n")
    
    # Record start time
    start_time = asyncio.get_event_loop().time()
    
    # Use asyncio.gather to run both queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    # Record end time
    end_time = asyncio.get_event_loop().time()
    execution_time = end_time - start_time
    
    print(f"\nBoth queries completed in {execution_time:.3f} seconds")
    
    # Display results
    print("\n" + "="*50)
    print("ALL USERS:")
    print("ID | Name    | Age")
    print("-" * 20)
    for user in all_users:
        print(f"{user[0]:2} | {user[1]:7} | {user[2]}")
    
    print("\n" + "="*50)
    print("USERS OLDER THAN 40:")
    print("ID | Name    | Age")
    print("-" * 20)
    for user in older_users:
        print(f"{user[0]:2} | {user[1]:7} | {user[2]}")
    
    return all_users, older_users

async def demonstrate_sequential_vs_concurrent():
    """Demonstrate the difference between sequential and concurrent execution"""
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON: Sequential vs Concurrent")
    print("="*60)
    
    # Sequential execution
    print("\n1. Sequential Execution:")
    start_time = asyncio.get_event_loop().time()
    
    users1 = await async_fetch_users()
    users2 = await async_fetch_older_users()
    
    sequential_time = asyncio.get_event_loop().time() - start_time
    print(f"Sequential execution time: {sequential_time:.3f} seconds")
    
    # Concurrent execution
    print("\n2. Concurrent Execution:")
    start_time = asyncio.get_event_loop().time()
    
    users1, users2 = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    concurrent_time = asyncio.get_event_loop().time() - start_time
    print(f"Concurrent execution time: {concurrent_time:.3f} seconds")
    
    # Calculate improvement
    improvement = ((sequential_time - concurrent_time) / sequential_time) * 100
    print(f"\nPerformance improvement: {improvement:.1f}%")

def main():
    """Main function to run the concurrent fetch"""
    # Run the concurrent fetch
    asyncio.run(fetch_concurrently())
    
    # Demonstrate performance difference
    asyncio.run(demonstrate_sequential_vs_concurrent())

if __name__ == "__main__":
    main()
