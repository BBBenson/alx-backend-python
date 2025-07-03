import mysql.connector


def streamusersinbatches(batchsize):
    """Generator that fetches rows in batches from the user_data table"""
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='ALX_prodev'
    )

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")

    batch = []
    for row in cursor:  # loop 1
        batch.append(row)
        if len(batch) == batchsize:
            yield batch
            batch = []

    if batch:
        yield batch

    cursor.close()
    connection.close()


def batch_processing(batchsize):
    """Processes each batch to filter users over the age of 25"""
    for batch in streamusersinbatches(batchsize):  # loop 2
        for user in batch:  # loop 3
            if user['age'] > 25:
                print(user)
