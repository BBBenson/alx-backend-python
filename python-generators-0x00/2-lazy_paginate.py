import mysql.connector
from mysql.connector import Error

def paginate_users(page_size, offset):
    """Fetch users with pagination"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ALX_prodev'
        )
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return rows
    except Error as e:
        print(f"Error paginating users: {e}")
        return []

def lazy_pagination(page_size):
    """Generator that implements lazy loading of paginated data"""
    offset = 0
    
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
