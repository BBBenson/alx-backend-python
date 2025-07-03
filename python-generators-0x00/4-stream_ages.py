import mysql.connector
from mysql.connector import Error

def stream_user_ages():
    """Generator that yields user ages one by one"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ALX_prodev'
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")
        
        for (age,) in cursor:
            yield age
            
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error streaming user ages: {e}")

def calculate_average_age():
    """Calculate average age using generator without loading entire dataset"""
    total_age = 0
    count = 0
    
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    if count > 0:
        average_age = total_age / count
        print(f"Average age of users: {average_age:.2f}")
        return average_age
    else:
        print("No users found")
        return 0

# Execute the calculation
if __name__ == "__main__":
    calculate_average_age()
