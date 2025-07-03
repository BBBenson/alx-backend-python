import mysql.connector
from mysql.connector import Error


def stream_users_in_batches(batch_size):
    """Generator that fetches rows in batches from the user_data table"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ALX_prodev'
        )

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")

        batch = []
        for row in cursor:
            batch.append(row)
            if len(batch) == batch_size:
                yield batch
                batch = []

        # Yield remaining rows if any
        if batch:
            yield batch

        cursor.close()
        connection.close()
        return

    except Error as e:
        print(f"Error streaming users in batches: {e}")
        return


def batch_processing(batch_size):
    """Processes each batch to filter users over the age of 25"""
    try:
        for batch in stream_users_in_batches(batch_size):
            for user in batch:
                if user['age'] > 25:
                    print(user)
        return
    except Exception as e:
        print(f"Error in batch processing: {e}")
        return
