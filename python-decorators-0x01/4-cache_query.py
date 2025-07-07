import time
import sqlite3
import functools
import hashlib
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global cache dictionary
query_cache = {}

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

def cache_query(func):
    """Decorator that caches query results based on the SQL query string."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from function name, args, and kwargs
        cache_key_data = {
            'function': func.__name__,
            'args': args[1:],  # Skip the connection object
            'kwargs': kwargs
        }
        
        # Create a hash of the cache key for consistent lookup
        cache_key = hashlib.md5(
            json.dumps(cache_key_data, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        # Check if result is in cache
        if cache_key in query_cache:
            logger.info(f"Cache HIT for {func.__name__} - returning cached result")
            return query_cache[cache_key]['result']
        
        # If not in cache, execute the function
        logger.info(f"Cache MISS for {func.__name__} - executing query")
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Store result in cache with metadata
        query_cache[cache_key] = {
            'result': result,
            'timestamp': time.time(),
            'execution_time': execution_time,
            'function': func.__name__
        }
        
        logger.info(f"Result cached for {func.__name__} (execution time: {execution_time:.3f}s)")
        return result
    
    return wrapper

def clear_cache():
    """Clear the query cache."""
    global query_cache
    cache_size = len(query_cache)
    query_cache.clear()
    logger.info(f"Cache cleared - removed {cache_size} entries")

def get_cache_stats():
    """Get cache statistics."""
    return {
        'total_entries': len(query_cache),
        'entries': [
            {
                'function': entry['function'],
                'timestamp': entry['timestamp'],
                'execution_time': entry['execution_time']
            }
            for entry in query_cache.values()
        ]
    }

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """Fetch users with caching capability."""
    # Simulate some processing time
    time.sleep(0.1)
    
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

@with_db_connection
@cache_query
def get_user_count_by_age_range(conn, min_age, max_age):
    """Get count of users in age range with caching."""
    time.sleep(0.05)  # Simulate processing time
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE age BETWEEN ? AND ?", (min_age, max_age))
    return cursor.fetchone()[0]

@with_db_connection
@cache_query
def get_users_by_email_domain(conn, domain):
    """Get users by email domain with caching."""
    time.sleep(0.08)  # Simulate processing time
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email LIKE ?", (f'%{domain}%',))
    return cursor.fetchall()

if __name__ == "__main__":
    print("=== Task 4: Cache Database Queries ===")
    
    # Test basic caching
    print("1. Testing basic query caching:")
    
    # First call will cache the result
    print("First call (should cache):")
    start_time = time.time()
    users = fetch_users_with_cache(query="SELECT * FROM users")
    first_call_time = time.time() - start_time
    print(f"Retrieved {len(users)} users in {first_call_time:.3f} seconds")
    
    # Second call will use the cached result
    print("\nSecond call (should use cache):")
    start_time = time.time()
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    second_call_time = time.time() - start_time
    print(f"Retrieved {len(users_again)} users in {second_call_time:.3f} seconds")
    
    print(f"Speed improvement: {(first_call_time / second_call_time):.1f}x faster")
    
    # Test different queries
    print("\n2. Testing different cached queries:")
    
    # Age range query
    count1 = get_user_count_by_age_range(min_age=25, max_age=35)
    print(f"Users aged 25-35: {count1}")
    
    # Same query again (should be cached)
    count2 = get_user_count_by_age_range(min_age=25, max_age=35)
    print(f"Users aged 25-35 (cached): {count2}")
    
    # Different age range (new cache entry)
    count3 = get_user_count_by_age_range(min_age=30, max_age=45)
    print(f"Users aged 30-45: {count3}")
    
    # Email domain query
    domain_users = get_users_by_email_domain(domain="email.com")
    print(f"Users with 'email.com' domain: {len(domain_users)}")
    
    # Same domain query (should be cached)
    domain_users_cached = get_users_by_email_domain(domain="email.com")
    print(f"Users with 'email.com' domain (cached): {len(domain_users_cached)}")
    
    # Display cache statistics
    print("\n3. Cache Statistics:")
    stats = get_cache_stats()
    print(f"Total cache entries: {stats['total_entries']}")
    for i, entry in enumerate(stats['entries'], 1):
        print(f"  {i}. {entry['function']} - executed in {entry['execution_time']:.3f}s")
    
    # Clear cache demonstration
    print("\n4. Cache Management:")
    clear_cache()
    
    # Verify cache is cleared
    print("Testing after cache clear (should execute query again):")
    users_after_clear = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Retrieved {len(users_after_clear)} users after cache clear")
